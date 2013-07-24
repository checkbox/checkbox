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

// Plainbox tree node class
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
const QString PBTreeNode::GetIntrospectXml(const QDBusObjectPath &object_path)
{
    // Connect to the introspectable interface
    QDBusInterface iface(PBBusName, \
                         object_path.path(), \
                         ofDIntrospectableName, \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug("Could not connect to introspectable interface");
        return NULL;
    }

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
QVariantMap PBTreeNode::GetObjectProperties(const QDBusObjectPath &object_path, \
                                            const QString interface)
{
    QVariantMap properties;

    // Connect to the freedesktop Properties interface
    QDBusInterface iface(PBBusName, \
                         object_path.path(), \
                         "org.freedesktop.DBus.Properties", \
                         QDBusConnection::sessionBus());
    if (!iface.isValid()) {
        qDebug("Could not connect to properties interface");
        return properties;
    }

    // GetAll properties
    QDBusMessage reply = iface.call("GetAll",interface);
    if (reply.type() != QDBusMessage::ReplyMessage) {
        qDebug("Could not get the properties");
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

PBTreeNode::~PBTreeNode()
{
    if (children.count()) {

        QList<PBTreeNode*>::iterator p;

        children.erase(children.begin(),children.end());
    }
}

void GuiEnginePlugin::registerTypes(const char *uri)
{
    // register our classes
    qmlRegisterType<GuiEngine>(uri,1,0,"GuiEngine");
}

GuiEngine::GuiEngine( QObject*parent ) : QObject(parent)
{
    qDebug("GuiEngine::GuiEngine");

    enginestate = UNINITIALISED;
    pb_objects=NULL;
    valid_pb_objects = false;

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

        // Obtain the initial tree of Plainbox objects, starting at the root "/"
        pb_objects = new PBTreeNode();
        pb_objects->AddNode(pb_objects, QDBusObjectPath("/"));
        if (!pb_objects) {
            qDebug("Failed to get Plainbox Objects");

            return false;
        }

        // Connect our change receivers
        QDBusConnection bus = QDBusConnection ::sessionBus();

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
const PBTreeNode* GuiEngine::GetPlainBoxObjects()
{
    return pb_objects;
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
    emit UpdateGuiObjects();

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
    emit UpdateGuiObjects();

    qDebug("GuiEngine::InterfacesRemoved - done");
}
QList<PBTreeNode*> GuiEngine::GetJobNodes(void)
{
    qDebug("GuiEngine::GetJobNodes()");

    QList<PBTreeNode*> jobnodes;

    PBTreeNode* jobnode = const_cast<PBTreeNode*>(GetRootJobsNode(GetPlainBoxObjects()));
    if (!jobnode) {
        return jobnodes;
    }

    QList<PBTreeNode*>::const_iterator iter =jobnode->children.begin();

    while(iter != jobnode->children.end()) {

        PBTreeNode* child = *iter;

         jobnodes.append(child);

         iter++;
    }

    qDebug("GuiEngine::GetJobNodes() - done");

    return jobnodes;
}
QList<PBTreeNode*> GuiEngine::GetWhiteListNodes(void)
{
    qDebug("GuiEngine::GetWhiteListNodes()");

    QList<PBTreeNode*> whitelistnodes;

    PBTreeNode* whitelistnode = const_cast<PBTreeNode*>(GetRootWhiteListNode(GetPlainBoxObjects()));
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
            const_cast<PBTreeNode*>(GetRootWhiteListNode(GetPlainBoxObjects()));
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

// temporary helper
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
