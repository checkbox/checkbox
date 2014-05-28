/*
 * This file is part of Checkbox
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Andrew Haigh <andrew.haigh@cellsoftware.co.uk>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "gui-engine.h"
#include <QtDBus/QtDBus>
#include <QDebug>
#include <stdexcept>

#include "PBTreeNode.h"

// Forward declarations
void decodeDBusArgType(const QDBusArgument &arg);       // temporary
void decodeDBusMessageType(const QDBusMessage &msg);    // temporary

QDBusArgument &operator<<(QDBusArgument &arg, const EstimatedDuration &ms)
{
    arg.beginStructure();
    arg << ms.automated_duration << ms.manual_duration;
    arg.endStructure();
    return arg;
}

const QDBusArgument &operator>>(const QDBusArgument &arg, EstimatedDuration &ms)
{
    arg.beginStructure();
    arg >> ms.automated_duration >> ms.manual_duration;
    arg.endStructure();
    return arg;
}

void GuiEnginePlugin::registerTypes(const char *uri)
{
    // register our classes
    qmlRegisterType<GuiEngine>(uri,1,0,"GuiEngine");
}

GuiEngine::GuiEngine( QObject*parent ) :
    QObject(parent),
    enginestate(UNINITIALISED),
    pb_objects(NULL),
    valid_pb_objects(false),
    job_tree(NULL),
    m_current_job_index(-1),    // -1 ensures correct NextRunJobIndex from clean
    m_running(true),
    m_waiting_result(false),
    m_running_manual_job(false),
    m_submitted(false),
    m_local_jobs_done(false),   // for QtTest
    m_jobs_done(false),         // for QtTest
    m_testing_manual_job(false) // for QtTest

{
    qDebug("GuiEngine::GuiEngine");

    // Nothing to do here

    qDebug("GuiEngine::GuiEngine - Done");
}

bool GuiEngine::Initialise(void)
{
    qDebug("GuiEngine::Initialise");
    // Only do this once
    if (enginestate==UNINITIALISED) {
        qDebug("GuiEngine - Initialising");
        // Connect to Dbus Session Bus
        if (!QDBusConnection::sessionBus().isConnected()) {
            qDebug("Cannot connect to the D-Bus session bus.\n");
            return false;
        }
        // Register our custom types for unpacking the object tree
        qDBusRegisterMetaType<om_smalldict>();
        qDBusRegisterMetaType<om_innerdict>();
        qDBusRegisterMetaType<om_outerdict>();
        // We need to pack ObjectPaths into an array for CreateSession()
        qDBusRegisterMetaType<opath_array_t>();
        // Register our Job State Map metatype
        qDBusRegisterMetaType<jsm_t>();
        // Register types needed to unpack the io log
        //qDBusRegisterMetaType<io_log_inner_t>();
        //qDBusRegisterMetaType<io_log_outer_t>();
        // Register our GetEstimatedDuration signature metatype
        qDBusRegisterMetaType<EstimatedDuration>();
        // Obtain the initial tree of Plainbox objects, starting at the root "/"
        RefreshPBObjects();
        // Connect our change receivers
        QDBusConnection bus = QDBusConnection ::sessionBus();
        enginestate = READY;
    }
    qDebug("GuiEngine::Initialise() - Done");
    return true;
}

bool GuiEngine::Shutdown(void)
{
    qDebug("GuiEngine::Shutdown()");
    // Were we initialised?
    if (enginestate==UNINITIALISED) {
        qDebug("Plainbox GUI Engine not initialised");
        return false;
    }
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug("Cant get Plainbox Service interface");
        return false;
    }
    QDBusMessage reply = iface.call("Exit");
    if (reply.type() != QDBusMessage::ReplyMessage) {
        qDebug() << "Failed to exit Plainbox" << reply.errorMessage();
        return false;
    }
    enginestate=UNINITIALISED;
    qDebug("GuiEngine::Shutdown() - Done");
    return true;
}

// DBus-QT Demarshalling helper functions
const QDBusArgument &operator>>(const QDBusArgument &argument, \
                                jsm_t &jsm)
{
    argument.beginMap();
    jsm.clear();
    while(!argument.atEnd())
    {
        argument.beginMapEntry();
        QString job_name;
        QDBusObjectPath opath;
        argument >> job_name >> opath;
        jsm.insert(job_name,opath);
        argument.endMapEntry();
    }
    argument.endMap();
    return argument;
}

const QDBusArgument &operator>>(const QDBusArgument &argument, \
                                om_smalldict &smalldict)
{
    argument.beginMap();
    smalldict.clear();
    while(!argument.atEnd())
    {
        argument.beginMapEntry();
        QString property;
        QDBusVariant variant;
        argument >> property >> variant;
        qDebug() << "string" \
                 << property \
                 << "variant: " \
                 << variant.variant().toString();
        smalldict.insert(property,variant);
        argument.endMapEntry();
    }
    argument.endMap();
    return argument;
}

const QDBusArgument &operator>>(const QDBusArgument &argument, \
                                om_innerdict &innerdict)
{
    argument.beginMap();
    innerdict.clear();
    while(!argument.atEnd())
    {
        argument.beginMapEntry();
        QString interface;
        om_smalldict sd;
        argument >> interface >> sd;
        qDebug() << "Interface: " << interface;
        innerdict.insert(interface,sd);
        argument.endMapEntry();
    }
    argument.endMap();
    return argument;
}

const QDBusArgument &operator>>(const QDBusArgument &argument, \
                                om_outerdict &outerdict)
{
    argument.beginMap();
    outerdict.clear();
    while(!argument.atEnd())
    {
        argument.beginMapEntry();
        QDBusObjectPath object_path;
        om_innerdict innerdict;
        argument >> object_path >> innerdict;
        qDebug() << "ObjectPath" \
                 << object_path.path();
        argument.endMapEntry();
        outerdict.insert(object_path,innerdict);
    }
    argument.endMap();
    return argument;
}

const PBTreeNode* GuiEngine::GetRootJobsNode(const PBTreeNode* node)
{
    // Are we there yet
    if (node->object_path.path() == "/plainbox/job") {
        return node;
    }
    PBTreeNode* jobnode = NULL;
    QList<PBTreeNode*>::const_iterator iter= node->children.begin();
    while(!jobnode && iter !=  node->children.end()) {
        PBTreeNode* child = *iter;
        jobnode = const_cast<PBTreeNode*>(GetRootJobsNode(child));
        if (jobnode) {
            return jobnode;
        }
        iter++;
    }
    return NULL;
}

const PBTreeNode* GuiEngine::GetRootWhiteListNode(const PBTreeNode* node)
{
    // Are we there yet
    if (node->object_path.path() == "/plainbox/whitelist") {
        return node;
    }
    PBTreeNode* whitenode = NULL;
    QList<PBTreeNode*>::const_iterator iter= node->children.begin();
    while(!whitenode && iter !=  node->children.end()) {
        PBTreeNode* child = *iter;
        whitenode = const_cast<PBTreeNode*>(GetRootWhiteListNode(child));
        if (whitenode) {
            return whitenode;
        }
        iter++;
    }
    return NULL;
}

// Work in progress
void GuiEngine::InterfacesAdded(QDBusMessage msg)
{
    qDebug("GuiEngine::InterfacesAdded");
    QList<QVariant> args = msg.arguments();
    QList<QVariant>::iterator p = args.begin();
    p = args.begin();
    QVariant q = *p;
    QDBusObjectPath opath = q.value<QDBusObjectPath>();
    qDebug() << "objectpath: " << opath.path();
    p++;
    q = *p;
    const QDBusArgument qda = q.value<QDBusArgument>();
    om_innerdict my_id;
    qda >> my_id;
    // Need to update our tree of objects.
    // todo
    // Now tell the GUI to update its knowledge of the objects
    //emit updateGuiObjects("TBD1",0,0);
    qDebug("GuiEngine::InterfacesAdded - done");
}

// Work in progress
void GuiEngine::InterfacesRemoved(QDBusMessage msg)
{
    qDebug("GuiEngine::InterfacesRemoved");
    // Need to update our tree of objects.
    qDebug() << "Signature is: " << msg.signature();
    QList<QVariant> args = msg.arguments();
    qDebug("Reply arguments: %d",args.count());
    QList<QVariant>::iterator p = args.begin();
    p = args.begin();
    QVariant q = *p;
    QDBusObjectPath opath = q.value<QDBusObjectPath>();
    qDebug() << "opath: " << opath.path();
    p++;
    q = *p;
    const QDBusArgument qda = q.value<QDBusArgument>();
    // Need to update our tree of objects.
    // todo
    // Now tell the GUI to update its knowledge of the objects
    //emit updateGuiObjects("TBD2",0,0);
    qDebug("GuiEngine::InterfacesRemoved - done");
}

QList<PBTreeNode*> GuiEngine::GetJobNodes(void)
{
    QList<PBTreeNode*> jobnodes;
    PBTreeNode* jobnode = \
            const_cast<PBTreeNode*>(GetRootJobsNode(pb_objects));
    if (!jobnode) {
        return jobnodes;
    }
    QList<PBTreeNode*>::const_iterator iter =jobnode->children.begin();
    while(iter != jobnode->children.end()) {
        PBTreeNode* child = *iter;
         jobnodes.append(child);
         iter++;
    }
    return jobnodes;
}

QList<PBTreeNode*> GuiEngine::GetWhiteListNodes(void)
{
    qDebug("GuiEngine::GetWhiteListNodes()");
    QList<PBTreeNode*> whitelistnodes;
    PBTreeNode* whitelistnode = \
            const_cast<PBTreeNode*>(GetRootWhiteListNode(pb_objects));
    if (!whitelistnode) {
        return whitelistnodes;
    }
    QList<PBTreeNode*>::const_iterator iter = whitelistnode->children.begin();
    while(iter != whitelistnode->children.end()) {
        PBTreeNode* child = *iter;
         whitelistnodes.append(child);
         iter++;
    }
    qDebug("GuiEngine::GetWhiteListNodes() - done");
    return whitelistnodes;
}

QMap<QDBusObjectPath,QString> GuiEngine::GetWhiteListPathsAndNames(void)
{
    QMap<QDBusObjectPath,QString> paths_and_names;
    PBTreeNode* whitenode = \
            const_cast<PBTreeNode*>(GetRootWhiteListNode(pb_objects));
    if (!whitenode) {
        return paths_and_names;
    }
    // loop around all the children
    QList<PBTreeNode*>::const_iterator iter =whitenode->children.begin();
    bool initialised = ! whitelist.empty();
    while(iter != whitenode->children.end()) {
        PBTreeNode* child = *iter;
        QString opath = child->object_path.path();
        // Connect to the introspectable interface
        QDBusInterface introspect_iface(PBBusName, \
                             opath, \
                             "org.freedesktop.DBus.Properties", \
                             QDBusConnection::sessionBus());
        if (introspect_iface.isValid()) {
            QDBusReply<QVariant> reply  = introspect_iface.call("Get", \
                       "com.canonical.certification.PlainBox.WhiteList1", \
                       "name");
            QVariant var(reply);
            QString name(var.toString());
            qDebug() << name;
            // Only show the user whitelists with the desired prefix.
            paths_and_names.insert(child->object_path,name);
            // First time round, fill in our whitelist member
            if (!initialised) {
                whitelist.insert(child->object_path, false);
            }
        }
        iter++;
    }
    return paths_and_names;
}

void GuiEngine::SetWhiteList(const QDBusObjectPath opath, const bool check)
{
    whitelist.remove(opath);
    whitelist.insert(opath,check);
}

void GuiEngine::Pause(void)
{
    // Very simple
    m_running = false;
}

void GuiEngine::Resume(void)
{
    if (m_waiting_result) {
        m_running = true;
        return;
    }
    if (!m_running) {
        // Make a note of it
        m_running = true;
        if (m_run_list.count() != m_current_job_index) {
            // Update the GUI so it knows what job is starting
            emit updateGuiBeginJob(m_run_list.at(m_current_job_index).path(), \
                    m_current_job_index, \
                    JobNameFromObjectPath(m_run_list.at(m_current_job_index)));
            // Now run the next job
            qDebug() << "Running Job (Resume)" << JobNameFromObjectPath(m_run_list.at(m_current_job_index));
            // Preserve progress so far
            EncodeGuiEngineStateAsJSON();
            RunJob(m_session,m_run_list.at(m_current_job_index));
            return;
        }
        // Tell the GUI its all finished
        emit jobsCompleted();
    }
}

/* Prepare the jobs to be run for real. This allows us to compute the number
* of jobs that will actually be run and show it to the user in the Test
* Selection screen as additional implicit jobs
*/

