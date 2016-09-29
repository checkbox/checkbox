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
import QtQuick 2.0
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3
import QtQuick.Layouts 1.1

/*! \brief Common dialog popup.
    \inherits Item

    This component is a general purpose message+buttons dialog.
    It should be used through DialogMgr object.
    By default every button in the dialog will close it.

    Typical usage:
            dialogMgr.showDialog(main, i18n.tr("Operation succedded"));
            dialogMgr.showDialog(main, i18n.tr("Do you want to proceed"), [
                {"text": i18n.tr("OK"), "color": "green", "onClicked": function() {console.log("Clicked OK");} },
                {"text": i18n.tr("Cancel"), "color": "red", "onClicked": function() {console.log("Clicked cancel");} },
            ]);
*/
Item {
    id: dialog

    property var buttons: []
    property alias dialog: dialogComponent
    property string label: ""

    Component {
        id: dialogComponent

        Dialog {
            id: dlg
            title: ""
            modal: true

            ColumnLayout {
                id: layout
                Label {
                    text: label
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                    width: parent.width
                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                }
            }

            Component {
                /* This component is necessary for dynamic button creation below */
                id: btnComponent
                Button {
                    onClicked: {
                        PopupUtils.close(dlg);
                    }
                }
            }

            Component.onCompleted: {
                for (var b in buttons) {
                    var newButtonProps = buttons[b];
                    newButtonProps["Layout.fillWidth"] = true;
                    var newButton = btnComponent.createObject(layout, newButtonProps);
                    if (buttons[b]['onClicked'])
                        newButton.onClicked.connect(buttons[b]['onClicked']);
                }
            }
        }
    }
}
