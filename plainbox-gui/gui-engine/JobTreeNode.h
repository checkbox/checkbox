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

#ifndef JOBTREENODE_H
#define JOBTREENODE_H

#include "PBTreeNode.h"

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

#endif // JOBTREENODE_H