int GuiEngine::PrepareJobs(void)
{
    qDebug("\n\nGuiEngine::PrepareJobs()\n");
    /* First, filter out any jobs we really dont want (i.e. not user-selected)
    *
    * Note: m_final_run_list is in the order of items shown in the gui,
    * so we try to preserve that when we give it to UpdateDesiredJobList()
    * and hopefully it is similar when we get it back from SessionStateRunList()
    */
    QStringList errors = UpdateDesiredJobList(m_session, m_final_run_list);
    if (errors.count() != 0) {
        qDebug("UpdateDesiredJobList generated errors:");
        for (int i=0; i<errors.count(); i++) {
            qDebug() << errors.at(i);
        }
    }
    // Now, the run_list contains the list of jobs I actually need to run \o/
    m_run_list = SessionStateRunList(m_session);
    /* Ensure that the first time through we run everything including implicit jobs
     */
    m_rerun_list = m_run_list;
    // useful to the gui (summary bar in test selection screen)
    return m_run_list.count();
}


int GuiEngine::NextRunJobIndex(int index)
{
    // Now we use the list of re-runs against the run_list to see what we do
    int next = index+1;
    while (next < m_run_list.count() ) {
        /* If the re-run list contains the current job, thats one we will return
         * otherwise we move on to the next.
         */
        if (m_rerun_list.contains(m_run_list.at(next))) {
            return next;
        }
        // Move to the next job
        next++;
    }
    // If we get this far we've really finished
    return next;
}

/* Run all the "real" test jobs. For consistency and clarity, we follow the
 * logic found in dbus-mini-client.py
 */
void GuiEngine::RunJobs(void)
{
    qDebug("GuiEngine::RunJobs");
    // Tell the GUI we are running the jobs
    emit jobsBegin();
    if (m_run_list.count() == 0) {
        // nothing should be left for re-run
        m_rerun_list.clear();
        // Tell the GUI its all finished
        emit jobsCompleted();
        return;
    }
    // Collect any pre-existing results (from previous resume)
    ResumeGetOutcomes();
    // Now connect the signal receivers
    ConnectJobReceivers();
    /* Start tracking which Job we are running, from the beginning
    * -1 to get index 0 because it normally runs at the end of a job,
    * but this will not necessarily be true for re-runs, hence why
    * we need to call NextRunJobIndex() and not just assume 0.
    */
    m_current_job_index = NextRunJobIndex(-1);
    qDebug("computed next job");
    if (m_current_job_index >= m_run_list.count()) {
        // nothing should be left for re-run
        m_rerun_list.clear();
        // Tell the GUI its all finished
        emit jobsCompleted();
        return;
    }
    // ok, this is new. we need to find the first job to really run
    // Tell the GUI so we know we have started running this job
    emit updateGuiBeginJob(m_run_list.at(m_current_job_index).path(), \
            m_current_job_index, \
            JobNameFromObjectPath(m_run_list.at(m_current_job_index)));
    // Now the actual run, job by job
    qDebug() << "Running Job (RunJobs)" << JobNameFromObjectPath(m_run_list.at(m_current_job_index));
    // Preserve progress so far
    EncodeGuiEngineStateAsJSON();
    RunJob(m_session,m_run_list.at(m_current_job_index));
    qDebug("GuiEngine::RunJobs - Done");
}

/* Run all the local "generator" jobs selected by the whitelists, in order
 * to generate the correct "via" information for the _real_ jobs
 * which the user may want to run. This gives us our hierarchy to
 * show in the test selection screen.
 *
 * For clarity of understanding, the flow/style follows dbus-mini-client.py
 */
void GuiEngine::RunLocalJobs(void)
{
    qDebug("GuiEngine::RunLocalJobs");
    /* Whitelist is selected elsewhere in GetWhiteListPathsAndNames()
     * so by this point its contained in the member variable "whitelist"
     * dbus-mini-client.py gets these via GetManagedObjects but it appears to be
     * the same list as exposed by actually trawling DBus itself.
     */
    // We rely upon an already created session; either created when
    // the startup code looked for a previous session file, OR
    // after the startup code resumed a previous session
    // Connect the LocalJobResultAvailable signal receiver
    QDBusConnection bus = QDBusConnection ::sessionBus();
    if (!bus.connect(PBBusName,\
                     NULL,\
                     PBInterfaceName,\
                     "JobResultAvailable",\
                     this,\
                     SLOT(CatchallLocalJobResultAvailableSignalsHandler(QDBusMessage)))) {
        qDebug("Failed to connect slot for JobResultAvailable events");
    }
    // to get only the *jobs* that are designated by the whitelist.
    m_desired_job_list = GenerateDesiredJobList();
    // This is just the list of all provider jobs marked "local"
    m_local_job_list = GetLocalJobs(m_desired_job_list);
    // Now I update the desired job list.
    QStringList errors = UpdateDesiredJobList(m_session, \
                                              m_local_job_list);
    if (errors.count() != 0) {
        qDebug("UpdateDesiredJobList generated errors:");
        for (int i=0; i<errors.count(); i++) {
            qDebug() << errors.at(i);
        }
    }
    // Now, the run_list contains the list of jobs I actually need to run \o/
    m_run_list = SessionStateRunList(m_session);
    // Keep track of which job we are running
    m_current_job_index = 0;
    qDebug() << "Running Local Job " << JobNameFromObjectPath(m_run_list.at(m_current_job_index));
    RunJob(m_session,m_run_list.at(m_current_job_index));
    qDebug("GuiEngine::RunLocalJobs - Done");
}

