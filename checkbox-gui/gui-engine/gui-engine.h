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

 #ifndef PLAINBOX_GUI_H
 #define PLAINBOX_GUI_H

#include <QtQml/qqml.h>
#include <QtQml/QQmlExtensionPlugin>
#include <QtDBus/QtDBus>
#include <QtXml/QDomDocument>

#include "PBJsonUtils.h"

#include <QtWidgets/QFileDialog>

class GuiEnginePlugin : public QQmlExtensionPlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "guiengine")

public:

    // inherited from QQmlExtensionPlugin
    void registerTypes(const char *uri);
};

#include "PBTypes.h"
#include "PBNames.h"

#include "PBTreeNode.h"

#include "JobTreeNode.h"

// Currently used for the metadata Title of saved sessions in Plainbox
static const QString GUI_ENGINE_NAME_STR("GuiEngine");


/* We need to extract the signature of GetEstimatedDuration(): (dd) */
struct EstimatedDuration{
    double automated_duration;
    double manual_duration;
};

Q_DECLARE_METATYPE(EstimatedDuration);

/* This class embodies the wrapper which can call Plainbox APIs over D-Bus
 *
 * Its intended clients are Test Suite selection, test selection etc.
 *
 * There should only be one instance of this class
 */
class GuiEngine : public QObject
{
    Q_OBJECT

    private:
        enum EngineState {
        UNINITIALISED,
        READY
        };

public:
        GuiEngine( QObject*parent = 0);

public slots:

        /* Called by the QML/Qt GUI */

        // Manage GuiEngine lifetime
        bool Initialise(void);
        bool Shutdown(void);

        // Returns whitelist object path, whitelist name
        QMap<QDBusObjectPath,QString> GetWhiteListPathsAndNames(void);

        void SetWhiteList(const QDBusObjectPath opath, const bool check);

        void SetRealJobsList(const QList<QDBusObjectPath> &real_jobs) {
            m_final_run_list = real_jobs;
        }

        void SetRerunJobsList(const QList<QDBusObjectPath> &rerun_jobs) {
            m_rerun_list = rerun_jobs;
        }

        /* Run all the jobs of type "local" in order to generate the true
         * list of tests from which the user can select.
         */
        void RunLocalJobs(void);

        // Helper which prepares the corrected run-list from plainbox
        int PrepareJobs(void);

        void RunJobs(void);

        // Used when running the real tests
        void Pause(void);
        void Resume(void);

        // Session estimated duration
        QVariantMap GetEstimatedDuration();

        /* Signal receivers from Plainbox
         */
        void InterfacesAdded(QDBusMessage msg);
        void InterfacesRemoved(QDBusMessage msg);

        void CatchallShowInteractiveUISignalsHandler(QDBusMessage msg);
        void CatchallAskForOutcomeSignalsHandler(QDBusMessage msg);
        void CatchallIOLogGeneratedSignalsHandler(QDBusMessage msg);
        void CatchallLocalJobResultAvailableSignalsHandler(QDBusMessage msg);
        void CatchallJobResultAvailableSignalsHandler(QDBusMessage msg);
        /* Helper functions for logging and testing
         */

        // Used by the test program test-gui-engine
        void AcknowledgeJobsDone(void);
        void AcknowledgeLocalJobsDone(void);
        void ManualTest(const int outcome);

        // Returns a list of DBus Object Paths for valid tests
        const QList<QDBusObjectPath>& GetValidRunList(void);

        /* Returns a list of DBusObjectPaths representing tests
         * which are relevant for human beings (i.e. excludes resource jobs)
         */
        const QList<QDBusObjectPath>& GetVisibleRunList(void);

        /* Returns a list of DBusObjectPaths representing tests
         * which are relevant for human beings (i.e. excludes resource jobs)
         */
        void SetVisibleJobsList(const QList<QDBusObjectPath> &visible_jobs) {
            m_visible_run_list = visible_jobs;
        }

        // Useful for the progress bar in the run manager
        int ValidRunListCount(void);

        // Resume after dealing with Manual Interaction Dialog
        void ResumeFromManualInteractionDialog(bool run_test, \
                                               const QString outcome, \
                                               const QString comments);

        // Convenience functions for the GUI
        QString GuiExportSessionAsXML(void);
        QString GuiExportSessionAsHTML(void);

