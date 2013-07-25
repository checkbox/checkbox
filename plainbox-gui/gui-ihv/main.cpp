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

#include <QtGui/QGuiApplication>
#include <QPluginLoader>
#include <QQmlExtensionPlugin>
#include <QDir>
#include <QtQml>
#include "qtquick2applicationviewer.h"
#include "commandtool.h"
#include "listmodel.h"
#include "whitelistitem.h"
#include "testitem.h"

#include "../gui-engine/gui-engine.h"

// Load up test suites here (it can be moved to another file)
ListModel* CreateWhiteListModel()
{
    qDebug("CreateWhiteListModel()");

    ListModel *model = new ListModel(new WhiteListItem, qApp);

    const QString engname("");

    GuiEngine* myengine = qApp->findChild<GuiEngine*>(engname);
    if(myengine == NULL) {
        qDebug("Cant find guiengine object");

        // NB: Model will be empty at this point
        return model;
    }

    QMap<QDBusObjectPath,QString> paths_and_names = \
            myengine->GetWhiteListPathsAndNames();

    QMap<QDBusObjectPath,QString>::const_iterator iter = paths_and_names.begin();

    while(iter != paths_and_names.end() ) {

        qDebug() << iter.key().path();

        qDebug() << " Name: " << iter.value();

        model->appendRow(new WhiteListItem(iter.value(), \
                                           iter.key().path(), \
                                           model));
        iter++;
    }

    qDebug("CreateWhiteListModel() - Done");

    return model;
}

// Load up test suites here (it can be moved to another file)
ListModel* CreateTestListModel()
{
    qDebug("CreateTestListModel()");

    ListModel *model = new ListModel(new TestItem, qApp);

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

    for (int i = 0; i< jobnodes.count(); i++) {
        PBObjectInterface* iface = NULL;

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
        QString group;
        bool check;
        QString path;

        for(int j=0; j < jobnodes.at(i)->interfaces.count(); j++) {
            iface = jobnodes.at(i)->interfaces.at(j);

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
                    }
                }
            }
        }

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
                                      check, \
                                      path, \
                                      model));
    }

    qDebug("CreateTestListModel() - done");

    return model;
}

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    qmlRegisterType<WhiteListItem>("Ubuntu.IhvTest", 0, 1, "WhiteListItem");
    qmlRegisterType<TestItem>("Ubuntu.IhvTest", 0, 1, "TestItem");

    QDir pluginsDir;
    pluginsDir.setPath("../plugins");

    QPluginLoader loader("../plugins/libgui-engine.so");

    QQmlExtensionPlugin *plugin = qobject_cast<QQmlExtensionPlugin*>(loader.instance());
    if (plugin)
        plugin->registerTypes("GuiEngine");

    // Create our GuiEngine and hang it on QGuiApplication
    GuiEngine guiengine((QObject*)&app);

    // Initialise - connect to Plainbox
    guiengine.Initialise();

    QtQuick2ApplicationViewer viewer;

    // WhiteList/Suite
    ListModel* whitelistmodel = CreateWhiteListModel();
    if (!whitelistmodel) {
        qDebug("Cannot create whitelist model");
        exit(1);
    }

    /* The test list model needs to be further updated by running all the "local"
	 jobs. But this is not yet ready.
     */
    ListModel* testlistmodel = CreateTestListModel();
    if (!testlistmodel) {
        qDebug("Cannot create Test List Model");
        exit(1);
    }

    viewer.rootContext()->setContextProperty("whiteListModel", whitelistmodel);

    // List of Tests
    viewer.rootContext()->setContextProperty("testListModel", testlistmodel);

    CommandTool cmdTool;
    viewer.rootContext()->setContextProperty("cmdTool", &cmdTool);

    // GuiEngine
    viewer.rootContext()->setContextProperty("guiEngine", &guiengine);

    // Now, load the main page
    viewer.setMainQmlFile(QStringLiteral("qml/outline/gui-ihv.qml"));
    viewer.showExpanded();

    return app.exec();
}
