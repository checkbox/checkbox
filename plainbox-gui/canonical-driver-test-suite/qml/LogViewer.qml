/*
 * This file is part of plainbox-gui
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
    id: logview
    title: "Not Set"
    property string jobPath: "Not Set"
    Rectangle {
        color: "black"
        radius: units.gu(1)
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            bottom: backButton.top
            topMargin: units.gu(5)
            bottomMargin: units.gu(2)
        }

        Item {
            id: logitem
            anchors.margins: units.gu(1)
            anchors.fill: parent

            Flickable {
                id: flickable
                width: parent.width
                height: parent.height
                contentWidth: logtext.width
                contentHeight: logtext.height
                flickableDirection: Flickable.VerticalFlick
                clip: true

                TextEdit {
                    id: logtext
                    width:logitem.width
                    selectionColor: Theme.palette.selected.background
                    color: Qt.rgba(1, 1, 1, 0.9)
                    wrapMode: Text.Wrap
                    text: "<code>Unable to load IO log</code>"
                    readOnly: true
                    selectByMouse: true
                    textFormat: TextEdit.RichText

                    Component.onCompleted: {
                        // get the log info from guiengine
                        text = "<code>" + guiEngine.GetIOLog(jobPath) + "</code>";
                    }
                }
            }
            Scrollbar {
                flickableItem: flickable
                align: Qt.AlignTrailing
            }
        }
    }
    Button {
        id: backButton
        text: "Back"
        onClicked: PopupUtils.close(logview)
        anchors.bottom: parent.bottom
    }
}