/* Suspend/resume functionality
 *
 * We need to repopulate:
 * m_run_list;
 * pb_objects;
 * the testitemmodel in the GuiEngine
 * job_tree
 * m_current_job_index
 * m_jsm
 * m_running
 * m_running_manual_job
 * tests
 *
 * We can recover
 * job_list
 * run_list
 *
 *From /plainbox/plainbox/impl/session/state.py:
 * metadata: String flags, String running_job_name, String title
 *
 * So, dev tasks are:
 * Ensure preservation of metadata first and foremost
 * Functions to recover the metadata and other session info
 * Begin the re-construction of the internal state of the gui (several pieces)
*/
 void GuiEngine::GuiResumeSession(const bool re_run)
 {
    qDebug() << "GuiEngine::GuiResumeSession( " << (re_run ? "true":"false") << ") ";
    SessionResume(m_session);
    qDebug() << m_session.path() ;
    /* Get the Session State properties
     *
     * We can recover:
     * desired_job_list
     * job_list
     * run_list
     * job_state_map
     * metadata
     */
    m_desired_job_list = SessionStateDesiredJobList(m_session);
    m_job_list = SessionStateJobList(m_session);
    m_run_list = SessionStateRunList(m_session);
    RefreshPBObjects();
    if (m_desired_job_list.isEmpty()){
        qDebug("Resumed session has no desired_job_list");
        // fixme - a nice gui error message would be welcome here
        return;
    }
    if (m_run_list.isEmpty()) {
        qDebug("Resumed session has no run_list");
        // fixme - a nice gui error message would be welcome here
        return;
    }
    // This should recover m_rerun_list for us
    DecodeGuiEngineStateFromJSON();
    // Having recoved the re-run list, this should be sufficent to skip
    // all the previous tests and to retry failed test.
    if (!re_run && !m_rerun_list.isEmpty()) {
        // Get the interim Job Results, this may take a few seconds as we dont have any shortcuts
        GetJobStateMap();
        GetJobStates();
        GetJobResults();
        // Now, we can set the outcome of this test
        QString empty;
        SetJobOutcome(m_current_job_path, JobResult_OUTCOME_FAIL, empty);
        // Lets skip this one
        m_rerun_list.removeOne(m_current_job_path);
    }
    qDebug() << "GuiEngine::GuiResumeSession() - Done";
 }

 // Called when RunManagerListView is setup
void GuiEngine::ResumeGetOutcomes(void)
{
    qDebug("GuiEngine::GuiResumeGetOutcomes");
    if (m_run_list.isEmpty()) {
        return;     // no results yet
    }
    // Get the interim Job Results, this may take a few seconds as we dont have any shortcuts
    GetJobStateMap();
    GetJobStates();
    GetJobResults();
    // This fixes the results display
    for(int i=0; i<m_run_list.count(); i++) {
        int outcome = GetOutcomeFromJobPath(m_run_list.at(i));
        // only update things which have defined results
        if (outcome != PBTreeNode::PBJobResult_None) {
            // Update the GUI so it knows what the job outcome was
            emit updateGuiEndJob(m_run_list.at(i).path(), \
                             i, \
                             outcome,
                                 "JobNameFromObjectPath(i)");
        }
    }
}

void GuiEngine::ConnectJobReceivers(void)
{
    qDebug("ConnectJobReceivers");
    // Connect the ShowInteractiveUI signal receiver
    QDBusConnection bus = QDBusConnection ::sessionBus();
    if (!bus.connect(PBBusName,\
                  NULL,\
                  PBSessionStateInterface,\
                  "ShowInteractiveUI",\
                  this,\
                  SLOT(CatchallShowInteractiveUISignalsHandler(QDBusMessage)))) {
     qDebug("Failed to connect slot for ShowInteractiveUI events");
     // TODO - Emit error for the gui
     return;
    }
    // Connect the AskForOutcome signal receiver
    if (!bus.connect(PBBusName,\
                  NULL,\
                  PBSessionStateInterface,\
                  "AskForOutcome",\
                  this,\
                  SLOT(CatchallAskForOutcomeSignalsHandler(QDBusMessage)))) {
     qDebug("Failed to connect slot for AskForOutcome events");
     // TODO - Emit error for the gui
     return;
    }
    // Connect the IOLogGenerated signal receiver
    if (!bus.connect(PBBusName,\
                  NULL,\
                  PBInterfaceName,\
                  "IOLogGenerated",\
                  this,\
                  SLOT(CatchallIOLogGeneratedSignalsHandler(QDBusMessage)))) {
     qDebug("Failed to connect slot for IOLogGenerated events");
     // TODO - Emit error for the gui
     return;
    }
    // Connect the JobResultAvailable signal receiver
    if (!bus.connect(PBBusName,\
                     NULL,\
                     PBInterfaceName,\
                     "JobResultAvailable",\
                     this,\
                     SLOT(CatchallJobResultAvailableSignalsHandler(QDBusMessage)))) {
        qDebug("Failed to connect slot for JobResultAvailable events");
        // TODO - Emit error for the gui
        return;
    }
    qDebug("GuiEngine::ConnectJobReceivers - Done");
}
/* Saves:
 * m_rerun_list
 * <TBD>
 */
void GuiEngine::EncodeGuiEngineStateAsJSON(void)
{
//    qDebug("GuiEngine::EncodeGuiEngineStateAsJSON()");

    // Everything will be preserved in here
    QJsonObject guienginestate_js;
    QJsonObject json_m_rerun_list = \
            PBJsonUtils::QDBusObjectPathArrayToJson("m_rerun_list",m_rerun_list);
    guienginestate_js.insert("m_rerun_list_object",json_m_rerun_list);
    QJsonObject json_m_visible_run_list = \
            PBJsonUtils::QDBusObjectPathArrayToJson("m_visible_run_list",m_visible_run_list);
    guienginestate_js.insert("m_visible_run_list_object",json_m_visible_run_list);
    QJsonDocument jsd(guienginestate_js);
    QString current_job_id;
    if (m_run_list.count() > m_current_job_index) {
        current_job_id = m_run_list.at(m_current_job_index).path();
    } else {
        current_job_id = "none";
    }
    // Preserve our properties
    SetSessionStateMetadata(m_session,\
                            m_submitted ? PB_FLAG_SUBMITTED: PB_FLAG_INCOMPLETE,\
                            current_job_id,
                            GUI_ENGINE_NAME_STR,
                            jsd.toJson(),
                            "com.canonical.checkbox-gui");
    // Plainbox should save this session
    SessionPersistentSave(m_session);
//    qDebug("GuiEngine::EncodeGuiEngineStateAsJSON() - Done");
}
void GuiEngine::DecodeGuiEngineStateFromJSON(void)
{
//    qDebug("GuiEngine::DecodeGuiEngineStateFromJSON()");
    QVariantMap metadata = SessionStateMetadata(m_session);
    // Grep the run_list to find metadata job id (should not fail!)
    QVariantMap::const_iterator iter_jobname = metadata.find("running_job_name");
    m_current_job_path = QDBusObjectPath(iter_jobname.value().toString());
    // Grep the run_list to find metadata job id (should not fail!)
    QVariantMap::const_iterator iter = metadata.find("app_blob");
    QString jsd_string = iter.value().toString();
    if (jsd_string.isEmpty()) {
        return;
    }
    // Now convert that app_blob string into JSON
    QByteArray jsdb = jsd_string.toUtf8();
    QJsonDocument jsd = QJsonDocument::fromJson(jsdb);
    // Will contain the recovered state of guiengine
    QJsonObject guienginestate_js;
    guienginestate_js = jsd.object();
    QJsonObject::const_iterator iter_rerun_object = guienginestate_js.find("m_rerun_list_object");
    if (iter_rerun_object == guienginestate_js.end()) {
        qDebug("Cannot find m_rerun_list_object");
    }
    QJsonObject json_m_rerun_list;
    json_m_rerun_list = iter_rerun_object.value().toObject();
    // Now we should find the next key
    QJsonObject::const_iterator iter_rerun = json_m_rerun_list.find("m_rerun_list");
    m_rerun_list = PBJsonUtils::JSONToQDBusObjectPathArray("m_rerun_list",json_m_rerun_list);
    // Visible run list (needed to repopulate the Run Manager View typically)
    QJsonObject::const_iterator iter_visible_object = guienginestate_js.find("m_visible_run_list_object");
    if (iter_visible_object == guienginestate_js.end()) {
        qDebug("Cannot find m_visible_run_list_object");
    }
    QJsonObject json_m_visible_run_list;
    json_m_visible_run_list = iter_visible_object.value().toObject();
    // Now we should find the next key
    QJsonObject::const_iterator iter_visible = json_m_visible_run_list.find("m_visible_run_list");
    m_visible_run_list = PBJsonUtils::JSONToQDBusObjectPathArray("m_visible_run_list",json_m_visible_run_list);

}

