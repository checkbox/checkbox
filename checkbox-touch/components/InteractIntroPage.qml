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

Page {
    id: userInteractVerifyIntroPage
    property alias testName: testNameLabel.text
    property alias testDescription: testDescrptionLabel.text

    signal testStarted();
    signal testSkipped();

    function stopActivity() {
        state = "idle"
        startTestButton.unlatch()
    }

    title: i18n.tr("Test Description")
    head {
        actions: [
            Action {
                id: skipAction
                iconName: "media-seek-forward"
                text: i18n.tr("Skip")
                onTriggered: {
                    testSkipped();
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
            id: testNameLabel
            fontSize: "large"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        }

        Label {
            id: testDescrptionLabel
            fontSize: "medium"
            Layout.fillWidth: true
            Layout.fillHeight: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        }

        ActivityIndicator {
            id: activity
            Layout.alignment: Qt.AlignHCenter
            implicitHeight: units.gu(6)
            implicitWidth: units.gu(6)
        }

        LatchButton {
            id: startTestButton
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
