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

/*!
    \qmltype WarningDialog
    \inherits Dialog
    \inqmlmodule
    \ingroup
    \brief The Dialog This Dialog shows a Warning Dialog.
    Turn on/off before showing:
                ok, showOK
                cancel, showCancel
                continue, showContinue
                'do not show warning' checkbox, showCheckbox
    Signals: onOK, onCancel, onCont (continue)
    Property: isChecked returns if the user checked 'do not show warning'

    Example:
    \qml
        import Ubuntu.Components 0.1
        import Ubuntu.Components.Popups 0.1
        import "."

        Item {
            Component {
                id: warning_dialog

                WarningDialog{
                    text: i18n.tr("The hoopla met the poopla and we all could no longer do as we want.  Would you like me to try again?")
                    showOK: false
                    showCheckbox: true

                    onCont: {
                        checkIfChecked();
                       console.log("continue clicked");
                    }

                    onCancel: {
                      checkIfChecked();
                     console.log("cancel clicked");
                    }

                    function checkIfChecked(){
                        if (isChecked)
                            console.log("do not warn again!");
                        else
                            console.log("warn again");
                    }

                }
              }
            Button {
                id: warning_button
                color: "yellow"
                text: "warning..."
                width: 100
                onClicked:{
                    PopupUtils.open(warning_dialog, warning_button);
                }
            }
    }
    \endqml
*/

Dialog {
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
            anchors.left: checkbox.right
            anchors.leftMargin: 8

            anchors.verticalCenter: checkbox.verticalCenter
        }

    }

    Button {
        id: okButton
        text: i18n.tr("ok")
        color: UbuntuColors.orange
        onClicked: {
            ok();
            PopupUtils.close(dialog);
        }
    }
    Button {
        id: continueButton
        text: i18n.tr("continue")
        color: UbuntuColors.orange
        onClicked: {
            cont()
            PopupUtils.close(dialog)
        }
    }
    Button {
        id: cancelButton
        text: i18n.tr("cancel")
        color: UbuntuColors.warmGrey
        onClicked: {
            cancel()
            PopupUtils.close(dialog)
        }
    }
}








