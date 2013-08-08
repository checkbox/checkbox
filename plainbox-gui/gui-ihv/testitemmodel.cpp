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

#include "testitemmodel.h"




// Factory class to create or update a TestItem Model
ListModel* TestItemModel::CreateTestListModel(ListModel* model)
{
    // Create a model
    qDebug("TestItemModel::CreateTestListModel()");

    // We can create OR update the model
    if (model==NULL) {
        qDebug("Creating fresh TestItemModel");
        model = new ListModel(new TestItem, qApp);
    } else {
        qDebug("Recreating TestItemModel");
        model->clear();
    }

    // We should interrogate the whitelist here
    const QString engname("");

    GuiEngine* myengine = qApp->findChild<GuiEngine*>(engname);
    if(myengine == NULL) {
        qDebug("Cant find guiengine object");

        // NB: Model will be empty at this point
        return model;
    }

    // Get all of the jobs here
    QList<PBTreeNode*> jobnodes = myengine->GetJobNodes();

    // Need to flatten the tree in the right order here
    JobTreeNode* jt_top = myengine->GetJobTreeNodes();

    if (!jt_top) {
        qDebug("no valid JobTree");
        return NULL;
    }

    QList<JobTreeNode*> flatnodes;

    flatnodes.clear();

    jt_top->Flatten(jt_top,flatnodes);

    // dont forget the "first" node is our internal one
    flatnodes.removeFirst();

    QList<JobTreeNode*>::iterator iter = flatnodes.begin();

    while(iter != flatnodes.end()) {

        PBObjectInterface* iface = NULL;

        JobTreeNode* jnode = *iter;
        if (jnode == NULL) {
            qDebug("We ran out of known nodes!");
            break;
        }

        if (jnode->m_node == NULL) {
            qDebug("must be the top node again");
        }

        PBTreeNode* node = jnode->m_node;
        // is this a valid item for the user?
        QList<QDBusObjectPath> list;

        list.append(node->object_path);

        // check against our filtered list
        QList<QDBusObjectPath> short_valid_list = \
                JobTreeNode::FilteredJobs(list,\
                                       myengine->GetValidRunList());

        if (myengine->GetValidRunList().count() != 0) {
            // we have _some_ valid tests :)
            if (short_valid_list.isEmpty()) {
                // we dont show this one
                iter++;
                continue;
            }
        }

        double duration;
        QString checksum;
        QString depends;
        QString testname;
        QString requires;
        QString description;
        QString command;
        QString environ;
        QString type = "Manual"; // translation required
        QString user;
        QString via;
        QString group;
        bool check;
        QString path;

        QList<QString> parent_names;
        QList<QString> parent_ids;

        // Fill in the parent names
        JobTreeNode* temp = jnode->parent;

        while (temp != jt_top) {
            parent_names.prepend(temp->m_name);

            temp = temp->parent;
        }

        // Fill in the parent ids
        temp = jnode->parent;

        while (temp != jt_top) {
           parent_ids.prepend(temp->m_id);

           temp = temp->parent;
        }

        // Should we show this to the usr at all?
        bool human = true;

        // Local jobs use description as the visible name
        bool description_as_name = false;

        for(int j=0; j < node->interfaces.count(); j++) {

            iface = node->interfaces.at(j);

            if (iface == NULL) {
                qDebug("Null interface");
            } else {
                if(iface->interface.compare(PlainboxJobDefinition1) == 0) {
                    QVariant variant;

                    variant = *iface->properties.find("estimated_duration");
                    if (variant.isValid() && variant.canConvert(QMetaType::Double)) {
                        duration = variant.toDouble();
                    }

                    variant = *iface->properties.find("checksum");
                    if (variant.isValid() && variant.canConvert(QMetaType::QString)) {
                        checksum = variant.toString();
                    }

                    variant = *iface->properties.find("depends");
                    if (variant.isValid() && variant.canConvert(QMetaType::QString)) {
                        depends = variant.toString();
                    }
                    variant = *iface->properties.find("description");
                    if (variant.isValid() && variant.canConvert(QMetaType::QString)) {
                        description = variant.toString();
                    }

                    variant = *iface->properties.find("name");
                    if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                        testname = variant.toString();
                    }

                    variant = *iface->properties.find("requires");
                    if (variant.isValid() && variant.canConvert(QMetaType::QString)) {
                        requires = variant.toString();
                    }
                }

                if(iface->interface.compare(CheckBoxJobDefinition1) == 0) {
                    QVariant variant;
                    variant = *iface->properties.find("plugin");

                    if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                        // show plugin type
                        QString plugin = "shell";

                        if (plugin.compare(variant.toString())) {
                            type = "Automatic"; // translation required
                        }

                        if (variant.toString().compare("local") == 0) {
                            description_as_name = true;
                        }

                        if (variant.toString().compare("resource") == 0) {
                            human = false;
                        }

                    }

                    variant = *iface->properties.find("via");
                    if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                        via = variant.toString();
                    }
                }
            }
        }

        // this will signal how far indented this item is
        int depth = 0;
        for (int i=0;i<parent_ids.count();i++) {

            depth++;
        }

        // For local jobs, we may substitute the description for the human name
        if (description_as_name) {
            // dont do this if the description is empty however!
            if (!description.isEmpty()) {
                testname = description;
            }
        }

        // Does this node have children?
        bool branch = true;
        if (jnode->m_children.isEmpty()) {
            branch = false;
        }

        // Is this to be shown to the user?
        if (human) {
            model->appendRow(new TestItem(duration, \
                                          checksum, \
                                          depends, \
                                          testname, \
                                          requires, \
                                          description, \
                                          command, \
                                          environ, \
                                          type, \
                                          user, \
                                          group, \
                                          via, \
                                          check, \
                                          path, \
                                          parent_names, \
                                          parent_ids, \
                                          depth, \
                                          branch, \
                                          model));
        }

        iter++;
    }

    qDebug("TestItemModel::CreateTestListModel() - done");

    return model;
}
