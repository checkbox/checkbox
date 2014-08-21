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
    property alias plainboxVersion: plainbox.version
    // Version of pyotherside
    property string pyothersideVersion;
    // Version of python runtime
    property string pythonVersion;
    // Signal sent when the stack has been fully initialized, plainboxVersion
    // is available and all PlainBox APIs are ready to use
    signal stackReady()

    // Pyotherside python object that we use to talk to all of plainbox
    Python {
        id: py
        // callback invoked when PlainBox is created
        function _onPlainBoxCreated(handle) {
            plainbox.handle = handle;
        }
        // callback invoked when checkbox_stack module is loaded
        function _onCheckboxStackLoaded() {
            call("checkbox_stack.create_plainbox_object", [], _onPlainBoxCreated);
        }
        function _init() {
            // Store versions of pyotherside and python for reference
            stack.pyothersideVersion = pluginVersion();
            stack.pythonVersion = pythonVersion();
            // A bit hacky but that's where the python code is
            addImportPath(Qt.resolvedUrl('../py/'));
            // Import path for plainbox and potentially other python libraries
            addImportPath(Qt.resolvedUrl('../lib/py'))
            // Import the checkbox_stack module on startup
            importModule("checkbox_stack", _onCheckboxStackLoaded);
        }
        Component.onCompleted: _init()
        onError: console.error("python error: " + traceback)
        onReceived: console.log("pyotherside.send: " + data)
    }

    // Handle to a PlainBox object.
    // Using this handle we can inspect the list of providers and sessions.
    PlainBox {
        py: py
        id: plainbox
        // Send the stackReady() signal once we get the version string
        onVersionChanged: {
            stack.stackReady()
        }
    }
}
