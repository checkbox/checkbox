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
    for (int i = 0; i < 20; i++){
        QString s;
        QTextStream(&s) << i << " SATA/IDE devive information.";
        model->appendRow(new TestSuiteItem("Informational tests", s, 60, "Automatic", model));
    }
    for (int i = 0; i < 5; i++){
        QString s;
        QTextStream(&s) << i << "  power-management/hibernate_advanced";
        model->appendRow(new TestSuiteItem("Hibernation tests", s, 60, "Automatic", model));
    }

    for (int i = 0; i < 3; i++){
        QString s;
        QTextStream(&s) << i << "  wireless/wireless_scanning";
        model->appendRow(new TestSuiteItem("Wireless networking tests", s, 360, "Automatic", model));
    }

    for (int i = 0; i < 3; i++){
        QString s;
        QTextStream(&s) << i << "  led/wireless";
        model->appendRow(new TestSuiteItem("LED tests", s, 360, "Automatic", model));
    }

    for (int i = 0; i < 5; i++){
        QString s;
        QTextStream(&s) << i << "  benchmarks/network/network-loopback";
        model->appendRow(new TestSuiteItem("Benchmarks tests", s, 360, "Automatic", model));
    }

    for (int i = 0; i < 3; i++){
        QString s;
        QTextStream(&s) << i << "  suspend/led_after_suspend/wireless";
        model->appendRow(new TestSuiteItem("Suspend tests", s, 1, "Manual",model));
     }

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