        bool GuiExportSessionToFileAsXML(const QString& output_file);
        bool GuiExportSessionToFileAsHTML(const QString& output_file);

        // Convenience until we move to Qt 5.1 and the FileDialog component
        QString GetSaveFileName(void);

        // Session management from the GUI
        void GuiSessionRemove(void);
        const QString GuiPreviousSessionFile(void);

        const QString GetIOLog(const QString& job);

        // Retrieve all the previous session data
        void GuiResumeSession(const bool re_run);
        void GuiCreateSession(void);

public:
        // Returns a list of all the jobnodes
        QList<PBTreeNode*> GetJobNodes(void);

        // Returns a tree of all the jobs
        JobTreeNode* GetJobTreeNodes();

        // Obtain The Results
        const QString ExportSession(const QDBusObjectPath session, \
                                    const QString& output_format, \
                                    const QStringList& option_list);


        const QString ExportSessionToFile(const QDBusObjectPath session, \
                                    const QString& output_format, \
                                    const QStringList& option_list,
                                    const QString& output_file);
        // Suspend and Resume Session
        void SessionPersistentSave(const QDBusObjectPath session);
        void SessionRemove(const QDBusObjectPath session);
        const QString PreviousSessionFile(const QDBusObjectPath session);

        // Ensure the RunManager view is updated with the recovered data
        void ResumeGetOutcomes(void);

signals:
        // Instruct the GUI to update itself
        void localJobsCompleted(void);

        // When starting a run of jobs
        void jobsBegin(void);

        void updateGuiBeginJob(const QString& job_id, \
                                const int current_job_index,
                                const QString& test_name);

        // When a job has completed
        void updateGuiEndJob(const QString& job_id, \
                              const int current_job_index,
                              const int outcome,
                              const QString& test_name);

        // When all jobs are completed
        void jobsCompleted(void);

        // Manual Interaction Dialog
        void raiseManualInteractionDialog(const int suggested_outcome /* from PB */, bool show_test);

        void updateManualInteractionDialog(const int suggested_outcome, bool show_test);

        void closeManualInteractionDialog(void);

private:
        // Helper function when generating the desired local and real jobs
        QList<QDBusObjectPath> GenerateDesiredJobList(QList<QDBusObjectPath> job_list);

        bool RefreshPBObjects(void);

        const PBTreeNode* GetRootJobsNode(const PBTreeNode *node);
        const PBTreeNode* GetRootWhiteListNode(const PBTreeNode *node);

        QList<PBTreeNode*> GetWhiteListNodes(void);

        bool WhiteListDesignates(const QDBusObjectPath white_opath, \
                                 const QDBusObjectPath job_opath);

        QDBusObjectPath CreateSession(QList<QDBusObjectPath> job_list);


        void ConnectJobReceivers(void);
        QList<QDBusObjectPath> GetLocalJobs(void);

        QList<QDBusObjectPath> GetAllJobs(void);


        // SessionState methods
        QStringList UpdateDesiredJobList(const QDBusObjectPath session, \
                                         QList<QDBusObjectPath> desired_job_list);

        void SessionResume(const QDBusObjectPath session);
        // SessionState Properties
        QList<QDBusObjectPath> SessionStateDesiredJobList(const QDBusObjectPath session);
        QList<QDBusObjectPath> SessionStateRunList(const QDBusObjectPath session);
        QList<QDBusObjectPath> SessionStateJobList(const QDBusObjectPath session);
        void SetSessionStateMetadata(const QDBusObjectPath session, \
                                     const QString& flags, \
                                     const QString& running_job_name, \
                                     const QString& title,
                                     const QByteArray& app_blob,
                                     const QString& app_id);

        const QVariantMap SessionStateMetadata(const QDBusObjectPath session);
        // Encode/decode of internal state of this class
        void EncodeGuiEngineStateAsJSON(void);
        void DecodeGuiEngineStateFromJSON(void);

        void UpdateJobResult(const QDBusObjectPath session, \
                                        const QDBusObjectPath &job_path, \
                                        const QDBusObjectPath &result_path);

        // JobRunner Methods
        void RunCommand(const QDBusObjectPath& runner);
        void SetOutcome(const QDBusObjectPath& runner, \
                        const QString& outcome, \
                        const QString& comments);

