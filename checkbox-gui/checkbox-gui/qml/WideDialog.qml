/*
 * This file is part of Checkbox
 *
 * Copyright 2012-2015 Canonical Ltd.
 *
 * Authors:
 * - Sylvain Pineau <sylvain.pineau@canonical.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import Ubuntu.Components 0.1
import Ubuntu.Components.Popups 0.1

PopupBase {
    id: dialog
    // See Dialog.qml
    default property alias contents: contentsColumn.data
    property alias title: foreground.title
    property alias text: foreground.text
    property bool modal: true
    // Cannot override FINAL property, so alias names have to be different
    property alias dialogWidth: foreground.width
    property alias dialogHeight: foreground.height

    __foreground: foreground
    __eventGrabber.enabled: modal
    __dimBackground: modal
    fadingAnimation: UbuntuNumberAnimation { duration: UbuntuAnimation.SnapDuration }

    FocusScope {
        id: foreground
        // Default settings, the Dialog will take the full MainView size
        width: parent.width
        height: parent.height
        anchors.centerIn: parent

        property string title
        property string text
        property real margins: units.gu(2)
        property Item dismissArea: dialog.dismissArea

        UbuntuShape {
            id: background
            anchors.fill: parent
            color: Qt.rgba(0, 0, 0, 0.7)

            Column {
                id: contentsColumn
                anchors {
                    fill: parent
                    margins: foreground.margins
                }
                onWidthChanged: updateChildrenWidths();

                Label {
                    horizontalAlignment: Text.AlignHCenter
                    text: dialog.title
                    fontSize: "large"
                    color: Qt.rgba(1, 1, 1, 0.9)
                }

                Label {
                    horizontalAlignment: Text.AlignHCenter
                    text: dialog.text
                    fontSize: "medium"
                    color: Qt.rgba(1, 1, 1, 0.6)
                    wrapMode: Text.Wrap
                    visible: (text !== "")
                }

                onChildrenChanged: updateChildrenWidths()

                function updateChildrenWidths() {
                    for (var i = 0; i < children.length; i++) {
                        children[i].width = contentsColumn.width;
                    }
                }
            }
        }
    }
}
