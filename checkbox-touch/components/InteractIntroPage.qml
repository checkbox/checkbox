/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
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
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1
import "ConfirmationLogic.js" as ConfirmationLogic

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

    title: i18n.tr("Test Description")
    head {
        actions: [
            Action {
                id: skipAction
                objectName: "skip"
                iconName: "media-seek-forward"
                text: i18n.tr("Skip")
                onTriggered: {
                    var confirmationOptions = {
                        question : i18n.tr("Do you really want to skip this test?"),
                        remember : true,
                    }
                    ConfirmationLogic.confirmRequest(userInteractVerifyIntroPage,
                        confirmationOptions, function(res) {
                            if (res) {
                                test["outcome"] = "skip";
                                testDone(test);
                            }
                    });
                }
            }
        ]
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

    ColumnLayout {
        id: descriptionContent
        spacing: units.gu(3)
        anchors.fill: parent
        anchors.margins: units.gu(3)

        Label {
            fontSize: "large"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: test["name"]
            font.bold: true
        }

        Label {
            fontSize: "medium"
            Layout.fillWidth: true
            Layout.fillHeight: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: test["description"]
        }

        ActivityIndicator {
            id: activity
            Layout.alignment: Qt.AlignHCenter
            implicitHeight: units.gu(6)
            implicitWidth: units.gu(6)
        }

        LatchButton {
            id: startTestButton
            objectName: "startTestButton"
            unlatchedColor: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Test")
            onLatchedClicked: {
                userInteractVerifyIntroPage.state = "testing"
                testStarted();
            }
        }
    }
}
