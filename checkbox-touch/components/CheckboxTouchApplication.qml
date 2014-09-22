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


PythonObjectHandle {
    id: app
    // Version of the application
    property string applicationVersion
    // Version of the plainbox library
    property string plainboxVersion

    // The identifier of the default test plan to execute. It will be
    // stored in the back-end and will be used as the default test
    // plan for other API calls
    property var testPlan: "tbd"; // TODO: use a real test plan ID

    // Signal sent when a session becomes ready
    signal sessionReady();

    // Create a new session
    //
    // Starts session in plainbox and runs all necessary setup actions
    // AppController will signal sessionReady() once it's finished doing setup.
    function startSession() {
        invoke("start_session", [app.testPlan], function() {
            sessionReady();
        });
    }

    onHandleReady: {
        invoke("get_version_pair", [], function(response) {
            app.applicationVersion = response.application_version;
            app.plainboxVersion = response.plainbox_version;
        });
    }
}
