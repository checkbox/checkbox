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
import "."

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
            open?openshutIcon.source = "artwork/DownArrow.png":openshutIcon.source = "artwork/RightArrow.png"
        }

        MouseArea {
            width: parent.width// - groupcheckbox.width
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
            width: units.gu(2)
        }

        Image {
            id: openshutIcon
            source: "artwork/DownArrow.png"
            width: units.gu(2)
            height: units.gu(2)
            anchors {
                verticalCenter: parent.verticalCenter
                left: groupfiller.left
            }

            opacity: enabled ? 1.0 : 0.5
        }

        CheckBox {
            id: groupcheckbox
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: openshutIcon.right
            anchors.leftMargin: units.gu(1)
            checked: true
            onClicked: {
                groupedList.selectGroup(section, checked)
                if (!checked)
                    groupedList.showWarning(groupcheckbox);
            }
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
            width: units.gu(38)
            anchors.left: grouptext.right
        }

        Text {
            id: estimatedTimeText
            text: groupedList.getEstimatedTime(section)
            width: units.gu(10)
            anchors.left:  estfiller.right
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
            color: "green"
            font.bold : true
        }



        ListItem.ThinDivider {}
    }
}

