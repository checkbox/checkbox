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

/* Decoding for the org.freedesktop.Dbus.ObjectManager
 *
 * Structs useful to the GUI for extraction and display purposes
 *
 * Ultimately we must decode this DBus Signature
 * "a{oa{sa{sv}}}
 *
 * So, starting with the inner most, we can say that:
 *   a{sv} = QString, QDBusVariant = om_smalldict
 *
 * Then, we will have
 *
 * a{sa{sv}} = QMap<QString,QVariantMap> = om_innerdict
 *
 * Finally, we want this:
 *
 * a{oa{sa{sv}}} = QMap<QString,innerdict> = outerdict
 */
typedef QMap<QString,QDBusVariant> om_smalldict;
typedef QMap<QString,om_smalldict> om_innerdict;
typedef QMap<QDBusObjectPath,om_innerdict> om_outerdict;

// now register these metatypes
Q_DECLARE_METATYPE(om_smalldict);
Q_DECLARE_METATYPE(om_innerdict);
Q_DECLARE_METATYPE(om_outerdict);

/* We need a new metatype for passing to plainbox CreateSession()
 *
 * Basically, an array of DBus Object Paths
 */
typedef QList<QDBusObjectPath> opath_array_t;

Q_DECLARE_METATYPE(opath_array_t);

/* Dbus specification standard interface names - they dont appear to be defined
 * by Qt DBus system.
 */

static const QString ofDObjectManagerName("org.freedesktop.DBus.ObjectManager");
static const QString ofDIntrospectableName("org.freedesktop.DBus.Introspectable");
static const QString ofDPropertiesName("org.freedesktop.DBus.Properties");

/* The names for Plainbox top-level DBus structures.
 */
static const QString PBBusName("com.canonical.certification.PlainBox");
static const QString PBObjectPathName("/plainbox/service1");
static const QString PBInterfaceName("com.canonical.certification.PlainBox.Service1");

// Whitelist interfaces
static const QString PBWhiteListInterface("com.canonical.certification.PlainBox.WhiteList1");

// Session Interfaces
static const QString PBSessionStateInterface("com.canonical.certification.PlainBox.Session1");

// Well-known Plainbox/Checkbox Job Interfaces
static const QString PlainboxJobDefinition1("com.canonical.certification.PlainBox.JobDefinition1");
static const QString CheckBoxJobDefinition1("com.canonical.certification.CheckBox.JobDefinition1");

/* Represents a DBus Object Interface. We only need the properties as the
 * methods are only of a few fixed types we already know.
 */
class PBObjectInterface
{
public:
    PBObjectInterface(QString interface, QVariantMap properties)
        : interface(interface), properties(properties)
    {

    };

    ~PBObjectInterface() { /* nothing to do */};

public:
    QString interface;
    // Methods - not clear what if anything needs to be stored for these?
    QVariantMap properties;
};

/* This enables us to build a tree of Plainbox objects. This is the tree
 * as seen by introspecting the object hierarchy over DBus. We do this
 * by recursively introspecting the tree over DBus
 */
class PBTreeNode
{
public:
    PBTreeNode();

    ~PBTreeNode();

    PBTreeNode* AddNode(PBTreeNode* parentNode, \
                        const QDBusObjectPath &object_path);

    // Should be a utility function?
    QVariantMap GetObjectProperties(const QDBusObjectPath &object_path, \
                                    const QString interface);

    // Should be a utility function?
    const QString GetIntrospectXml(const QDBusObjectPath &object_path);

    // Returns the Node identified by via
    static PBTreeNode* FindJobNode(const QString via, QList<PBTreeNode*> jobnodes);

    // Convenience functions, returns the relevant property
    const QString via(void);
    const QString id(void);
    const QString name(void);

public:
    PBTreeNode *parent;

    QDBusObjectPath object_path;
    om_outerdict managed_objects;
    QList<PBTreeNode*> children;
    QDomDocument* introspection;
    QString xmlstring;  // the raw xml of introspection

    QList<PBObjectInterface*> interfaces;
};

// We need a tree to represent the derived hierarchy of job dependencies
class JobTreeNode
{
public:
    JobTreeNode();
    ~JobTreeNode();

    JobTreeNode* AddNode(JobTreeNode* jtnode, QList<PBTreeNode*> chain);

    void Flatten(JobTreeNode* jnode, QList<JobTreeNode*> &list);

public:
    JobTreeNode* parent;
    QString m_via;
    PBTreeNode* m_node;
    QList<JobTreeNode*> m_children;

    // convenience for the displaymodel- how deep is this node
    int m_depth;
    QString m_name; // human readable name
    QString m_id;   // the id string from /plainbox/job/id

};

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
        // Manage GuiEngine lifetime
        bool Initialise(void);
        bool Shutdown(void);

        // update object tree based on callbacks from plainbox/dbus
        void InterfacesAdded(QDBusMessage msg);
        void InterfacesRemoved(QDBusMessage msg);

        // Handle to the tree of PlainBox objects
        const PBTreeNode* GetPlainBoxObjects(void);

        // temporary
        void dump_whitelist_selection(void);

        // temporary function to run the "local" jobs generators
        void RunLocalJobs(void);

        // temporary function for debug purposes
        void LogDumpTree(void);

signals:
        // Instruct the GUI to update itself
        void UpdateGuiObjects(void);

public:
        // Temporary public functions
        const PBTreeNode* GetRootJobsNode(const PBTreeNode *node);
        const PBTreeNode* GetRootWhiteListNode(const PBTreeNode *node);

        QList<PBTreeNode*> GetJobNodes(void);
        QList<PBTreeNode*> GetWhiteListNodes(void);

        // Returns whitelist object path, whitelist name
        QMap<QDBusObjectPath,QString> GetWhiteListPathsAndNames(void);

        void SetWhiteList(const QDBusObjectPath opath, const bool check);

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

        // UpdateJobResult - todo

        // Service Methods
        void RunJob(const QDBusObjectPath session, const QDBusObjectPath opath);

        // Returns a tree of all the jobs
        JobTreeNode* GetJobTreeNodes();

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
};

 #endif
