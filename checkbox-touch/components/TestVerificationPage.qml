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

/*! \brief Test verification page

    This page asks user whether the action was completed successfully
    See design document at: http://goo.gl/ghR9wL
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1
import "ConfirmationLogic.js" as ConfirmationLogic

Page {
    id: testVerification
    property var test: { "name": "", "verificationDescription": "" }

    signal testDone(var test);

    objectName: "testVerificationPage"
    title: i18n.tr("Verification")

    head {
        actions: [
            Action {
                iconName: "media-seek-forward"
                text: i18n.tr("Skip")
                onTriggered: {
                    var confirmationOptions = {
                        question : i18n.tr("Do you really want to skip this test?"),
                        remember : true,
                    }
                    ConfirmationLogic.confirmRequest(testVerification,
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
            text: test["verificationDescription"]
        }

        LatchButton {
            unlatchedColor: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Yes")
            onLatchedClicked: {
                test["outcome"] = "pass";
                testDone(test);
            }
        }

        LatchButton {
            unlatchedColor: UbuntuColors.red
            Layout.fillWidth: true
            text: i18n.tr("No")
            onLatchedClicked: {
                test["outcome"] = "fail";
                testDone(test);
            }
        }
    }
}
