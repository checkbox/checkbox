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

#include "PBTreeNode.h"

// Ctor
PBTreeNode::PBTreeNode()
{
    parent = NULL;
    object_path.path().clear();
    managed_objects.clear();
    children.clear();
    introspection = NULL;
    xmlstring.clear();
    interfaces.clear();
}

// Dtor
PBTreeNode::~PBTreeNode()
{
    if (introspection) {
        delete introspection;
    }

    // delete the interfaces
    if (interfaces.count()) {
        QList<PBObjectInterface*>::iterator iter = interfaces.begin();

        while(iter != interfaces.end()) {
            delete *iter;

            iter++;
        }
    }

    interfaces.erase(interfaces.begin(),interfaces.end());

    if (children.count()) {

        QList<PBTreeNode*>::iterator iter = children.begin();

        while (iter != children.end()) {
            delete *iter;

            iter++;
        }

        children.erase(children.begin(),children.end());
    }
}

/* Add a new PBTreeNode based upon the supplied DBus object_path
 */
PBTreeNode* PBTreeNode::AddNode(PBTreeNode* parentNode, \
                                const QDBusObjectPath &object_path)
{
    PBTreeNode* pbtn = NULL;

    // special case for the root node
    if(parentNode->object_path.path().isNull()) {
        // We ARE the parentNode this time
        pbtn = parentNode;
    }
    else {
        pbtn = new PBTreeNode();
    }

    pbtn->object_path = object_path;
    pbtn->parent=parentNode;

    // The introspected string describing this object
    const QString intro_xml = GetIntrospectXml(object_path);

    pbtn->introspection=new QDomDocument(intro_xml);
    pbtn->xmlstring = intro_xml;

    /* We fill in all the children.
     *
     * We do this by creating a new child node for each node in intro_xml,
     * and then introspecting these child nodes until we get nothing more
     */
    QDomDocument doc;
    doc.setContent(intro_xml);
    QDomElement xmlnode=doc.documentElement();
    QDomElement child=xmlnode.firstChildElement();
    while(!child.isNull()) {

        // Is this a node?
        if (child.tagName() == "node") {
            // Yes, so we should introspect that as well
            QString child_path;

            if (object_path.path() == "/") {
                child_path = object_path.path() + child.attribute("name");
            } else {
                child_path = object_path.path() + "/" + child.attribute("name");
            }

            QDBusObjectPath child_object_path(child_path);

            PBTreeNode* node = AddNode(pbtn,child_object_path);
            if (node) {
                pbtn->children.append(node);
            }
        }

        // Is this an interface?
        if (child.tagName() == "interface") {
            QString iface_name = child.attribute("name");

            // we dont need properties from freedesktop interfaces
            if (iface_name != ofDIntrospectableName && \
                    iface_name != ofDPropertiesName) {

                QVariantMap properties;

                properties = GetObjectProperties(object_path, iface_name);

                if (!properties.empty()) {
                    PBObjectInterface *iface = \
                            new PBObjectInterface(iface_name,properties);

                    pbtn->interfaces.append(iface);
                }
            }
        }
        child = child.nextSiblingElement();
    }

    return pbtn;
}

QVariantMap PBTreeNode::GetObjectProperties(const QDBusObjectPath &object_path, \
                                            const QString interface)
{
    QVariantMap properties;

    // Connect to the freedesktop Properties interface
    QDBusInterface iface(PBBusName, \
                         object_path.path(), \
                         ofDPropertiesName, \
                         QDBusConnection::sessionBus());

    // GetAll properties
    QDBusMessage reply = iface.call("GetAll",interface);
    if (reply.type() != QDBusMessage::ReplyMessage) {
        // not worth complaining if they dont have properties, just return the empty
        return properties;
    }

    QList<QVariant> args = reply.arguments();

    if (args.empty()) {
        return properties;
    }

    QList<QVariant>::iterator p = args.begin();

    QVariant variant = *p;

    const QDBusArgument qda = variant.value<QDBusArgument>();

    qda >> properties;

    return properties;
}

const QString PBTreeNode::GetIntrospectXml(const QDBusObjectPath &object_path)
{
    // Connect to the introspectable interface
    QDBusInterface iface(PBBusName, \
                         object_path.path(), \
                         ofDIntrospectableName, \
                         QDBusConnection::sessionBus());

    // Lets see what we have - introspect this first
    QDBusMessage reply = iface.call("Introspect");
    if (reply.type() != QDBusMessage::ReplyMessage) {
        qDebug("Could not introspect this object");
        return NULL;
    }

    QList<QVariant> args = reply.arguments();

    QList<QVariant>::iterator iter = args.begin();

    QVariant variant = *iter;

    // The introspected string describing this object
    const QString intro_xml = variant.value<QString>();

    return intro_xml;
}

