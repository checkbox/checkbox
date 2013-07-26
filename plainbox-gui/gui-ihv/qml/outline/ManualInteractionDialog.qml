/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
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


Dialog {
    id: dialog

    property var testItem;

    title: i18n.tr("Manual Test")
    text: testItem.testname//i18n.tr("Name of the Test.")


    TextArea{
        id: instructions
        text: testItem.description//"This is where we put our instructions\n2- This is 1\n3 -This is where we put our instructions\n4- This is where we put our instructions\n5 -where we put our instructions\n"
        Text { font.family: "Helvetica"; font.pointSize: 13; font.bold: true }
        color: "green"
        height: units.gu(24)
    }

    Button {
        text: i18n.tr("Test")
        color: UbuntuColors.orange
        onClicked: {
            console.log("Test")
        }
    }

    Row {
        spacing: units.gu(8)
        CheckBox {
            id: yescheck
            text: i18n.tr("Yes")
            checked: true
            onClicked: {
                if (checked){
                    nocheck.checked = !checked
                    skipcheck.checked = !checked
                }
                else
                    checked = true;
            }
            Label{
                anchors.left: yescheck.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: units.gu(1)
                text: i18n.tr("Yes")
            }
        }

        CheckBox {
            id: nocheck
            text: i18n.tr("No")
            checked: false
            onClicked: {
                if (checked){
                    yescheck.checked = !checked
                    skipcheck.checked = !checked
                }
                else
                    checked = true;
            }
            Label{
                anchors.left: nocheck.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: units.gu(1)
                text: i18n.tr("No")
            }
        }

        CheckBox {
            id: skipcheck
            text: i18n.tr("Skip")
            checked: false
            onClicked: {
                if (checked){
                    nocheck.checked = !checked
                    yescheck.checked = !checked
                }
                else
                    checked = true;
            }
            Label{
                anchors.left: skipcheck.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: units.gu(1)
                text: i18n.tr("Skip")
            }
        }
    }


    Column {
        Label{
            text: i18n.tr("Comments")
        }

        TextArea {
            id: comments
            text: ""
        }
    }




    Button {
        id: continuebutton
        text: i18n.tr("Continue")
        color: UbuntuColors.warmGrey
        onClicked: {
            console.log("Continue")
            if (skipcheck.checked && comments.text === "")
            {
                PopupUtils.open(skip_warning_dialog, continuebutton);
            }

            else
                PopupUtils.close(dialog)
        }
    }



    Component {
        id: skip_warning_dialog
        WarningDialog{
            text: i18n.tr("Skipping a test requires a reason to be entered in the Comments field.  Please update that field and click 'Continue' again.");

            showCancel: false
            showContinue: false
            showCheckbox: false

            onOk: {
                console.log("ok clicked");
            }
        }
    }
}