void GuiEngine::SetSessionStateMetadata(const QDBusObjectPath session, \
                                        const QString &flags, \
                                        const QString &running_job_name, \
                                        const QString &title, \
                                        const QByteArray& app_blob, \
                                        const QString &app_id)
{
    qDebug() << "GuiEngine::SetSessionStateMetadata() \n" \
             << " " << session.path() \
             << "\nflags           : " << flags \
             << "\nrunning_job_name: " << running_job_name \
             << "\ntitle           : " << title \
             << "\napp_blob        : " << app_blob \
             << "\napp_id          : " << app_id;
    QMap<QString,QVariant> metadata;
    // flags contains an array of strings in a variant
    QStringList flags_array;
    // only one string for the moment
    flags_array.append(flags);
    QVariant flags_variant;
    flags_variant = QVariant::fromValue<QStringList>(flags_array);
    metadata.insert("flags",flags_variant);
    metadata.insert("running_job_name",running_job_name);
    metadata.insert("title",title);
    metadata.insert("app_blob",app_blob);
    metadata.insert("app_id",app_id);
    QDBusInterface iface(PBBusName, \
                         session.path(), \
                         ofDPropertiesName, \
                         QDBusConnection::sessionBus());
    QDBusMessage reply = iface.call("Set",PBSessionStateInterface,"metadata",metadata);
    if (reply.type() != QDBusMessage::ReplyMessage) {
        qDebug() << "Failed to set metadata:";
        decodeDBusMessageType(reply);
    }
}

const QVariantMap GuiEngine::SessionStateMetadata(const QDBusObjectPath session)
{
    qDebug("SessionStateMetadata");
    QVariantMap properties;
    om_smalldict results;
    // temp
    PBTreeNode* node = new PBTreeNode();
    properties = node->GetObjectProperties(session,PBSessionStateInterface);
    QVariantMap::iterator iter = properties.find("metadata");
    QVariant variant = iter.value();
    const QDBusArgument qda = variant.value<QDBusArgument>();
    qda >> results;
    delete node;
    QVariantMap metadata;
    // Convert om_smalldict to QVariantMap
    om_smalldict::iterator iter_m = results.begin();
    QString metadata_str = "Metadata : ";
    while(iter_m != results.end()) {
        metadata.insert(iter_m.key(),iter_m.value().variant());
        metadata_str.append(iter_m.key());
        metadata_str.append(":");
        metadata_str.append(iter_m.value().variant().toString());
        metadata_str.append(" ");
        iter_m++;
    }
    return metadata;
}

void GuiEngine::SessionPersistentSave(const QDBusObjectPath session)
{
    QDBusInterface iface(PBBusName, \
                         session.path(), \
                         PBSessionStateInterface, \
                         QDBusConnection::sessionBus());
    // No reply expected from this
    iface.call("PersistentSave");
}

void GuiEngine::GuiSessionRemove(void)
{
    return SessionRemove(m_session);
}

void GuiEngine::SessionRemove(const QDBusObjectPath session)
{
    qDebug() << "GuiEngine::SessionRemove() ";
    QDBusInterface iface(PBBusName, \
                         session.path(), \
                         PBSessionStateInterface, \
                         QDBusConnection::sessionBus());

    // No reply expected from this
    iface.call("Remove");
}
const QString GuiEngine::GuiPreviousSessionFile(void)
{
    // Create a session and "seed" it with my job list:
    m_job_list = GetAllJobs();
    // Create a session
    m_session = CreateSession(m_job_list);
    QString previous = PreviousSessionFile(m_session);
    return previous;
}

void GuiEngine::GuiCreateSession(void)
{
    // Create a session and "seed" it with my job list:
    m_job_list = GetAllJobs();
    // Create a session
    m_session = CreateSession(m_job_list);
}

const QString GuiEngine::PreviousSessionFile(const QDBusObjectPath session)
{
    qDebug() << "GuiEngine::PreviousSessionFile() ";
    QDBusInterface iface(PBBusName, \
                         session.path(), \
                         PBSessionStateInterface, \
                         QDBusConnection::sessionBus());
    QDBusReply<QString> reply = iface.call("PreviousSessionFile");
    return reply;
}

void GuiEngine::SessionResume(const QDBusObjectPath session)
{
    qDebug() << "GuiEngine::SessionResume() ";
    QDBusInterface iface(PBBusName, \
                         session.path(), \
                         PBSessionStateInterface, \
                         QDBusConnection::sessionBus());
    iface.call("Resume");
}

bool GuiEngine::WhiteListDesignates(const QDBusObjectPath white_opath, \
                                    const QDBusObjectPath job_opath)
{
    QDBusInterface iface(PBBusName, \
                         white_opath.path(), \
                         PBWhiteListInterface, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug("Could not connect to \
               com.canonical.certification.PlainBox.WhiteList1 interface");
    }
    QDBusReply<bool> reply = \
            iface.call("Designates",\
                       QVariant::fromValue<QDBusObjectPath>(job_opath));
    if (!reply.isValid()) {
        qDebug() << "Failed to call whitelist Designates" << \
                    reply.error().name();
        return false;   // Error case defaults to dont run
    }
    return reply.value();
}

QDBusObjectPath GuiEngine::CreateSession(QList<QDBusObjectPath> job_list)
{
    QDBusObjectPath session;
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug("Could not connect to \
               com.canonical.certification.PlainBox.Service1 interface");
        return session;
    }
    QDBusReply<QDBusObjectPath> reply = \
            iface.call("CreateSession",\
                       QVariant::fromValue<opath_array_t>(job_list));
    if (reply.isValid()) {
        session = reply.value();
    } else {
        qDebug("Failed to CreateSession()");
    }
    return session;
}

QList<QDBusObjectPath> GuiEngine::GetLocalJobs(const QList<QDBusObjectPath> &job_list)
{
    QList<QDBusObjectPath> generator_jobs;
    QListIterator<QDBusObjectPath> jobs(job_list);
    while (jobs.hasNext()) {
        QDBusObjectPath job = jobs.next();
        QDBusInterface job_iface(PBBusName, \
                           job.path(), \
                           CheckBoxJobDefinition1, \
                           QDBusConnection::sessionBus());
        if (!job_iface.isValid()) {
            throw std::runtime_error("Could not connect to com.canonical.certification.CheckBox.JobDefinition1 interface");
        }
        if (job_iface.property("plugin").toString() == "local") {
            generator_jobs.append(job);
            qDebug() << job.path();
        }
    }
    return generator_jobs;
}

QList<QDBusObjectPath> GuiEngine::GetAllJobs(void)
{
    QList<QDBusObjectPath> jobs;
    QList<PBTreeNode*> jobnodes = GetJobNodes();
    QList<PBTreeNode*>::const_iterator iter = jobnodes.begin();
    while(iter != jobnodes.end()) {
        PBTreeNode* node = *iter;
        // now append this to the list of jobs to feed to CreateSession()
        jobs.append(node->object_path);
        iter++;
    }
    return jobs;
}

QVariantMap GuiEngine::GetEstimatedDuration()
{
    QVariantMap estimated_duration;
    QDBusInterface iface(PBBusName, \
                         m_session.path(), \
                         PBSessionStateInterface, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        throw std::runtime_error("Could not connect to com.canonical.certification.PlainBox.Service1 interface");
    }
    QDBusReply<EstimatedDuration> reply = \
            iface.call("GetEstimatedDuration");
    if (reply.isValid()) {
        estimated_duration["automated_duration"] = QVariant::fromValue(reply.value().automated_duration);
        estimated_duration["manual_duration"] = QVariant::fromValue(reply.value().manual_duration);
    } else {
        throw std::runtime_error("GetEstimatedDuration() failed, invalid reply");
    }
    return estimated_duration;
}


/* Shouldnt this really return QList<QDBusObjectPath> ?
 *
 * At present it doesnt because it matches the Plainbox return type, which
 * appears to be inconsistent at least.
 */
QStringList GuiEngine::UpdateDesiredJobList(const QDBusObjectPath session, \
                                            QList<QDBusObjectPath> desired_job_list)
{
    QStringList job_list;
    QDBusInterface iface(PBBusName, \
                         session.path(), \
                         PBSessionStateInterface, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug("Could not connect to \
               com.canonical.certification.PlainBox.Service1 interface");
        return job_list;
    }
    QDBusReply<QStringList> reply = \
            iface.call("UpdateDesiredJobList",\
                       QVariant::fromValue<opath_array_t>(desired_job_list));
    if (reply.isValid()) {
        job_list = reply.value();
    } else {
        qDebug("Failed to CreateSession()");
    }
    return job_list;
}

QList<QDBusObjectPath> GuiEngine::SessionStateDesiredJobList(const QDBusObjectPath session)
{
    PBTreeNode node;
    QVariantMap map = node.GetObjectProperties(session,PBSessionStateInterface);
    QList<QDBusObjectPath> opathlist;
    QVariantMap::iterator iter = map.find("desired_job_list");
    QVariant variant = iter.value();
    const QDBusArgument qda = variant.value<QDBusArgument>();
    qda >> opathlist;
    return opathlist;
}

