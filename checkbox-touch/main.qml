/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
 *
 * Authors:
 * - Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
 * - Maciej Kisielewski <maciej.kisielewski@canonical.com>
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
import Ubuntu.Components 1.1
import "components"


/*!
    \brief MainView with a Label and Button elements.
*/

MainView {
    // objectName for functional testing purposes (autopilot-qt5)
    objectName: "mainView"

    // Note! applicationName needs to match the "name" field of the click manifest
    applicationName: "com.canonical.certification.checkbox-touch"

    /*
     This property enables the application to change orientation
     when the device is rotated. The default is false.
    */
    //automaticOrientation: true

    width: units.gu(100)
    height: units.gu(75)

    useDeprecatedToolbar: false

    // High-level object representing the full checkbox testing stack
    CheckboxStack {
        id: checkboxStack
        onStackReady: {
            console.log("Pyotherside version" + pyothersideVersion);
            console.log("Python version " + pythonVersion);
            console.log("Plainbox version " + plainboxVersion);
            console.log("Checkbox Touch version " + applicationVersion);
            // TODO: enable the start testing button on the welcome page
        }
    }

    PageStack {
        id: pageStack
        Component.onCompleted: {
            push(welcomePage);
        }
    }

    WelcomePage {
        id: welcomePage;
        welcomeText: i18n.tr("Welcome to Checkbox Touch");
        onStartTestingTriggered: {
            checkboxStack.application.startSession();
        }
    }
}
