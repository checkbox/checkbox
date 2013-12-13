/*
 * This file is part of Checkbox
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

import QtQuick 2.0
import Ubuntu.Components 0.1
import Ubuntu.Components.Popups 0.1
import "."


MainView {
    id: mainView
    width: units.gu(100)
    height: units.gu(90)

    // TODO - For Resume dialog, when plainbox starts up, check if this is a 'Resume'
    // if it is, set pageName = "ResumeView", state = "RESUME"

    Component.onDestruction: {console.log("SHUTDOWN");}

    PageStack {
        id: pageStack
        state: "WELCOME"
        property string pageName: "WelcomeView.qml"  // initial state

        Component.onCompleted: {
            push(Qt.resolvedUrl(pageName))

            // Check if we need to resume
            if (resumePreviousSession === true)
            {
                pageName = "ResumeView.qml";
                state = "RESUME"
                push(Qt.resolvedUrl(pageName))
            }
        }

        onPageNameChanged: {
            pop();
            push(Qt.resolvedUrl(pageName))
        }
    }

    // The pages/views will set the state to the next one when it is done
    // like this: onClicked: {mainView.state = "TESTSELECTION"}
    states: [
        State {
            name: "WELCOME"
            PropertyChanges { target: pageStack; pageName: "WelcomeView.qml"}
        },
        State {
            name: "SUITESELECTION"
            PropertyChanges { target: pageStack; pageName: "SuiteSelectionView.qml"}
        },
        State {
            name: "DEMOWARNINGS"
            PropertyChanges { target: pageStack; pageName: "DemoWarnings.qml"}
        },
        State {
            name: "TESTSELECTION"
            PropertyChanges { target: pageStack; pageName: "TestSelectionView.qml"}
        },
        State {
            name: "RUNMANAGER"
            PropertyChanges {target: pageStack; pageName: "RunManagerView.qml"}
        },
        State {
            name: "RESUME"
            PropertyChanges {target: pageStack; pageName: "ResumeView.qml"}
        }
    ]
}



