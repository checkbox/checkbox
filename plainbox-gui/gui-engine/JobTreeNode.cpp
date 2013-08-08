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

#include "JobTreeNode.h"

// Ctor
JobTreeNode::JobTreeNode()
{
    parent = NULL;
    m_via = "";
    m_node = NULL;
    m_children.clear();
    m_depth = 0;
}

// Dtor
JobTreeNode::~JobTreeNode()
{
    for(int i=0;i<m_children.count();i++) {
        delete m_children.at(i);
    }
}

JobTreeNode* JobTreeNode::AddNode(JobTreeNode *jtnode, QList<PBTreeNode*> chain)
{
    //Do we have sensible arguments?
    if (!jtnode) {
        qDebug("There is no node");
        return NULL;
    }

    if (chain.empty()) {
        qDebug("There is no more chain to follow");
        return NULL;
    }

    // Chain is an ordered list from top to bottom of our tree nodes

    // Look for each chain element in turn, adding if needed
    QList<PBTreeNode*> local_chain = chain;

    // can we find this in our children?
    QList<JobTreeNode*>::iterator iter = jtnode->m_children.begin();

    // go through in turn
    while(iter != jtnode->m_children.end()) {

        // Is this the front of the chain?
        JobTreeNode* node = *iter;

        if (node->m_node == local_chain.first()) {
            // ok, found it. now, is it the only element in the chain?

            // follow it down I guess
            local_chain.removeFirst();

            if (!local_chain.empty()) {
                return AddNode(node,local_chain);
            } else {
                /* we must have added this previously in order to
                 * add a child element. As this is a leaf element,
                 * there is nothing left to do but return.
                 */
                return NULL;
            }
        }

        // round the loop
        iter++;
    }

    // If we get here, we've not found this element in the tree at this level,
    // so we shall add it
    JobTreeNode* jt_new = new JobTreeNode();

    jt_new->parent = jtnode;
    jt_new->m_node = local_chain.first();
    jt_new->m_name = local_chain.first()->name();
    jt_new->m_id = local_chain.first()->id();
    jt_new->m_via = local_chain.first()->via();

    // Trim this item now we have stored it
    local_chain.removeFirst();

    jtnode->m_children.append(jt_new);

    // Are there any more elements?
    if (!local_chain.empty()) {
        // Yep, we need to go down to the next level again
        return AddNode(jt_new,local_chain);
    }

    return NULL;
}

// We just recursively add ourselves to the list
void JobTreeNode::Flatten(JobTreeNode* jnode, QList<JobTreeNode*> &list)
{
    list.append(jnode);

    for(int i=0; i < jnode->m_children.count() ;i++) {
        Flatten(jnode->m_children.at(i),list);
    }
}

