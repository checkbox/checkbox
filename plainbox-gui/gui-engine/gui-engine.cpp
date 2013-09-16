/*
 * This file is part of plainbox-gui
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

#include "PBTreeNode.h"

// Forward declarations
void decodeDBusArgType(const QDBusArgument &arg);       // temporary
void decodeDBusMessageType(const QDBusMessage &msg);    // temporary

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
    m_running(true),
    m_running_manual_job(false),
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


        // Obtain the initial tree of Plainbox objects, starting at the root "/"
        RefreshPBObjects();

        // Connect our change receivers
        QDBusConnection bus = QDBusConnection ::sessionBus();

// FIXME - We will want these for process real job signals. For now they clutter the log :)
/*
        if (!bus.connect(PBBusName, \
                         PBObjectPathName, \
                         ofDObjectManagerName,\
                         "InterfacesAdded",\
                         this,\
                         SLOT(InterfacesAdded(QDBusMessage)))) {

            qDebug("Failed to connect slot for InterfacesAdded events");

            return false;
        }

        if (!bus.connect(PBBusName,\
                         PBObjectPathName,\
                         ofDObjectManagerName,\
                         "InterfacesRemoved",\
                         this,\
                         SLOT(InterfacesRemoved(QDBusMessage)))) {

            qDebug("Failed to connect slot for InterfacesRemoved events");

            return false;
        }
*/

        // Connect the JobResultAvailable signal receiver
        if (!bus.connect(PBBusName,\
                         NULL,\
                         PBInterfaceName,\
                         "JobResultAvailable",\
                         this,\
                         SLOT(CatchallLocalJobResultAvailableSignalsHandler(QDBusMessage)))) {

            qDebug("Failed to connect slot for JobResultAvailable events");

            return false;
        }

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
    emit updateGuiObjects("TBD1",0,0);

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
    emit updateGuiObjects("TBD2",0,0);

    qDebug("GuiEngine::InterfacesRemoved - done");
}