QList<QDBusObjectPath> GuiEngine::SessionStateRunList(const QDBusObjectPath session)
{
    PBTreeNode node;
    QVariantMap map = node.GetObjectProperties(session,PBSessionStateInterface);
    QList<QDBusObjectPath> opathlist;
    QVariantMap::iterator iter = map.find("run_list");
    QVariant variant = iter.value();
    const QDBusArgument qda = variant.value<QDBusArgument>();
    qda >> opathlist;
    return opathlist;
}

QList<QDBusObjectPath> GuiEngine::SessionStateJobList(const QDBusObjectPath session)
{
    PBTreeNode node;
    QVariantMap map = node.GetObjectProperties(session,PBSessionStateInterface);
    QList<QDBusObjectPath> opathlist;
    QVariantMap::iterator iter = map.find("job_list");
    QVariant variant = iter.value();
    const QDBusArgument qda = variant.value<QDBusArgument>();
    qda >> opathlist;
    return opathlist;
}


void GuiEngine::RunJob(const QDBusObjectPath session, \
                       const QDBusObjectPath opath)
{
    QStringList job_list;
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() <<"Could not connect to " << PBInterfaceName;
        return;
    }
    QDBusPendingCall async_reply = iface.asyncCall("RunJob", \
                QVariant::fromValue<QDBusObjectPath>(session), \
                QVariant::fromValue<QDBusObjectPath>(opath));
    QDBusPendingCallWatcher watcher(async_reply,this);
    watcher.waitForFinished();
    m_waiting_result = true;
    QDBusPendingReply<QString,QByteArray> reply = async_reply;
    if (reply.isError()) {
        // For the moment, we wont get the "say" signature, just "o"
        QDBusError qde = reply.error();
        if (qde.name().compare("org.freedesktop.DBus.Error.InvalidSignature") !=0) {
            qDebug() << qde.name() << " " << qde.message();
        }
    }
}

jsm_t GuiEngine::GetJobStateMap(void)
{
    jsm_t jsm;
    QVariantMap properties = \
            pb_objects->GetObjectProperties(m_session,PBSessionStateInterface);
    // Now dig out the relevant properties
    QVariantMap::iterator iter = properties.find("job_state_map");
    QVariant variant = iter.value();
    if (!variant.isValid()) {
        qDebug("Cannot obtain the Job State Map");
        return jsm;
    }
    const QDBusArgument qda = variant.value<QDBusArgument>();
    qda >> jsm;
    // Preserve this for future use
    m_jsm = jsm;
    return jsm;
}

void GuiEngine::GetJobStates(void)
{
    if (m_jsm.isEmpty()) {
        return;
    }
    // Have we collected this before? if so, lets clean up and start again
    if (m_job_state_list.count()) {
        // we need to delete each item
        for(int i=0;i<m_job_state_list.count();i++) {
            delete m_job_state_list.at(i);
        }
        // Now empty the list of (now useless) pointers to PBTreeNodes)
        m_job_state_list.clear();
    }
    // Run through each Job State
    jsm_t::iterator iter = m_jsm.begin();
    while(iter!=m_jsm.end()) {
        // Object Name
        QDBusObjectPath opath = iter.value();
        PBTreeNode* node = new PBTreeNode();
        node->AddNode(node,opath);
        m_job_state_list.append(node);
        iter++;
    }
}

void GuiEngine::GetJobResults(void)
{
    if (m_job_state_list.empty()) {
        qDebug("No Job States available yet");
        return;
    }
    // Have we collected this before? if so, lets clean up and start again
    if (m_job_state_results.count()) {
        // we need to delete each item
        for(int i=0;i<m_job_state_results.count();i++) {
            delete m_job_state_results.at(i);
        }
        // Now empty the list of (now useless) pointers to PBTreeNodes)
        m_job_state_results.clear();
    }
    for (int i=0;i<m_job_state_list.count();i++) {
        QDBusObjectPath opath;
        PBTreeNode* node = m_job_state_list.at(i);
        QDBusObjectPath job = node->job();
        QDBusObjectPath result = node->result();
        // now, append the results to m_job_state_results;
        PBTreeNode* result_node = new PBTreeNode();
        result_node->AddNode(result_node,result);
        m_job_state_results.append(result_node);
    }
}

// temporary - Print the DBus argument type
void decodeDBusArgType(const QDBusArgument &arg)
{
    // Print the signature
    qDebug() << "Signature is: "<< arg.currentSignature();
    QString type;
    switch (arg.currentType())
    {
    case QDBusArgument::BasicType:
        type = "BasicType";
        break;
    case QDBusArgument::VariantType:
        type = "VariantType";
        break;
    case QDBusArgument::ArrayType:
        type = "ArrayType";
        break;
    case QDBusArgument::StructureType:
        type = "StructureType";
        break;
    case QDBusArgument::MapType:
        type = "MapType";
        break;
    case QDBusArgument::MapEntryType:
        type = "MapEntryType";
        break;
    case QDBusArgument::UnknownType:
        type = "Unknown";
        break;
    default:
        type = "UNRECOGNISED";
    }
    qDebug() << "Type: " << type;
}

// temporary - print the DBus message reply type
void decodeDBusMessageType(const QDBusMessage &msg)
{
    QString type;
    switch (msg.type())
    {
        case QDBusMessage::MethodCallMessage:
        type = "MethodCallMessage";
        break;
        case QDBusMessage::SignalMessage:
        type = "SignalMessage";
        break;
        case QDBusMessage::ReplyMessage:
        type = "ReplyMessage";
        break;
        case QDBusMessage::ErrorMessage:
        type = "ErrorMessage";
        break;
        case QDBusMessage::InvalidMessage:
        type = "InvalidMessage";
        break;
        default:
        type = "UNRECOGNISED";
    }
    qDebug() << "Type: " << type << msg.errorMessage() << " " << msg.errorName();
}

JobTreeNode* GuiEngine::GetJobTreeNodes(void)
{
    if (job_tree) {
        // lets re-build it as the PBTree may have changed
        delete job_tree;
    }
    job_tree = new JobTreeNode();
    // Get our list of jobs
    QList<PBTreeNode*> jobnodes = GetJobNodes();
    for (int i = 0; i< jobnodes.count(); i++) {
        /* We assemble a path of PBTreeNodes to represent the chain to the
        * top of our notional tree. It will be in discovered order.
        */
        PBTreeNode* node = jobnodes.at(i);
        QList<PBTreeNode*> chain;
        PBTreeNode* next = node;
        while(next) {
            chain.prepend(next);
            next = PBTreeNode::FindJobNode(next->via(),jobnodes);
        }
        job_tree->AddNode(job_tree, chain);
    }
    return job_tree;
}


QList<QDBusObjectPath> GuiEngine::GenerateDesiredJobList()
{
    QList<QDBusObjectPath> desired_job_list;
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug("Could not connect to \
               com.canonical.certification.PlainBox.Service1 interface");
        return desired_job_list;
    }
    QList<QDBusObjectPath> whitelists;
    QMap<QDBusObjectPath, bool>::iterator iter = whitelist.begin();
    while (iter != whitelist.end()) {
        if (iter.value()) {
            whitelists.append(iter.key());
        }
        iter++;
    }
    QDBusReply<opath_array_t> reply = \
            iface.call("SelectJobs", \
                       QVariant::fromValue<opath_array_t>(whitelists));
    if (reply.isValid()) {
        desired_job_list = reply.value();
    } else {
        qDebug("Failed to GenerateDesiredJobList()");
    }
    return desired_job_list;
}

void GuiEngine::UpdateJobResult(const QDBusObjectPath session, \
                                           const QDBusObjectPath &job_path, \
                                           const QDBusObjectPath &result_path
                                           )
{
    QDBusInterface iface(PBBusName, \
                         session.path(), \
                         PBSessionStateInterface, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() <<"Could not connect to " << PBInterfaceName;
        return;
    }
    QDBusMessage reply = \
            iface.call("UpdateJobResult", \
                       QVariant::fromValue<QDBusObjectPath>(job_path), \
                       QVariant::fromValue<QDBusObjectPath>(result_path));
    if (reply.type() != QDBusMessage::ReplyMessage) {
        qDebug() << "Error: " << reply.errorName() << " " << reply.errorName();
    }
}

QString GuiEngine::GetCommand(const QDBusObjectPath& opath)
{
    PBTreeNode node;
    QVariantMap map = node.GetObjectProperties(opath,CheckBoxJobDefinition1);
    QString command;
    QVariantMap::iterator iter = map.find("command");
    QVariant variant = iter.value();
    command = variant.value<QString>();
    return command;
}

