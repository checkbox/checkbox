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
import Ubuntu.Components 1.1
import Ubuntu.Components.ListItems 1.0

/*! \brief ListItemWrappable
    \inherits Empty

    List item class similar to ListItems.Standard, but with wrappable text.
    It shows text and a control item. The height of the item will be
    automatically increased to fit the contained text label.
*/
Empty {
    id: listItem

    property alias control: controlContainer.control

    property var selected

    highlightWhenPressed: !listItem.control

    // Avoid emit clicked signals when clicking on the control area
    __acceptEvents: false

    height: (label.contentHeight < control.height ? control.height : label.contentHeight) + units.gu(2)
    __contents.anchors.topMargin: units.gu(1)
    __contents.anchors.bottomMargin: units.gu(1)
    __contentsMargins: 0
    divider.anchors.leftMargin: 0
    divider.anchors.rightMargin: 0

    property bool __controlAreaPressed: false
    Rectangle {
        id: controlHighlight

        visible: listItem.swipingState === "" ? control && __controlAreaPressed : false
        anchors.fill: parent
        color: Theme.palette.selected.background
    }

    property bool __iconIsItem: false
    property alias __foregroundColor: label.color
    property real __rightIconMargin

    Label{
        id: label
        property var selected: listItem.selected
        anchors {
            verticalCenter: parent.verticalCenter
            left: parent.left
            leftMargin: __iconIsItem ? icon.width + 2 * listItem.__contentsMargins : listItem.__contentsMargins
            right: control ? controlContainer.left : (progression ? progressionHelper.left : parent.right)
            rightMargin: listItem.__contentsMargins
        }
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        clip: true
        text: listItem.text
        verticalAlignment: Text.AlignVCenter
    }

    Item {
        id: controlContainer
        property Item control

        width: control ? control.width : undefined
        height: control ? control.height : undefined
        anchors {
            right: listItem.progression ? progressionHelper.left : parent.right
            rightMargin: listItem.__contentsMargins
        }

        onControlChanged: {
            if (control) control.parent = controlContainer;
        }

        Connections {
            target: listItem.__mouseArea

            onClicked: {
                if (control) {
                    if (control.enabled && control.hasOwnProperty("clicked")) control.clicked();
                } else {
                    listItem.clicked();
                }
            }

            onPressAndHold: {
                if (control && control.enabled && control.hasOwnProperty("pressAndHold")) {
                    control.pressAndHold();
                } else {
                    listItem.pressAndHold();
                }
            }
        }
    }

    onPressedChanged: {
        if (listItem.pressed && control && control.enabled) {
            listItem.__controlAreaPressed = true
        } else {
            listItem.__controlAreaPressed = false
        }
    }
}