PBTreeNode* PBTreeNode::FindJobNode(const QString via, QList<PBTreeNode*> jobnodes)
{
    // construct the object path
    QString target = "/plainbox/job/" + via;

    QList<PBTreeNode*>::iterator iter = jobnodes.begin();

    while(iter != jobnodes.end()) {
        PBTreeNode* node = *iter;

        if (node->object_path.path().compare(target)==0) {
            return node;
        }

        iter++;
    }

    // Cant find such a job
    return NULL;
}

const QString PBTreeNode::via(void)
{
    for(int j=0; j < interfaces.count(); j++) {
        PBObjectInterface* iface = interfaces.at(j);

        if (iface == NULL) {
            qDebug("Null interface");
        } else {
            if(iface->interface.compare(CheckBoxJobDefinition1) == 0) {
                QVariant variant;
                variant = *iface->properties.find("via");
                if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                    return variant.toString();
                }
            }
        }
    }

    // There is no "via" so its a top level node
    return QString("");
}

const QString PBTreeNode::name(void)
{
    for(int j=0; j < interfaces.count(); j++) {
        PBObjectInterface* iface = interfaces.at(j);

        if (iface == NULL) {
            qDebug("Null interface");
        } else {
            if(iface->interface.compare(PlainboxJobDefinition1) == 0) {
                QVariant variant;
                variant = *iface->properties.find("name");
                if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                    return variant.toString();
                }
            }
        }
    }

    // No name - should this be flagged as an error in the tests themselves?
    return QString("");
}

const QString PBTreeNode::id(void)
{
    QStringList list = object_path.path().split("/");

    return list.last();
}

// TODO - These can be refactored quite easily
const QDBusObjectPath PBTreeNode::job(void)
{
    for(int j=0; j < interfaces.count(); j++) {
        PBObjectInterface* iface = interfaces.at(j);

        if (iface == NULL) {
            qDebug("Null interface");
        } else {
            if(iface->interface.compare(JobStateInterface) == 0) {
                QVariant variant;
                variant = *iface->properties.find("job");
                if (variant.isValid() ) {

                    QDBusObjectPath job = variant.value<QDBusObjectPath>();

                    return job;
                }
            }
        }
    }

    // No job - should this be flagged as an error in the tests themselves?
    qDebug("There is no job property");

    return QDBusObjectPath("");
}

const QDBusObjectPath PBTreeNode::result(void)
{
    for(int j=0; j < interfaces.count(); j++) {
        PBObjectInterface* iface = interfaces.at(j);

        if (iface == NULL) {
            qDebug("Null interface");
        } else {
            if(iface->interface.compare(JobStateInterface) == 0) {
                QVariant variant;
                variant = *iface->properties.find("result");
                if (variant.isValid() ) {

                    QDBusObjectPath result = variant.value<QDBusObjectPath>();

                    return result;
                }
            }
        }
    }

    // No name - should this be flagged as an error in the tests themselves?
    return QDBusObjectPath("");
}


const QString PBTreeNode::io_log(void)
{
    for(int j=0; j < interfaces.count(); j++) {
        PBObjectInterface* iface = interfaces.at(j);

        if (iface == NULL) {
            qDebug("Null interface");
        } else {
            if(iface->interface.compare(JobResultInterface) == 0) {
                QVariant variant;
                variant = *iface->properties.find("io_log");
                if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                    return variant.toString();
                }
            }
        }
    }

    // No name - should this be flagged as an error in the tests themselves?
    return QString("");
}


const QString PBTreeNode::comments(void)
{
    for(int j=0; j < interfaces.count(); j++) {
        PBObjectInterface* iface = interfaces.at(j);

        if (iface == NULL) {
            qDebug("Null interface");
        } else {
            if(iface->interface.compare(JobResultInterface) == 0) {
                QVariant variant;
                variant = *iface->properties.find("comments");
                if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                    return variant.toString();
                }
            }
        }
    }

    // No name - should this be flagged as an error in the tests themselves?
    return QString("");
}


const QString PBTreeNode::outcome(void)
{
    for(int j=0; j < interfaces.count(); j++) {
        PBObjectInterface* iface = interfaces.at(j);

        if (iface == NULL) {
            qDebug("Null interface");
        } else {
            if(iface->interface.compare(JobResultInterface) == 0) {
                QVariant variant;
                variant = *iface->properties.find("outcome");
                if (variant.isValid() && variant.canConvert(QMetaType::QString) ) {
                    return variant.toString();
                }
            }
        }
    }

    // No name - should this be flagged as an error in the tests themselves?
    return QString("");
}