void GuiEngine::RunCommand(const QDBusObjectPath& runner)
{
    qDebug("GuiEngine::RunCommand");
    QDBusInterface iface(PBBusName, \
                         runner.path(), \
                         PBJobRunnerInterface, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() <<"Could not connect to " << PBJobRunnerInterface;
        return;
    }
    QDBusMessage reply = iface.call("RunCommand");
    if (reply.type() != QDBusMessage::ReplyMessage) {
        qDebug() << "Error: " << reply.errorName() << " " << reply.errorName();
    }
    qDebug("GuiEngine::RunCommand");
}

void GuiEngine::SetOutcome(const QDBusObjectPath &runner, \
                           const QString &outcome, \
                           const QString &comments)
{
    qDebug("GuiEngine::SetOutcome");
    QDBusInterface iface(PBBusName, \
                         runner.path(), \
                         PBJobRunnerInterface, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() <<"Could not connect to " << PBInterfaceName;
        return;
    }
    QDBusMessage reply = \
            iface.call("SetOutcome", \
                       QVariant::fromValue<QString>(outcome), \
                       QVariant::fromValue<QString>(comments));
    if (reply.type() != QDBusMessage::ReplyMessage) {
        qDebug() << "Error: " << reply.errorName() << " " << reply.errorName();
    }
    qDebug("GuiEngine::SetOutcome - Done");
}

/* A synthesised method. This is needed in the case of skipping tests
 * on resuming a session, since in this circumstance, there is no
 * runner object to serve as a means of setting the outcome.
 */
QDBusObjectPath GuiEngine::SetJobOutcome(const QDBusObjectPath &job_path, \
                                         const QString &outcome, \
                                         const QString &comments)
{
    qDebug() << "GuiEngine::SetJobOutcome() " << job_path.path() << " " << outcome;
    /* first, we need to go through the m_job_state_list to find the
     * relevant job to result mapping. then we go through m_job_state_results
     * to obtain the actual result.
     */
     QDBusObjectPath resultpath;
     for(int i=0; i < m_job_state_list.count(); i++) {
         if (m_job_state_list.at(i)->job().path().compare(job_path.path()) == 0) {
             // ok, we found the right statelist entry
             resultpath = m_job_state_list.at(i)->result();
             break;
         }
     }
      // Now to find the right result object
     for(int i=0;i<m_job_state_results.count();i++) {
         if (m_job_state_results.at(i)->object_path.path().compare(resultpath.path()) == 0) {
             m_job_state_results.at(i)->setOutcome(outcome);
             m_job_state_results.at(i)->setComments(comments);
             break;
         }
     }
    qDebug() << "GuiEngine::SetJobOutcome() - Done";
    return resultpath;
}

bool GuiEngine::JobCanStart(const QDBusObjectPath &job_path)
{
    qDebug() << "GuiEngine::JobCanStart()";
    /* first, we need to go through the m_job_state_list to find the
     * relevant job to result mapping.
     */
     for(int i=0; i < m_job_state_list.count(); i++) {
         if (m_job_state_list.at(i)->job().path().compare(job_path.path()) == 0) {
             // ok, we found the right statelist entry
             return m_job_state_list.at(i)->CanStart();
         }
     }
     return false;  // Error case defaults to dont run
}

const QString GuiEngine::GetReadinessDescription(const QDBusObjectPath &job_path)
{
    QString empty;
    qDebug() << "GuiEngine::GetReadinessDescription()";
    /* first, we need to go through the m_job_state_list to find the
     * relevant job to result mapping.
     */
     for(int i=0; i < m_job_state_list.count(); i++) {
         if (m_job_state_list.at(i)->job().path().compare(job_path.path()) == 0) {
             // ok, we found the right statelist entry
             return m_job_state_list.at(i)->GetReadinessDescription();
         }
     }
     return empty;
}

void GuiEngine::CatchallShowInteractiveUISignalsHandler(QDBusMessage msg)
{
    qDebug("GuiEngine::CatchallShowInteractiveUISignalsHandler");
    QList<QVariant> args = msg.arguments();
    QList<QVariant>::iterator iter = args.begin();
    QVariant variant = *iter;
    m_runner = variant.value<QDBusObjectPath>();
    QString job_cmd = GetCommand(m_run_list.at(m_current_job_index));
    bool show_test = ! job_cmd.isEmpty();
    // Open the GUI dialog
    if (!m_running_manual_job) {
        // must be the first time for this particular job
        m_running_manual_job = true;
        emit raiseManualInteractionDialog(PBTreeNode::PBJobResult_Skip, show_test);
    } else {
        emit updateManualInteractionDialog(PBTreeNode::PBJobResult_Skip, show_test);
    }
    qDebug("GuiEngine::CatchallShowInteractiveUISignalsHandler - Done");
}

void GuiEngine::CatchallAskForOutcomeSignalsHandler(QDBusMessage msg)
{
    qDebug("GuiEngine::CatchallAskForOutcomeSignalsHandler");
    QList<QVariant> args = msg.arguments();
    QList<QVariant>::iterator iter = args.begin();
    QVariant variant = *iter;
    m_runner = variant.value<QDBusObjectPath>();
    iter++;
    variant = *iter;
    QString suggested_outcome = variant.value<QString>();
    int suggested_status;
    // convert outcome string into a result number
    if (suggested_outcome.compare(JobResult_OUTCOME_PASS) == 0 ) {
        suggested_status = PBTreeNode::PBJobResult_Pass;
    }
    if (suggested_outcome.compare(JobResult_OUTCOME_FAIL) == 0) {
        suggested_status = PBTreeNode::PBJobResult_Fail;
    }
    if (suggested_outcome.compare(JobResult_OUTCOME_SKIP) == 0) {
        suggested_status = PBTreeNode::PBJobResult_Skip;
    }
    QString job_cmd = GetCommand(m_run_list.at(m_current_job_index));
    bool show_test = ! job_cmd.isEmpty();
    // Open the GUI dialog
    if (!m_running_manual_job) {
        // must be the first time for this particular job
        m_running_manual_job = true;
        emit raiseManualInteractionDialog(suggested_status, show_test);
    } else {
        emit updateManualInteractionDialog(suggested_status, show_test);
    }
    qDebug("GuiEngine::CatchallAskForOutcomeSignalsHandler - Done");
}

void GuiEngine::ResumeFromManualInteractionDialog(bool run_test, \
                                                  const QString outcome, \
                                                  const QString comments)
{
    qDebug("GuiEngine::ResumeFromManualInteraction()");
    if (run_test) {
        RunCommand(m_runner);
        return;
    }
    // No longer running a manual test
    m_running_manual_job = false;
    // This should trigger a further JobResultAvailable event
    SetOutcome(m_runner,outcome,comments);
    qDebug("GuiEngine::ResumeFromManualInteraction()");
}

const QString ConvertOutcome(const int outcome)
{
    // convert outcome id into a string
    switch(outcome) {
        case PBTreeNode::PBJobResult_Pass:
            return JobResult_OUTCOME_PASS;
        break;
        case PBTreeNode::PBJobResult_Fail:
            return JobResult_OUTCOME_FAIL;
        break;
        case PBTreeNode::PBJobResult_Skip:
            return JobResult_OUTCOME_SKIP;
        break;
        default:
            return "?";
    }
}

QString GuiEngine::GuiExportSessionAsXML(void)
{
    qDebug("GuiEngine::GuiExportSessionAsXML");
    QString output_format = "xml";
    QStringList options;    // No options
    return ExportSession(m_session,output_format,options);
}

QString GuiEngine::GuiExportSessionAsHTML(void)
{
    qDebug("GuiEngine::GuiExportSessionAsHTML");
    QString output_format = "html";
    QStringList options;    // No options
    return ExportSession(m_session,output_format,options);
}

QString GuiEngine::GuiExportSessionAsXLSX(void)
{
    qDebug("GuiEngine::GuiExportSessionAsXLSX");
    QString output_format = "xlsx";
    QStringList options;    // No options
    return ExportSession(m_session,output_format,options);
}


const QString GuiEngine::ExportSession(const QDBusObjectPath session, \
                                       const QString &output_format, \
                                       const QStringList& option_list)
{
    QString empty;
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() <<"Could not connect to " << PBInterfaceName;
        // no meaningful results really
        return empty;
    }
    // Construct a list of QVariants?
    QVariantList varlist;
    for(int i=0;i<option_list.count(); i++) {
        varlist.append(option_list.at(i));
    }
    QDBusReply<QString> reply = \
            iface.call("ExportSession", \
                       QVariant::fromValue<QString>(session.path()), \
                       QVariant::fromValue<QString>(output_format), \
                       varlist);
    if (!reply.isValid()) {
        qDebug() << "Error: " << reply.error();
        return empty;
    }
    return reply;
}

bool GuiEngine::GuiExportSessionToFileAsXML(const QString& output_file,
                                            const QStringList& option_list)
{
    QString output_format = "xml";
    // very basic argument checking
    if (output_file.isEmpty()) {
        return false;
    }
    // FIXME - When we get a useful success/failure code here, return to caller
    QString done = ExportSessionToFile(m_session,output_format,option_list,output_file);
    return true;
}

