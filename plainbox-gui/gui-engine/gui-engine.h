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

        /* Run all the jobs of type "local" in order to generate the true
         * list of tests from which the user can select.
         */
        void RunLocalJobs(void);

        /* Signal receivers from Plainbox
         */

        void JobResultAvailable(QDBusMessage msg);

        void InterfacesAdded(QDBusMessage msg);
        void InterfacesRemoved(QDBusMessage msg);

        /* Helper functions for logging and testing
         */

        // Logging function
        void dump_whitelist_selection(void);

        // Used by the test program test-gui-engine
        void AcknowledgeJobsDone(void);

public:
        // Returns a list of all the jobnodes
        QList<PBTreeNode*> GetJobNodes(void);

        // Returns a tree of all the jobs
        JobTreeNode* GetJobTreeNodes();

        // Returns a list of DBus Object Paths for valid tests
        const QList<QDBusObjectPath>& GetValidRunList(void) {
            return valid_run_list;
        }

signals:
        // Instruct the GUI to update itself
        void UpdateGuiObjects(void);
        void localJobsCompleted(void);

private:
        // Helper function when generating the desired local and real jobs
        QList<QDBusObjectPath> GenerateDesiredJobList(QList<QDBusObjectPath> job_list);

        // Temporary public functions
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

        // Service Methods
        void RunJob(const QDBusObjectPath session, const QDBusObjectPath opath);

        // Debugging tool
        const QString JobNameFromObjectPath(const QDBusObjectPath& opath);

private:
        EngineState enginestate;

        // Contains our Tree of Plainbox objects (Methods, results, tests etc)
        PBTreeNode* pb_objects;

        // Have we got valid tree of PlainBox objects?
        bool valid_pb_objects;

        // These may go later, but are helpful for now

        // A list of the selected whitelists from the user
        QMap<QDBusObjectPath, bool> whitelist;

        // A user-selected list of tests. We store the object path
        QMap<QDBusObjectPath, bool> tests;

        // All the jobs which are valid to be chosen by the user
        QList<QDBusObjectPath> valid_run_list;

        // All the jobs ultimately selected by the user
        QList<QDBusObjectPath> final_run_list;

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

// Used by the test program
protected:
        bool m_local_jobs_done;
};

 #endif
