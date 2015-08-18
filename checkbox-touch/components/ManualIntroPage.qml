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

/*! \brief Page for Manual test - introduction step

    This page shows test name and description of an Manual test.
    See design document at: http://goo.gl/vrD9yn
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1
import Ubuntu.Components.Popups 0.1
import "ConfirmationLogic.js" as ConfirmationLogic

Page {
    id: manualIntroPage
    objectName: "manualIntroPage"
    property var test: { "name": "", "description": "", "test_number": 0, "tests_count": 0}

    signal continueClicked();
    signal testDone(var test);

    title: i18n.tr("Test Description")
    head {
        actions: [
            Action {
                id: addCommentAction
                iconName: "document-new-symbolic"
                text: i18n.tr("Add comment")
                onTriggered: {
                    commentsDialog.commentAdded.connect(function(comment) {
                        test["comments"] = comment;
                    });
                    PopupUtils.open(commentsDialog.dialogComponent);
                }
            },
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
                    ConfirmationLogic.confirmRequest(manualIntroPage,
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
        spacing: units.gu(3)
        anchors {
            fill: parent
            topMargin: units.gu(3)
            bottomMargin: units.gu(3)
            leftMargin: units.gu(1)
            rightMargin: units.gu(1)
        }

        Label {
            fontSize: "large"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: test["name"]
            font.bold: true
        }

        Flickable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentHeight: childrenRect.height
            flickableDirection: Flickable.VerticalFlick
            clip: true
            Label {
                fontSize: "medium"
                anchors.fill: parent
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                text: test["description"]
            }
        }

        Button {
            objectName: "continueButton"
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Continue")
            onClicked: {
                continueClicked();
            }
        }
    }
}