bool GuiEngine::GuiExportSessionToFileAsHTML(const QString& output_file,
                                             const QStringList& option_list)
{
    QString output_format = "html";
    // very basic argument checking
    if (output_file.isEmpty()) {
        return false;
    }
    // FIXME - When we get a useful success/failure code here, return to caller
    QString done = ExportSessionToFile(m_session,output_format,option_list,output_file);
    return true;
}

bool GuiEngine::GuiExportSessionToFileAsXLSX(const QString& output_file,
                                             const QStringList& option_list)
{
    QString output_format = "xlsx";
    // very basic argument checking
    if (output_file.isEmpty()) {
        return false;
    }
    // FIXME - When we get a useful success/failure code here, return to caller
    QString done = ExportSessionToFile(m_session,output_format,option_list,output_file);
    return true;
}

const QString GuiEngine::ExportSessionToFile(const QDBusObjectPath session, \
                                             const QString &output_format, \
                                             const QStringList &option_list, \
                                             const QString &output_file)
{
    QString empty;
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() <<"Could not connect to " << PBInterfaceName;
        // no meaningful results really
        return empty;
    }
    // Construct a list of QVariants?
    QVariantList varlist;
    for(int i=0;i<option_list.count(); i++) {
        varlist.append(option_list.at(i));
    }
    QDBusReply<QString> reply = \
            iface.call("ExportSessionToFile", \
                       QVariant::fromValue<QString>(session.path()), \
                       QVariant::fromValue<QString>(output_format), \
                       varlist, \
                       QVariant::fromValue<QString>(output_file));
    if (!reply.isValid()) {
        qDebug() << "Error: " << reply.error();
        return empty;
    }
    return reply;
}

QString GuiEngine::SendDataViaTransport(const QDBusObjectPath session, \
                                        const QString &transport, \
                                        const QString &url, \
                                        const QString &option_list, \
                                        const QString &data)
{
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() << "Could not connect to " << PBInterfaceName;
        return QString("Could not connect to " + PBInterfaceName);
    }
    QDBusReply<QString> reply = \
            iface.call("SendDataViaTransport", \
                       QVariant::fromValue<QString>(session.path()), \
                       QVariant::fromValue<QString>(transport), \
                       QVariant::fromValue<QString>(url), \
                       QVariant::fromValue<QString>(option_list), \
                       QVariant::fromValue<QString>(data));
    if (!reply.isValid()) {
        qDebug() << "Error: " << reply.error();
        return QString("Error: " + reply.error().message());
    }
    return reply;                          
}

const QString GuiEngine::SendSubmissionViaCertificationTransport( \
        const QString &submission_path,
        const QString &secure_id,
        const bool submit_to_hexr)
{
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() << "Could not connect to " << PBInterfaceName;
        return QString("Could not connect to " + PBInterfaceName);
    }
    QDBusReply<QStringList> reply = iface.call("GetAllTransports");
    if (!reply.isValid()) {
        qDebug() << "Error: " << reply.error();
        return QString("Error: " + reply.error().message());
    }
    if (!reply.value().contains("certification")) {
        return QString("'certification' is not a supported transport");
    }
    // Read submission file
    QFile submissionFile(submission_path);
    QByteArray submissionData;
    if (submissionFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        submissionData = submissionFile.readAll();
        submissionFile.close();
    }
    else {
        qDebug() << "Could not read " << submission_path;
        return QString("Could not read " + submission_path);
    }
    QStringList options;
    options << QString("secure_id=" + secure_id);
    options << QString("submit_to_hexr=" + QString::number(submit_to_hexr));
    return SendDataViaTransport(m_session, "certification", \
            "https://certification.canonical.com/submissions/submit/", \
            options.join(','), \
            submissionData);
}

const QString GuiEngine::SendSubmissionViaLaunchpadTransport( \
        const QString &submission_path,
        const QString &email)
{
    QDBusInterface iface(PBBusName, \
                         PBObjectPathName, \
                         PBInterfaceName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug() << "Could not connect to " << PBInterfaceName;
        return QString("Could not connect to " + PBInterfaceName);
    }
    QDBusReply<QStringList> reply = iface.call("GetAllTransports");
    if (!reply.isValid()) {
        qDebug() << "Error: " << reply.error();
        return QString("Error: " + reply.error().message());
    }
    if (!reply.value().contains("launchpad")) {
        return QString("'launchpad' is not a supported transport");
    }
    // Read submission file
    QFile submissionFile(submission_path);
    QByteArray submissionData;
    if (submissionFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        submissionData = submissionFile.readAll();
        submissionFile.close();
    }
    else {
        qDebug() << "Could not read " << submission_path;
        return QString("Could not read " + submission_path);
    }
    QStringList options;
    options << QString("field.emailaddress=" + email);
    return SendDataViaTransport(m_session, "launchpad", \
            "https://launchpad.net/+hwdb/+submit", \
            options.join(','), \
            submissionData);
}

void GuiEngine::CatchallIOLogGeneratedSignalsHandler(QDBusMessage /*msg*/)
{
    /* TODO - This could be used for updating a live display of the IO Log
     * but for now its not important.
     */
}


void GuiEngine::CatchallLocalJobResultAvailableSignalsHandler(QDBusMessage msg)
{
    /* We need information about which job and jobresult we should look at
     * in order to call UpdateJobResult().
     */
    QList<QVariant> args = msg.arguments();
    QList<QVariant>::iterator iter = args.begin();
    QVariant variant = *iter;
    QDBusObjectPath job = variant.value<QDBusObjectPath>();
    iter++;
    variant = *iter;
    QDBusObjectPath result = variant.value<QDBusObjectPath>();
    UpdateJobResult(m_session,job,result);
    // Move to the next job
    m_current_job_index++;
    // Have we finished?
    if (m_run_list.count() != m_current_job_index ) {
        // Not finished, so run the next job
        qDebug() << "Running Local Job " << JobNameFromObjectPath(m_run_list.at(m_current_job_index));
        RunJob(m_session,m_run_list.at(m_current_job_index));
        return;
    }
    qDebug("All Local Jobs completed\n");
    // Now I update the desired job list to get jobs created from local jobs.
    QStringList errors = UpdateDesiredJobList(m_session, m_desired_job_list);
    if (errors.count() != 0) {
        qDebug("UpdateDesiredJobList generated errors:");
        for (int i=0; i<errors.count(); i++) {
            qDebug() << errors.at(i);
        }
    }
    // Disconnect the JobResultAvailable local job signal receiver
    QDBusConnection bus = QDBusConnection ::sessionBus();
    if (!bus.disconnect(PBBusName,\
                     NULL,\
                     PBInterfaceName,\
                     "JobResultAvailable",\
                     this,\
                     SLOT(CatchallLocalJobResultAvailableSignalsHandler(QDBusMessage)))) {
        qDebug("Failed to disconnect slot for JobResultAvailable events");
        // TODO - Emit error for the gui
        return;
    }
    // to get only the *jobs* that are designated by the whitelist.
    m_desired_job_list = GenerateDesiredJobList();
    /* Now I update the desired job list.
        XXX: Remove previous local jobs from this list to avoid evaluating
        them twice
    */
    errors = UpdateDesiredJobList(m_session, m_desired_job_list);
    if (errors.count() != 0) {
        qDebug("UpdateDesiredJobList generated errors:");
        for (int i=0; i<errors.count(); i++) {
            qDebug() << errors.at(i);
        }
    }
    // Now, the run_list contains the list of jobs I actually need to run \o/
    m_run_list = SessionStateRunList(m_session);
    QListIterator<QDBusObjectPath> run_jobs(m_run_list);
    // Keep a copy of what should be visible
    m_visible_run_list = m_run_list;
    // Repopulate our knowledge of PlainBox
    RefreshPBObjects();
    // we should emit a signal to say its all done
    emit localJobsCompleted();
}

