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
import Ubuntu.Components 1.1
import Ubuntu.Components.Popups 0.1

/*! \brief Skip-confirmation dialog.
    \inherits Item

    This component is a confirmation dialog with an option to remember
    selected option. It comes with a Component object encosing dialog so
    callers have to call PopupUtils.open() only.
*/

Item {
    id: confirmationDialog
    objectName: "confirmationDialog"

    /*!
        Gets signalled user selects an option
     */
    signal answer(bool confirmation, bool remember)

    /*!
      `dialog` alias helps use the component containing dialog
    */
    property alias dialog : dialogComponent

    /*!
      Text to display in confimation dialog
    */
    property string question : i18n.tr("Are you sure?")

    /*!
      Presents option to remember choice
    */
    property bool withRemember: false

    width: units.gu(80)
    height: units.gu(80)
    Component {
        id: dialogComponent

        Dialog {
            id: dlg
            objectName: "dialog"
            modal: true // Screen behind the dialog will be greyed-out
            title: question

            Button {
                text: i18n.tr("YES")
                objectName: "yesButton"
                color: UbuntuColors.green
                onClicked: {
                    answer(true, checkBox.checked);
                    PopupUtils.close(dlg);
                }
            }
            Button {
                text: i18n.tr("NO")
                objectName: "noButton"
                color: UbuntuColors.red
                onClicked: {
                    answer(false, checkBox.checked);
                    PopupUtils.close(dlg);
                }
            }

            Row {
                visible: withRemember
                CheckBox {
                    id: checkBox
                }
                Label {
                    text: i18n.tr("Do not ask me this question again")
                    anchors.verticalCenter: parent.verticalCenter
                    MouseArea{
                        // This MouseArea helps trigger checkbox changes
                        // when user taps on the label
                        anchors.fill: parent
                        onClicked: {
                            checkBox.checked = !checkBox.checked
                        }
                    }
                }
            }
        }
    }
}
