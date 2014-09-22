/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
 *
 * Authors:
 * - Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

import QtQuick 2.0
import io.thp.pyotherside 1.2

Item {
    id: stack
    // Version of the plainbox core
    property alias plainboxVersion: app.plainboxVersion
    // Version of the checkbox touch application
    property alias applicationVersion: app.applicationVersion
    // Version of pyotherside
    property string pyothersideVersion;
    // Version of python runtime
    property string pythonVersion;
    // Exposed application instance
    property alias application: app
    // Signal sent when the stack has been fully initialized, plainboxVersion
    // is available and all PlainBox APIs are ready to use, i.e. when request()
    // can be used.
    signal stackReady()

    // Pyotherside python object that we use to talk to all of plainbox
    Python {
        id: py
        // callback invoked when the application object is created
        function _onCheckboxTouchAppCreated(handle) {
            app.handle = handle;
        }
        // callback invoked when checkbox_touch module is loaded
        function _onCheckboxTouchLoaded() {
            call("checkbox_touch.create_app_object", [], _onCheckboxTouchAppCreated);
        }
        function _init() {
            // Store versions of pyotherside and python for reference
            stack.pyothersideVersion = pluginVersion();
            stack.pythonVersion = pythonVersion();
            // A bit hacky but that's where the python code is
            addImportPath(Qt.resolvedUrl('../py/'));
            // Import path for plainbox and potentially other python libraries
            addImportPath(Qt.resolvedUrl('../lib/py'))
            // Import the checkbox_touch module on startup
            importModule("checkbox_touch", _onCheckboxTouchLoaded);
        }
        Component.onCompleted: _init()
        onError: console.error("python error: " + traceback)
        onReceived: console.log("pyotherside.send: " + data)
    }

    // Handle to a CheckboxTouchApplication object.
    // Using this handle we can inspect the list of providers and sessions.
    CheckboxTouchApplication {
        py: py
        id: app
        // Send the stackReady() signal once we get the version string
        onPlainboxVersionChanged: {
            stack.stackReady()
        }
    }
}
