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

    title: i18n.tr("Manual Test")
    text: i18n.tr("Name of the Test.")


    TextArea{
        id: instructions
        text: "This is where we put our instructions\n
               2- This is
        3 -This is where we put our instructions\n
        4- This is where we put our instructions\n
        5 -where we put our instructions\n"
        Text { font.family: "Helvetica"; font.pointSize: 13; font.bold: true }
        color: "green"
    }


    Row {
        spacing: units.gu(8)
        CheckBox {
            id: yescheck
            text: i18n.tr("Yes")
            checked: true
            onClicked: {
                nocheck.checked = !checked
                skipcheck.checked = !checked
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
                yescheck.checked = !checked
                skipcheck.checked = !checked
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
                nocheck.checked = !checked
                yescheck.checked = !checked
            }
            Label{
                anchors.left: skipcheck.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: units.gu(1)
                text: i18n.tr("Skip")
            }
        }
    }

    Button {
        text: i18n.tr("Test")
        onClicked: {
            console.log("Test")
        }
    }
    Column {
        Label{
            text: i18n.tr("Comments")
        }

    TextArea {
id: comments
    }
    }


    Button {
        text: i18n.tr("Previous")
        color: UbuntuColors.warmGrey
        onClicked: {
            console.log("Previous")
            PopupUtils.close(dialog)
        }
    }


    Button {
        text: i18n.tr("Next")
        color: UbuntuColors.warmGrey
        onClicked: {
            console.log("Next")
            PopupUtils.close(dialog)
        }
    }
}








