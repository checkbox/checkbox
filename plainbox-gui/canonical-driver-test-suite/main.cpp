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
#include <QCoreApplication>
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
#include "WhiteListModelFactory.h"

#include "../gui-engine/gui-engine.h"

int main(int argc, char *argv[])
{
     QApplication app(argc, argv);
    qputenv("APP_ID", QFileInfo(QCoreApplication::applicationFilePath()).fileName().toUtf8());

    qmlRegisterType<WhiteListItem>("Ubuntu.IhvTest", 0, 1, "WhiteListItem");
    qmlRegisterType<TestItem>("Ubuntu.IhvTest", 0, 1, "TestItem");

    QtQuick2ApplicationViewer viewer;

    // Create our GuiEngine and hang it on QGuiApplication
    GuiEngine guiengine((QObject*)&app);

    // Register the GuiEngine with the QML runtime
    viewer.rootContext()->setContextProperty("guiEngine", &guiengine);

    // Initialise - connect to Plainbox
    guiengine.Initialise();


    // WhiteList Item Model Factory and placeholder model registered with QML engine
    WhiteListModelFactory whitelistfactory;
    viewer.rootContext()->setContextProperty("whitelistitemFactory",&whitelistfactory);

    /* We need a placeholder object here or the QML integration is unhappy
     * that this isnt a recognisable Qt object.
     */
    ListModel* whitelistmodel = new ListModel(new WhiteListItem, qApp);
    if (!whitelistmodel) {
        // Essentially we are likely out of memory here
        qDebug("Cannot create whitelist model");
        exit(1);
    }

    viewer.rootContext()->setContextProperty("whiteListModel", whitelistmodel);



    // Test Item Model Factory and placeholder model registered with QML engine
    TestItemModel testitemFactory;
    viewer.rootContext()->setContextProperty("testitemFactory",&testitemFactory);

    /* We need a placeholder object here or the QML integration is unhappy
     * that this isnt a recognisable Qt object.
     */
    ListModel* testlistmodel = new ListModel(new TestItem, qApp); //CreateTestListModel();
    if (!testlistmodel) {
        // Essentially we are likely out of memory here
        qDebug("Cannot create testlist model");
        exit(1);
    }

    viewer.rootContext()->setContextProperty("testListModel", testlistmodel);



    // We may not need this at all
    CommandTool cmdTool;
    viewer.rootContext()->setContextProperty("cmdTool", &cmdTool);



     // In the beginning, lets see if we need to resume
    bool resumeSession = false;

    QString previous = guiengine.GuiPreviousSessionFile();
     if ( previous.isEmpty() ) {
         // Show the Welcome screen
     } else {
          // show the resume screen
         qDebug() << "Resume session file : " << previous;

         resumeSession = true;
     }

    viewer.rootContext()->setContextProperty("resumePreviousSession",resumeSession);



    // Now, load the main page
    viewer.setMainQmlFile(QStringLiteral("../share/canonical-driver-test-suite/qml/canonical-driver-test-suite.qml"));

    viewer.setTitle(app.tr("Canonical Driver Test Suite"));

    // Ensure a reasonable minimum size for this window
    viewer.setMinimumSize(QSize(800,600));

    viewer.showExpanded();

    int errcode = app.exec();

    // Shutdown the guiengine
    guiengine.Shutdown();

    return errcode;
}
