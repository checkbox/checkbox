/*
 * Copyright 2015 Canonical Ltd.
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

    default property alias contents: contentsColumn.data

    property alias title: foreground.title
    property alias text: foreground.text
    property Item caller
    property real edgeMargins: units.gu(2)
    property real callerMargin: units.gu(1)
    property bool modal: true

    __foreground: foreground
    __eventGrabber.enabled: modal
    __dimBackground: modal
    fadingAnimation: UbuntuNumberAnimation { duration: UbuntuAnimation.SnapDuration }

    UbuntuShape {
        id: foreground
        width: Math.min(minimumWidth, dialog.width)
        anchors.centerIn: parent
        color: Qt.rgba(0, 0, 0, 0.7)

        // used in the style
        property string title
        property string text
        property real minimumWidth: units.gu(38)
        property real minimumHeight: units.gu(32)
        property real maxHeight: 3*dialog.height/4
        property real margins: units.gu(4)
        property real itemSpacing: units.gu(2)
        property Item dismissArea: dialog.dismissArea

        height: Math.min(childrenRect.height + itemSpacing, dialog.height)

        Column {
            id: contentsColumn
            anchors {
                top: parent.top
                left: parent.left
                right: parent.right
                margins: foreground.margins
            }
            spacing: foreground.itemSpacing
            height: childrenRect.height + foreground.margins
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
