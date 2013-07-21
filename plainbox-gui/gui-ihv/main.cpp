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
#include "launchgedit.h"
#include "listmodel.h"
#include "testsuiteitem.h"


// Load up test suites here (it can be moved to another file)
ListModel* CreateTestSuiteModel(){
    //QList<QObject*> list;
    ListModel *model = new ListModel(new TestSuiteItem, qApp);
    model->appendRow(new TestSuiteItem("Informational tests", "SATA/IDE devive information.", 60, "Automatic", model));
    model->appendRow(new TestSuiteItem("Hibernation tests", "power-management/hibernate_advanced", 22, "Manual", model));
    model->appendRow(new TestSuiteItem("Wireless networking tests", "wireless/wireless_scanning", 360, "Automatic", model));
    model->appendRow(new TestSuiteItem("Wireless networking tests", "wireless/wireless_connection", 600, "Automatic", model));
    model->appendRow(new TestSuiteItem("LED tests", "led/wireless", 200, "Manual",model));
    model->appendRow(new TestSuiteItem("Benchmarks tests", "benchmarks/network/network-loopback", 100, "Manual",model));
    model->appendRow(new TestSuiteItem("Suspend tests", "suspend/led_after_suspend/wireless", 1, "Manual",model));
    model->appendRow(new TestSuiteItem("Suspend tests", "suspend/wireless_after_suspenspeded", 2,  "Manual",model));

    return model;
}





int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    qmlRegisterType<TestSuiteItem>("Ubuntu.IhvTest", 0, 1, "TestSuiteItem");

    QDir pluginsDir;
    pluginsDir.setPath("../plugins");

    QPluginLoader loader("../plugins/libgui-engine.so");

    QQmlExtensionPlugin *plugin = qobject_cast<QQmlExtensionPlugin*>(loader.instance());
    if (plugin)
        plugin->registerTypes("GuiEngine");

    QtQuick2ApplicationViewer viewer;
    viewer.rootContext()->setContextProperty("testSuiteModel", CreateTestSuiteModel());

    LaunchGEdit glauncher;
    viewer.rootContext()->setContextProperty("gedit", &glauncher);

    viewer.setMainQmlFile(QStringLiteral("qml/outline/gui-ihv.qml"));
    viewer.showExpanded();

    return app.exec();
}
