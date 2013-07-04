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
#include "qtquick2applicationviewer.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    QDir pluginsDir;
    pluginsDir.setPath("../plugins");

    QPluginLoader loader("../plugins/libgui-engine.so");

    QQmlExtensionPlugin *plugin = qobject_cast<QQmlExtensionPlugin*>(loader.instance());
    if (plugin)
        plugin->registerTypes("GuiEngine");

    QtQuick2ApplicationViewer viewer;
    viewer.setMainQmlFile(QStringLiteral("qml/outline/gui-ihv.qml"));
    viewer.showExpanded();

    return app.exec();
}