QList<PBTreeNode*> GuiEngine::GetJobNodes(void)
{
    //qDebug("GuiEngine::GetJobNodes()");

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

    //qDebug("GuiEngine::GetJobNodes() - done");

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

            paths_and_names.insert(child->object_path,name);

            // First time round, fill in our whitelist member
            if (!initialised) {
                whitelist.insert(child->object_path,true);
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

// temporary helper
void GuiEngine::dump_whitelist_selection(void)
{
    // loop around all the children
    QMap<QDBusObjectPath,bool>::const_iterator iter = whitelist.begin();

    while(iter != whitelist.end() ) {

        bool yes = iter.value();

        qDebug() << iter.key().path() << (yes ? "Yes" : "No");

        iter++;
    }
}

void GuiEngine::Pause(void)
{
    // Very simple
    m_running = false;
}

void GuiEngine::Resume(void)
{
    if (!m_running) {

        // Make a note of it
        m_running = true;

        if (m_run_list.count() != m_current_job_index) {

            // Update the GUI so it knows what job is starting
            emit updateGuiObjects(m_run_list.at(m_current_job_index).path(), \
                                  m_current_job_index, \
                                  PBTreeNode::PBJobResult_Running);

            // Now run the next job
            qDebug() << "Running Job " << JobNameFromObjectPath(m_run_list.at(m_current_job_index));

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


    QList<QDBusObjectPath> temp_desired_job_list = \
            JobTreeNode::FilteredJobs(m_final_run_list,m_desired_job_list);

    QStringList errors = UpdateDesiredJobList(m_session, temp_desired_job_list);
    if (errors.count() != 0) {
        qDebug("UpdateDesiredJobList generated errors:");

        for (int i=0; i<errors.count(); i++) {
            qDebug() << errors.at(i);
        }
    }

    // Now, the run_list contains the list of jobs I actually need to run \o/
    m_run_list = SessionStateRunList(m_session);

//    qDebug("\n\nGuiEngine::PrepareJobs() - Done\n");

    // useful to the gui (summary bar in test selection screen)
    return m_run_list.count();
}

/* Run all the "real" test jobs. For consistency and clarity, we follow the
 * logic found in dbus-mini-client.py
 */
void GuiEngine::RunJobs(void)
{
//    qDebug("GuiEngine::RunJobs");

    // Start tracking which Job we are running, from the beginning
    m_current_job_index = 0;

    // Tell the GUI so we know we have started running this job
    emit updateGuiObjects(m_run_list.at(m_current_job_index).path(), \
                          m_current_job_index, \
                          PBTreeNode::PBJobResult_Running);

    // Now the actual run, job by job
    qDebug() << "Running Job " << JobNameFromObjectPath(m_run_list.at(m_current_job_index));

    RunJob(m_session,m_run_list.at(m_current_job_index));

//    qDebug("GuiEngine::RunJobs - Done");
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

    // Create a session and "seed" it with my job list:
    m_job_list = GetAllJobs();

    // Create a session
    m_session = CreateSession(m_job_list);

    // to get only the *jobs* that are designated by the whitelist.
    m_desired_job_list = GenerateDesiredJobList(m_job_list);

    // This is just the list of all provider jobs marked "local"
    m_local_job_list = GetLocalJobs();

    // desired local jobs are the Union of all local jobs and the desired jobs
    m_desired_local_job_list = JobTreeNode::FilteredJobs(m_local_job_list, \
                                                         m_desired_job_list);

    // Now I update the desired job list.
    QStringList errors = UpdateDesiredJobList(m_session, \
                                              m_desired_local_job_list);
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

bool GuiEngine::WhiteListDesignates(const QDBusObjectPath white_opath, \
                                    const QDBusObjectPath job_opath)
{
    /*
      qDebug() << "GuiEngine::WhiteListDesignates " << white_opath.path() << \
                job_opath.path();
    */

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

QList<QDBusObjectPath> GuiEngine::GetLocalJobs(void)
{
    QList<QDBusObjectPath> generator_jobs;

    QList<PBTreeNode*> jobnodes = GetJobNodes();

    QList<PBTreeNode*>::const_iterator iter = jobnodes.begin();

    while(iter != jobnodes.end()) {

        PBTreeNode* node = *iter;

        QList<PBObjectInterface*> interfaces = node->interfaces;

        // Now find the plainbox interface
        for (int i=0; i< interfaces.count(); i++) {
            if (interfaces.at(i)->interface.compare(CheckBoxJobDefinition1) == 0) {

                // Now we need to find the plugin property
                QVariant variant;

                variant = interfaces.at(i)->properties.find("plugin").value();

                if (variant.isValid() && variant.canConvert(QMetaType::QString)) {
                    if (variant.toString().compare("local") == 0) {

                        // now append this to the list of jobs for CreateSession()
                        generator_jobs.append(node->object_path);
                    }
                }
            }
        }

        iter++;
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
//    qDebug() << "RunJob() " << session.path() << " " << opath.path();

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
//    qDebug("GuiEngine::GetJobStateMap()");

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

//    qDebug("GuiEngine::GetJobStateMap() - done");

    return jsm;
}

void GuiEngine::GetJobStates(void)
{
//    qDebug("GuiEngine::GetJobStates()");

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

//    qDebug("GuiEngine::GetJobStates() - Done");
}

void GuiEngine::GetJobResults(void)
{
//    qDebug("GuiEngine::GetJobResults()");

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

        //QVariant variant = node->interfaces.

        QDBusObjectPath job = node->job();
        QDBusObjectPath result = node->result();

        //qDebug() << "job " << job.path() << " result " << result.path();

        // now, append the results to m_job_state_results;
        PBTreeNode* result_node = new PBTreeNode();

        result_node->AddNode(result_node,result);

        m_job_state_results.append(result_node);

    }

//    qDebug("GuiEngine::GetJobResults()");
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


QList<QDBusObjectPath> GuiEngine::GenerateDesiredJobList(QList<QDBusObjectPath> job_list)
{
    QList<QDBusObjectPath> desired_job_list;

    // Iterate through each whitelist, and check if it Designates each job
    QMap<QDBusObjectPath, bool>::iterator iter = whitelist.begin();
    while(iter != whitelist.end()) {

        // Try it if we have selected this whitelist
        if (iter.value()) {
            QDBusObjectPath white = iter.key();

            // local_jobs
            for(int i=0; i < job_list.count(); i++) {

                QDBusObjectPath job = job_list.at(i);

                // Does the whitelist designate this job?
                bool ok = WhiteListDesignates(white,job);

                // If ANY whitelist wants this job, we say yes
                if (ok) {
                    if (!desired_job_list.contains(job)) {
                        desired_job_list.append(job);
                    }
                }
            }
        }

        // Next whitelist
        iter++;
    }

    return desired_job_list;
}

void GuiEngine::UpdateJobResult(const QDBusObjectPath session, \
                                           const QDBusObjectPath &job_path, \
                                           const QDBusObjectPath &result_path
                                           )
{
//    qDebug() << "UpdateJobResult() " << session.path() << " " << job_path.path();

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

void GuiEngine::CatchallAskForOutcomeSignalsHandler(QDBusMessage msg)
{
    qDebug("GuiEngine::CatchallAskForOutcomeSignalsHandler");

    QList<QVariant> args = msg.arguments();

    QList<QVariant>::iterator iter = args.begin();

    QVariant variant = *iter;

    m_runner = variant.value<QDBusObjectPath>();

    QString job_cmd = GetCommand(m_run_list.at(m_current_job_index));

    /* FIXME: Find a better way to get the previous result, this one is too
       expensive, see https://bugs.launchpad.net/checkbox-ihv-ng/+bug/1218846

    // Get the interim Job Results
    GetJobStateMap();

    GetJobStates();

    GetJobResults();

    // we should look up the prior job result if available
    const int outcome = GetOutcomeFromJobResultPath(m_run_list.at(m_current_job_index));
    */
    // FIXME: we should look up the prior job result if available
    const int outcome = PBTreeNode::PBJobResult_None;

    // Open the GUI dialog -- TODO - Default the Yes/No/Skip icons
    if (!m_running_manual_job) {
        // must be the first time for this particular job
        m_running_manual_job = true;

        emit raiseManualInteractionDialog(outcome);
    } else {
        emit updateManualInteractionDialog(outcome);
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

bool GuiEngine::GuiExportSessionToFileAsXML(const QString& output_file)
{
    QString output_format = "xml";
    QStringList options;    // No options

    // very basic argument checking
    if (output_file.isEmpty()) {
        return false;
    }

    // FIXME - When we get a useful success/failure code here, return to caller
    QString done = ExportSessionToFile(m_session,output_format,options,output_file);

    return true;
}

bool GuiEngine::GuiExportSessionToFileAsHTML(const QString& output_file)
{
    QString output_format = "html";
    QStringList options;    // No options

    // very basic argument checking
    if (output_file.isEmpty()) {
        return false;
    }

    // FIXME - When we get a useful success/failure code here, return to caller
    QString done = ExportSessionToFile(m_session,output_format,options,output_file);

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

void GuiEngine::CatchallIOLogGeneratedSignalsHandler(QDBusMessage msg)
{
//    qDebug("GuiEngine::CatchallIOLogGeneratedSignalsHandler");

    /* TODO - This could be used for updating a live display of the IO Log
     * but for now its not important.
     */

//    qDebug("GuiEngine::CatchallIOLogGeneratedSignalsHandler - Done");
}


void GuiEngine::CatchallLocalJobResultAvailableSignalsHandler(QDBusMessage msg)
{
//    qDebug("GuiEngine::CatchallLocalJobResultAvailableSignalsHandler");

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

    // Connect the AskForOutcome signal receiver
    QDBusConnection bus = QDBusConnection ::sessionBus();
    if (!bus.connect(PBBusName,\
                     NULL,\
                     PBInterfaceName,\
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

    // get the job-list: NB: From the SessionState this time
    m_job_list = SessionStateJobList(m_session);

    // to get only the *jobs* that are designated by the whitelist.
    m_desired_job_list = GenerateDesiredJobList(m_job_list);

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

    // Repopulate our knowledge of PlainBox
    RefreshPBObjects();

    // we should emit a signal to say its all done
    emit localJobsCompleted();

    // qDebug("GuiEngine::CatchallLocalJobResultAvailableSignalsHandler - Done");

}

void GuiEngine::CatchallJobResultAvailableSignalsHandler(QDBusMessage msg)
{
//    qDebug("GuiEngine::CatchallJobResultAvailableSignalsHandler");

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

    // Update the GUI so it knows what the job outcome was
    emit updateGuiObjects(m_run_list.at(m_current_job_index).path(), \
                          m_current_job_index, \
                          outcome);

    // Move to the next job
    m_current_job_index++;

    // We should deal with Pause/Resume here
    if (!m_running) {

        // Dont start the next job
        return;
    }

    if (m_run_list.count() != m_current_job_index) {

        // Update the GUI so it knows what job is starting
        emit updateGuiObjects(m_run_list.at(m_current_job_index).path(), \
                              m_current_job_index, \
                              PBTreeNode::PBJobResult_Running);

        // Now run the next job
        qDebug() << "Running Job " << JobNameFromObjectPath(m_run_list.at(m_current_job_index));

        RunJob(m_session,m_run_list.at(m_current_job_index));

        return;
    }

    // Tell the GUI its all finished
    emit jobsCompleted();

//    qDebug("GuiEngine::CatchallJobResultAvailableSignalsHandler - Done");
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

void GuiEngine::ManualTest(const int outcome)
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

QString GuiEngine::GetSaveFileName(void)
{
    QString prompt = "Choose a filename:";

    return QFileDialog::getSaveFileName(NULL,prompt, "submission.xml", tr("XML files (*.xml)"));
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
    return GetIOLogFromJobPath(opath);;
}