        /* A synthesised method. This is needed in the case of skipping tests
         * on resuming a session, since in this circumstance, there is no
         * runner object to serve as a means of setting the outcome.
         */
        QDBusObjectPath SetJobOutcome(const QDBusObjectPath& job_path, \
                                      const QString& outcome, \
                                      const QString& comments);

        bool JobCanStart(const QDBusObjectPath& job_path);
        const QString GetReadinessDescription(const QDBusObjectPath& job_path);

        // Job Properties
        QString GetCommand(const QDBusObjectPath& opath);

        // Service Methods
        void RunJob(const QDBusObjectPath session, const QDBusObjectPath opath);

        // Convenience functions
        int GetOutcomeFromJobResultPath(const QDBusObjectPath &opath);
        int GetOutcomeFromJobPath(const QDBusObjectPath &opath);
        const QString GetIOLogFromJobPath(const QDBusObjectPath &opath);

        const QString ConvertOutcome(const int outcome);

        // Find the next real job index to run based on current index through m_run_list
        int NextRunJobIndex(int index);

protected:  // for test purposes only
        // JobStateMap
        jsm_t GetJobStateMap(void);

        void GetJobStates(void);

        void GetJobResults(void);

        // Debugging tool
        const QString JobNameFromObjectPath(const QDBusObjectPath& opath);

        const QDBusObjectPath GetCurrentSession(void);

private:
        EngineState enginestate;

        /* Contains our Tree of Plainbox objects (Methods, results, tests etc)
         * Structure is as exposed on DBus.
         */
        PBTreeNode* pb_objects;

        // Have we got valid tree of PlainBox objects?
        bool valid_pb_objects;

        // These may go later, but are helpful for now

        // A list of the selected whitelists from the user
        QMap<QDBusObjectPath, bool> whitelist;

        // A user-selected list of tests. We store the object path
        QMap<QDBusObjectPath, bool> tests;

        // All the jobs ultimately selected by the user
        QList<QDBusObjectPath> m_final_run_list;

        // We only care about one session
        QDBusObjectPath m_session;

        // Job Tree as defined by the "via" properties
        JobTreeNode* job_tree;

        QList<QDBusObjectPath> m_job_list;

        QList<QDBusObjectPath> m_desired_job_list;

        QList<QDBusObjectPath> m_run_list;

        QList<QDBusObjectPath> m_local_job_list;

        QList<QDBusObjectPath> m_local_run_list;

        QList<QDBusObjectPath> m_desired_local_job_list;

        /* Re-run list. First time round it contains ALL m_run_list
         * but on subsequent rounds its only those selected by the user
         */
        QList<QDBusObjectPath> m_rerun_list;

        /* Visible job list; this is mainly for the benefit
         * of the gui, which needs to show real jobs being run,
         * together with local jobs used to group the real tests being
         * run.
         *
         * Its not ideal, just an interim solution. Ultimately,
         * it would be best to be able to populate the gui with a single
         * call to extract all the relevant data from the gui-engine.
         */
        QList<QDBusObjectPath> m_visible_run_list;

        // The currently running job as an index into m_run_list
        int m_current_job_index;

        // The current job path (for tests being run)
        QDBusObjectPath m_current_job_path;

        // Job State Map
        jsm_t m_jsm;

        // Job State List (NB: These are NOT in pb_objects!)
        QList<PBTreeNode*> m_job_state_list;

        /* Job Results. These could be either DiskJobResults or MemoryJobResults
         *
         * (NB: These are NOT in pb_objects!)
         */
        QList<PBTreeNode*> m_job_state_results;

        // Are we running tests or not? (Used for Pause/Resume)
        bool m_running;
        bool m_waiting_result;

        // Used to preserve interim data from Manual Interaction event
        QDBusObjectPath m_runner;

        /* lets us choose whether to raise the manual interaction dialog
        * or simply update it
        */
        bool m_running_manual_job;

        /* Records whether the results of running the tests have been submitted
        * Note that depending on the GUI, this may simply mean saved to disk,
        * or submitted to a validation website. it may not even matter. But this
        * is here in order to allow the state to be preserved by plainbox
        * in a saved session.
        */
        bool m_submitted;
// Used by the test program
protected:
        bool m_local_jobs_done;

        bool m_jobs_done;

        bool m_testing_manual_job;
};

 #endif
