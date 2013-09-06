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

 #ifndef PLAINBOX_GUI_H
 #define PLAINBOX_GUI_H

#include <QtQml/qqml.h>
#include <QtQml/QQmlExtensionPlugin>
#include <QtDBus/QtDBus>
#include <QtXml/QDomDocument>

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

        /* Signal receivers from Plainbox
         */
        void InterfacesAdded(QDBusMessage msg);
        void InterfacesRemoved(QDBusMessage msg);

        void CatchallAskForOutcomeSignalsHandler(QDBusMessage msg);
        void CatchallIOLogGeneratedSignalsHandler(QDBusMessage msg);
        void CatchallLocalJobResultAvailableSignalsHandler(QDBusMessage msg);
        void CatchallJobResultAvailableSignalsHandler(QDBusMessage msg);
        /* Helper functions for logging and testing
         */

        // Logging function
        void dump_whitelist_selection(void);

        // Used by the test program test-gui-engine
        void AcknowledgeJobsDone(void);
        void AcknowledgeLocalJobsDone(void);
        void ManualTest(const int outcome);

        // Returns a list of DBus Object Paths for valid tests
        const QList<QDBusObjectPath>& GetValidRunList(void);

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

        const QString GetIOLog(const QString& job);

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

signals:
        // Instruct the GUI to update itself
        void updateGuiObjects(const QString& job_id, \
                              const int current_job_index,
                              const int outcome);
        void localJobsCompleted(void);
        void jobsCompleted(void);

        void raiseManualInteractionDialog(const int outcome /* from PB */);

        void updateManualInteractionDialog(const int outcome);

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

        QList<QDBusObjectPath> GetLocalJobs(void);

        QList<QDBusObjectPath> GetAllJobs(void);


        // SessionState methods
        // GetEstimatedDuration - todo if needed

        QStringList UpdateDesiredJobList(const QDBusObjectPath session, \
                                         QList<QDBusObjectPath> desired_job_list);

        // SessionState Properties
        QList<QDBusObjectPath> SessionStateRunList(const QDBusObjectPath session);
        QList<QDBusObjectPath> SessionStateJobList(const QDBusObjectPath session);

        void UpdateJobResult(const QDBusObjectPath session, \
                                        const QDBusObjectPath &job_path, \
                                        const QDBusObjectPath &result_path);

        // JobRunner Methods
        void RunCommand(const QDBusObjectPath& runner);
        void SetOutcome(const QDBusObjectPath& runner, \
                        const QString& outcome, \
                        const QString& comments);

        // Job Properties
        QString GetCommand(const QDBusObjectPath& opath);

        // Service Methods
        void RunJob(const QDBusObjectPath session, const QDBusObjectPath opath);

        // Convenience functions
        int GetOutcomeFromJobResultPath(const QDBusObjectPath &opath);
        const QString GetIOLogFromJobPath(const QDBusObjectPath &opath);

        const QString ConvertOutcome(const int outcome);

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

        // The currently running job as an index into m_run_list
        int m_current_job_index;

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

        // Used to preserve interim data from Manual Interaction event
        QDBusObjectPath m_runner;

        /* lets us choose whether to raise the manual interaction dialog
        * or simply update it
        */
        bool m_running_manual_job;

// Used by the test program
protected:
        bool m_local_jobs_done;

        bool m_jobs_done;

        bool m_testing_manual_job;
};

 #endif