void GuiEngine::CatchallJobResultAvailableSignalsHandler(QDBusMessage msg)
{
//    qDebug("GuiEngine::CatchallJobResultAvailableSignalsHandler");

    if (msg.type() != 0) { // QDBusMessage::InvalidMessage
        /* We need information about which job and jobresult we should look at
         * in order to call UpdateJobResult().
         */
        QList<QVariant> args = msg.arguments();
        QList<QVariant>::iterator iter = args.begin();
        QVariant variant = *iter;
        QDBusObjectPath job = variant.value<QDBusObjectPath>();
        iter++;
        variant = *iter;
        QDBusObjectPath result = variant.value<QDBusObjectPath>();
        UpdateJobResult(m_session,job,result);
        // How did this job turn out?
        const int outcome = GetOutcomeFromJobResultPath(result);
        if (m_running_manual_job) {
            m_running_manual_job = false;
            emit closeManualInteractionDialog();
        }
        // Update the GUI so it knows what the job outcome was
        emit updateGuiEndJob(m_run_list.at(m_current_job_index).path(), \
                m_current_job_index, \
                outcome, \
                JobNameFromObjectPath(m_run_list.at(m_current_job_index)));
        // Ok, lets note that we've run this, remove it from rerun
        m_rerun_list.removeOne(m_run_list.at(m_current_job_index));
        // Move to the next job
        m_current_job_index = NextRunJobIndex(m_current_job_index);
        m_waiting_result = false;
        // We should deal with Pause/Resume here
        if (!m_running) {
            // Dont start the next job
            return;
        }
    }
    if (m_run_list.count() != m_current_job_index) {
        // Update the GUI so it knows what job is starting
        emit updateGuiBeginJob(m_run_list.at(m_current_job_index).path(), \
                m_current_job_index, \
                JobNameFromObjectPath(m_run_list.at(m_current_job_index)));
        // Preserve progress so far
        EncodeGuiEngineStateAsJSON();
        if (JobCanStart(m_run_list.at(m_current_job_index))) {
            // Now run the next job
            qDebug() << "Running Job (CatchallJobResultAvailableSignalsHandler)" << JobNameFromObjectPath(m_run_list.at(m_current_job_index));
            RunJob(m_session,m_run_list.at(m_current_job_index));
        } else {
            // Now, we can set the outcome/comments of this test
            QDBusObjectPath result = SetJobOutcome(m_run_list.at(m_current_job_index), JobResult_OUTCOME_NOT_SUPPORTED, GetReadinessDescription(m_run_list.at(m_current_job_index)));
            UpdateJobResult(m_session, m_run_list.at(m_current_job_index), result);
            emit updateGuiEndJob(m_run_list.at(m_current_job_index).path(), \
                    m_current_job_index, \
                    PBTreeNode::PBJobResult_DepsNotMet, \
                    JobNameFromObjectPath(m_run_list.at(m_current_job_index)));
            m_current_job_index = NextRunJobIndex(m_current_job_index);
            QDBusMessage fake_msg;
            CatchallJobResultAvailableSignalsHandler(fake_msg);
        }
        return;
    }
    // nothing should be left for re-run
    m_rerun_list.clear();
    // Finaly note that its all over
    EncodeGuiEngineStateAsJSON();
    // Tell the GUI its all finished
    emit jobsCompleted();
}

void GuiEngine::AcknowledgeLocalJobsDone(void)
{
    qDebug("GuiEngine::AcknowledgeJobsDone()");
    m_local_jobs_done = true;
    qDebug("GuiEngine::AcknowledgeJobsDone() - done");
}

void GuiEngine::AcknowledgeJobsDone(void)
{
    qDebug("GuiEngine::AcknowledgeJobsDone()");
    m_jobs_done = true;
    qDebug("GuiEngine::AcknowledgeJobsDone() - done");
}

void GuiEngine::ManualTest(const int /*outcome*/)
{
    qDebug("GuiEngine::ManualTestAsk");
    // We run the manual test _once_
    if (!m_testing_manual_job) {
        m_testing_manual_job = true;
        ResumeFromManualInteractionDialog(true,"" /* outcome */,"" /* comments */);
    } else {
        m_testing_manual_job = false;
        ResumeFromManualInteractionDialog(false,"pass","Run by test-gui-engine");
    }
    qDebug("GuiEngine::ManualTestAsk");
}

// Returns a list of DBus Object Paths for valid tests
const QList<QDBusObjectPath>& GuiEngine::GetValidRunList(void)
{
    return m_run_list;
}

/* Returns a list of DBusObjectPaths representing tests
 * which are relevant for human beings (i.e. excludes resource jobs)
 */
const QList<QDBusObjectPath>& GuiEngine::GetVisibleRunList(void)
{
    return m_visible_run_list;
}

int GuiEngine::ValidRunListCount(void)
{
    return m_run_list.count();
}

bool GuiEngine::RefreshPBObjects(void)
{
    qDebug("GuiEngine::RefreshPBObjects");
    // We must have reached the end, so
    if (pb_objects) {
        delete pb_objects;
    }
    // Obtain the initial tree of Plainbox objects, starting at the root "/"
    pb_objects = new PBTreeNode();
    pb_objects->AddNode(pb_objects, QDBusObjectPath("/"));
    if (!pb_objects) {
        qDebug("Failed to get Plainbox Objects");
        return false;
    }
    qDebug("GuiEngine::RefreshPBObjects - Done");
    return true;
}

const QString GuiEngine::JobNameFromObjectPath(const QDBusObjectPath& opath)
{
    QString empty;
    QList<PBTreeNode*> jlist = GetJobNodes();
    for(int i=0;i<jlist.count();i++) {
        if (jlist.at(i)->object_path.path().compare(opath.path()) == 0) {
            return jlist.at(i)->name();
        }
    }
    return empty;
}

const QString GuiEngine::GetIOLogFromJobPath(const QDBusObjectPath &opath)
{
    QString io_log;
    /* first, we need to go through the m_job_state_list to find the
     * relevant job to result mapping. then we go through m_job_state_results
     * to obtain the actual result.
     */
    QDBusObjectPath iologpath;
    GetJobStateMap();
    GetJobStates();
    for(int i=0; i < m_job_state_list.count(); i++) {
        if (m_job_state_list.at(i)->job().path().compare(opath.path()) == 0) {
            // ok, we found the right statelist entry
            iologpath = m_job_state_list.at(i)->result();
            break;
        }
    }
    GetJobResults();
    // Now to find the right result object
    for(int i=0;i<m_job_state_results.count();i++) {
        if (m_job_state_results.at(i)->object_path.path().compare(iologpath.path()) == 0) {
            io_log = m_job_state_results.at(i)->io_log();
            break;
        }
    }
    return io_log;
}

int GuiEngine::GetOutcomeFromJobResultPath(const QDBusObjectPath &opath)
{
    QString outcome;
    PBTreeNode* result_node = new PBTreeNode();
    result_node->AddNode(result_node, opath);
    outcome = result_node->outcome();
    delete result_node;
    qDebug() << "Real outcome " << outcome;
    // convert outcome string into a result number
    if (outcome.compare(JobResult_OUTCOME_PASS) == 0 ) {
        return PBTreeNode::PBJobResult_Pass;
    }
    if (outcome.compare(JobResult_OUTCOME_FAIL) == 0) {
        return PBTreeNode::PBJobResult_Fail;
    }
    if (outcome.compare(JobResult_OUTCOME_SKIP) == 0) {
        return PBTreeNode::PBJobResult_Skip;
    }
    if (outcome.compare(JobResult_OUTCOME_NONE) == 0) {
        return PBTreeNode::PBJobResult_None;
    }
    // Machine could not otherwise run it
    return PBTreeNode::PBJobResult_DepsNotMet;
}

int GuiEngine::GetOutcomeFromJobPath(const QDBusObjectPath &opath)
{
    QString outcome = "No idea";
   /* first, we need to go through the m_job_state_list to find the
    * to obtain the actual result.
    * relevant job to result mapping. then we go through m_job_state_results
    */
    QDBusObjectPath resultpath;
    for(int i=0; i < m_job_state_list.count(); i++) {
        if (m_job_state_list.at(i)->job().path().compare(opath.path()) == 0) {
            // ok, we found the right statelist entry
            resultpath = m_job_state_list.at(i)->result();
            break;
        }
    }
     // Now to find the right result object
    for(int i=0;i<m_job_state_results.count();i++) {
        if (m_job_state_results.at(i)->object_path.path().compare(resultpath.path()) == 0) {
            outcome = m_job_state_results.at(i)->outcome();
            break;
        }
    }
    qDebug() << "Real outcome " << outcome;
    // convert outcome string into a result number
    if (outcome.compare(JobResult_OUTCOME_PASS) == 0 ) {
        return PBTreeNode::PBJobResult_Pass;
    }
    if (outcome.compare(JobResult_OUTCOME_FAIL) == 0) {
        return PBTreeNode::PBJobResult_Fail;
    }
    if (outcome.compare(JobResult_OUTCOME_SKIP) == 0) {
        return PBTreeNode::PBJobResult_Skip;
    }
    if (outcome.compare(JobResult_OUTCOME_NONE) == 0) {
        return PBTreeNode::PBJobResult_None;
    }
    // Machine could not otherwise run it
    return PBTreeNode::PBJobResult_DepsNotMet;
}

QString GuiEngine::GetSaveFileName(const QString& defaultName,
                                   const QString& text)
{
    QString prompt = "Choose a filename:";
    return QFileDialog::getSaveFileName(NULL, \
                                        prompt, \
                                        defaultName, \
                                        text, \
                                        NULL, \
                                        QFileDialog::DontUseNativeDialog);
}

const QDBusObjectPath GuiEngine::GetCurrentSession(void)
{
    return m_session;
}

const QString GuiEngine::GetIOLog(const QString& job)
{
    // need to go get the result object for this path
    // then get the iolog property
    qDebug() << job;
    // Io_log is Array of [Struct of [Double, String, Array of [Byte])]
    QDBusObjectPath opath(job);
    // FIXME - The log unpacking is not yet completed
    return GetIOLogFromJobPath(opath);
}
