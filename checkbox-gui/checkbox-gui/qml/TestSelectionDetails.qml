/*
 * This file is part of Checkbox
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
 * - Sylvain Pineau <sylvain.pineau@canonical.com>
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

WideDialog {
    id: detailsview
    title: currentTestItem.testname
    dialogHeight: testdetails.height + (backButton.height * 3) + units.gu(1) > Math.round(mainView.height / 1.618) ? Math.round(mainView.height / 1.618) : testdetails.height + (backButton.height * 3) + units.gu(1)
    dialogWidth: Math.round(parent.width / 2 * 1.618)
    Flickable {
        id: flickable
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            bottom: backButton.top
            topMargin: units.gu(5)
            bottomMargin: units.gu(2)
        }
        width: parent.width
        height: parent.height
        contentHeight: testdetails.height
        flickableDirection: Flickable.VerticalFlick
        clip: true

        Rectangle {
            id: testdetails
            height: detailsblock.height
            width: parent.width
            color: "transparent"

            Item{
                id: detailsblock

                height: nameText.height + descriptionText.height + dependsText.height + requiresText.height + commandText.height + units.gu(1)
                width: parent.width

                TestSelectionDetailsItems{
                    id: nameText
                    labelName: i18n.tr("name")
                    anchors.top: parent.top
                    text: currentTestItem.testname
                }

                TestSelectionDetailsItems{
                    id: descriptionText
                    labelName: i18n.tr("description")
                    anchors.top: nameText.bottom
                    text: currentTestItem.description
                }

                TestSelectionDetailsItems{
                    id: dependsText
                    labelName: i18n.tr("depends")
                    anchors.top: descriptionText.bottom
                    text: currentTestItem.depends
                }

                TestSelectionDetailsItems{
                    id: requiresText
                    labelName: i18n.tr("requires")
                    anchors.top: dependsText.bottom
                    text:currentTestItem.requires
                }

                TestSelectionDetailsItems{
                    id: commandText
                    labelName: i18n.tr("command")
                    anchors.top: requiresText.bottom
                    text: "<code>" + currentTestItem.command.replace(/\n/g, "<br />") + "</code>"
                    textFormat: TextEdit.RichText
                }
            }
        }
    }

    Scrollbar {
        flickableItem: flickable
        align: Qt.AlignTrailing
    }

    Button {
        id: backButton
        text: "Back"
        onClicked: PopupUtils.close(detailsview)
        anchors.bottom: parent.bottom
    }
}
