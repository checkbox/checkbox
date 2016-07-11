/*
 * This file is part of Checkbox
 *
 * Copyright 2014, 2015 Canonical Ltd.
 *
 * Authors:
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

/*! \brief Intro page for tests requiring user interation

    This page shows test name and description.
    When the test is run, page displays activity indicator
    See design document at: http://goo.gl/ghR9wL
*/

import QtQuick 2.0
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 0.1
import QtQuick.Layouts 1.1
import "actions"

Page {
    id: userInteractVerifyIntroPage
    objectName: "userInteractVerifyIntroPage"
    property var test: { "name": "", "description": "", "test_number": 0, "tests_count": 0}

    signal testStarted();
    signal testDone(var test);

    function stopActivity() {
        state = "idle"
        startTestButton.unlatch()
    }

    onTestChanged: {
        header.value = test['test_number']
        header.maximumValue = test['tests_count']
    }
    header: ProgressHeader {
        value: test['test_number']
        maximumValue: test['tests_count']
        title: i18n.tr("Test Description")
        leadingActionBar { actions: [] }
        trailingActionBar {
            objectName: 'trailingActionBar'
            actions: [
                AddCommentAction {
                    id: addCommentAction
                },
                SkipAction {
                    id: skipAction
                }
            ]
        }
    }

    state: "idle"
    states: [
         State {
            name: "idle"
            PropertyChanges { target: activity; running: false }
            PropertyChanges { target: skipAction; visible: true }
         },
         State {
            name: "testing"
            PropertyChanges { target: activity; running: true }
            PropertyChanges { target: skipAction; visible: false }
         }
     ]

    TestPageBody {
        header: test["name"]
        body: test["description"]
        ActivityIndicator {
            id: activity
            Layout.alignment: Qt.AlignHCenter
            implicitHeight: units.gu(6)
            implicitWidth: units.gu(6)
        }

        Button {
            id: showOutputButton
            objectName: "showOutputButton"
            visible: ((test["command"]) ? true : false) && (userInteractVerifyIntroPage.state == "testing")
            color: "white"
            Layout.fillWidth: true
            text: "Output"
            onClicked: {
                pageStack.push(commandOutputPage);
            }
        }

        LatchButton {
            id: startTestButton
            objectName: "startTestButton"
            unlatchedColor: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Start the test")
            onLatchedClicked: {
                userInteractVerifyIntroPage.state = "testing"
                testStarted();
            }
        }
    }
    Component.onCompleted: {
        rootKeysDelegator.setHandler('alt+s', userInteractVerifyIntroPage, skipAction.trigger);
        rootKeysDelegator.setHandler('alt+c', userInteractVerifyIntroPage, addCommentAction.trigger);
        rootKeysDelegator.setHandler('alt+t', userInteractVerifyIntroPage, startTestButton.clicked);
    }
}
