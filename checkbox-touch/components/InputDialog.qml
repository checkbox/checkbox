/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
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
import QtQuick 2.0
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 0.1

/*! \brief Simple input dialog.
    \inherits Item
*/
Item {
    id: inputDialog

    /*!
      This alias aids the process of popping up the dialog.
      Usage: PopupUtils.open(inputDialog.dialogComponent);
     */
    property alias dialogComponent: component

    property string prompt: ""

    signal textEntered(string text)
    signal cancelClicked()

    Component {
        id: component

        Dialog {
            id: dialog
            title: prompt

            modal: true

            TextField {
                id: textBox
                onAccepted: okButton.clicked(text)
            }

            Button {
                id: okButton
                text: i18n.tr("OK")
                color: UbuntuColors.green
                onClicked: {
                    PopupUtils.close(dialog);
                    textEntered(textBox.text);
                    textBox.text = "";
                }
            }

            Button {
                text: i18n.tr("Cancel")
                color: UbuntuColors.red
                onClicked: {
                    textBox.text = "";
                    PopupUtils.close(dialog);
                    cancelClicked();
                }
            }

            Component.onCompleted: {
                textBox.forceActiveFocus();
            }
        }
    }
}
