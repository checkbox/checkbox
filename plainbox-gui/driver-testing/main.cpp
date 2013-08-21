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

#include <QtWidgets/QApplication>
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
#include "testitemmodel.h"

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
ListModel* CreateTestListModel(ListModel* model=NULL )
{
    qDebug("CreateTestListModel()");

    TestItemModel factory;

    return factory.CreateTestListModel(model);
}

int main(int argc, char *argv[])
{
     QApplication app(argc, argv);

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

    // create a factory object to give us our test model
    TestItemModel testitemFactory;

    viewer.rootContext()->setContextProperty("testitemFactory",&testitemFactory);

    // Now, load the main page
    viewer.setMainQmlFile(QStringLiteral("qml/driver-testing.qml"));

    // Ensure a reasonable minimum size for this window
    viewer.setMinimumSize(QSize(800,600));

    viewer.showExpanded();

    return app.exec();
}
