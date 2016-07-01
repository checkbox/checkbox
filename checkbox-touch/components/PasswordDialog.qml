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

/*! \brief Password prompt dialog.
    \inherits Item

    This component is a prompt for user's password.
*/
Item {
    id: passwordDialog

    /*!
      This alias aids the process of popping up the dialog.
      Usage: PopupUtils.open(passwordDialog.dialogComponent);
     */
    property alias dialogComponent: component

    signal passwordEntered(string password)
    signal dialogCancelled

    Component {
        id: component

        Dialog {
            id: dialog
            title: i18n.tr("Enter password")

            modal: true

            TextField {
                id: passwordBox
                objectName: "passwordBox"
                placeholderText: i18n.tr("password")
                echoMode: TextInput.Password
                onAccepted: okButton.clicked(text)
            }

            Button {
                id: okButton
                objectName: "okButton"
                text: i18n.tr("OK")
                color: UbuntuColors.green
                onClicked: {
                    PopupUtils.close(dialog);
                    // once qml pam authentication goes live, we might want to
                    // check if the password is correct in some QML-ish manner
                    passwordEntered(passwordBox.text);
                    passwordBox.text = "";
                }
            }

            Button {
                objectName: "cancelButton"
                text: i18n.tr("Cancel")
                color: UbuntuColors.red
                onClicked: {
                    passwordBox.text = "";
                    PopupUtils.close(dialog);
                    dialogCancelled();
                }
            }

            Component.onCompleted: {
                // let user type in password without tapping on
                // the text field
                passwordBox.forceActiveFocus();
            }
        }
    }
}
