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
import Ubuntu.Components.ListItems 0.1 as ListItem
import "./artwork"

Component {
    id: groupDelegate
    Item {
        id: itemdelegate
        width: parent.width
        height: units.gu(7)
        property string groupname: section
        property alias checked: groupcheckbox.checked
        property string labelname: section
        property bool open: true

        onOpenChanged: {
            open?progressIcon.source = "DownArrow.png":progressIcon.source = "RightArrow.png"
        }

        MouseArea {
            width: parent.width - groupcheckbox.width
            height: parent.height
            anchors.right: parent.right

            onClicked: {
                itemdelegate.open = !itemdelegate.open
                groupedList.openShutSubgroup(section, itemdelegate.open)
                //console.log("Open/Shut items below")
            }
        }

        Item {
            id: groupfiller
            width: units.gu(1)
        }

        CheckBox {
            id: groupcheckbox
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: groupfiller.right
            anchors.leftMargin: units.gu(1)
            checked: groupedList.isGroupSelected(section)
            onClicked: groupedList.selectGroup(section, checked)
        }


        Text {
            id: grouptext
            text: section
            width: units.gu(20)
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: groupcheckbox.right
            anchors.leftMargin: units.gu(1)
        }

        Item {
            id: estfiller
            width: units.gu(55)
            anchors.left: grouptext.right
        }

        Text {
            id: estimatedTimeText
            text: groupedList.getEstimatedTime(section)
            width: units.gu(12)
            anchors.left:  estfiller.right
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
            color: "green"
            font.bold : true
        }

        Image {
            id: progressIcon
            source: "DownArrow.png"
            anchors {
                verticalCenter: parent.verticalCenter
                right: parent.right
                rightMargin: units.gu(1)
            }

            opacity: enabled ? 1.0 : 0.5
        }

        ListItem.ThinDivider {}
    }
}

