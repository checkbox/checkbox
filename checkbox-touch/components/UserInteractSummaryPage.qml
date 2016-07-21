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

/*! \brief Page for User-Interact test - summary step

    This page shows result of automated verification of a test.
    See design document at: http://goo.gl/6pNAFE
*/

import QtQuick 2.0
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3
import QtQuick.Layouts 1.1
import "actions"

Page {
    id: userInteractSummary
    objectName: "userInteractSummary"
    property var test: { "name": "", "outcome": "pass", "test_number": 0, "tests_count": 0}

    signal testDone(var test);

    onTestChanged: {
        header.value = test['test_number']
        header.maximumValue = test['tests_count']
    }
    header: ProgressHeader {
        value: test['test_number']
        maximumValue: test['tests_count']
        title: i18n.tr("Verification")
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

    TestPageBody {
        header: test["name"]
        fullHeightBody: false

        Row {
            Layout.fillWidth: true
            Label {
                fontSize: "large"
                Layout.fillHeight: true
                // TRANSLATORS: this string will be followed by either "PASSED" or "FAILED"
                text : i18n.tr("This test ")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            }

            Rectangle {
                height: resultLabel.height
                width: resultLabel.width + units.gu(1)
                Layout.alignment: Qt.AlignCenter
                radius: 2
                color: test["outcome"] == "pass" ? UbuntuColors.green : UbuntuColors.red

                Label {
                    id: resultLabel
                    height: paintedHeight
                    fontSize: "large"
                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                    color: "white"
                    text : test["outcome"] == "pass" ? i18n.tr("PASSED") : i18n.tr("FAILED")
                    anchors.centerIn: parent
                }
            }
        }

        Label {
            fontSize: "large"
            Layout.fillHeight: true
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text : i18n.tr("You can go back to rerun the test or continue to the next test.")
        }

        Button {
            id: continueButton
            color: UbuntuColors.green
            objectName: "continueButton"
            Layout.fillWidth: true
            text: i18n.tr("Continue")
            onClicked: {
                testDone(test);
            }
        }
    }
    Component.onCompleted: {
        rootKeysDelegator.setHandler('alt+s', userInteractSummary, skipAction.trigger);
        rootKeysDelegator.setHandler('alt+c', userInteractSummary, addCommentAction.trigger);
        rootKeysDelegator.setHandler('alt+t', userInteractSummary, continueButton.clicked);
    }
}
