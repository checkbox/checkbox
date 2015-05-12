/*
 * This file is part of Checkbox
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


DarkDialog {
    id: dialog
    signal ok
    signal cancel
    signal cont

    property alias title: dialog.title
    property alias text: dialog.text
    property alias showOK: okButton.visible
    property alias showContinue: continueButton.visible
    property alias showCancel: cancelButton.visible
    property alias showCheckbox: checkboxitem.visible
    property alias isChecked: checkbox.checked


    title: i18n.tr("Warning!")
    text: i18n.tr("Change me to a real warning.")


    Item {
        id: checkboxitem
        width: childrenRect.width
        height: childrenRect.height

        CheckBox {
            id: checkbox
        }

        Label {
            id: checkbox_label
            text: i18n.tr("Do not show this warning again.")
            fontSize: "small"
            color: "white"
            anchors.left: checkbox.right
            anchors.leftMargin: 8
            anchors.verticalCenter: checkbox.verticalCenter

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    checkbox.checked = !checkbox.checked
                }
            }
        }

    }

    Button {
        id: okButton
        text: i18n.tr("OK")
        color: UbuntuColors.orange
        onClicked: {
            ok();
            PopupUtils.close(dialog);
        }
    }
    Button {
        id: continueButton
        text: i18n.tr("Continue")
        color: UbuntuColors.orange
        onClicked: {
            cont()
            PopupUtils.close(dialog)
        }
    }
    Button {
        id: cancelButton
        text: i18n.tr("Cancel")
        color: UbuntuColors.warmGrey
        onClicked: {
            cancel()
            PopupUtils.close(dialog)
        }
    }
}
