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

#ifndef PBTREENODE_H
#define PBTREENODE_H

#include <QtQml/qqml.h>
#include <QtQml/QQmlExtensionPlugin>
#include <QtDBus/QtDBus>
#include <QtXml/QDomDocument>

#include "PBTypes.h"
#include "PBNames.h"

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

    // From JobState nodes
    const QDBusObjectPath job(void);
    const QDBusObjectPath result(void);

    // From JobResult nodes (either DiskJobResult or MemoryJobResult)
    const QString io_log(void); // note this can be very large
    const QString comments(void);
    const QString outcome(void);

    // Convenient enumeration of Job Results. We will use these in the GUI
    Q_ENUMS(PBJobResult);
    enum PBJobResult {
        PBJobResult_NotRun = 0,
        PBJobResult_Skip = 1,
        PBJobResult_Pass = 2,
        PBJobResult_Fail = 3,
        PBJobResult_Error = 4, // not clear what this means? log_viewer_with_trouble???
        PBJobResult_UserInteraction = 5, // May not make sense here
        PBJobResult_DepsNotMet = 6,  // We want to show jobs where deps are not met
        PBJobResult_Running = 7, // this test is being run right now
        PBJobResult_None = 8    // no outcome is set for this job yet
    };

public:
    PBTreeNode *parent;

    QDBusObjectPath object_path;
    om_outerdict managed_objects;
    QList<PBTreeNode*> children;
    QDomDocument* introspection;
    QString xmlstring;  // the raw xml of introspection

    QList<PBObjectInterface*> interfaces;
};

#endif // PBTREENODE_H
