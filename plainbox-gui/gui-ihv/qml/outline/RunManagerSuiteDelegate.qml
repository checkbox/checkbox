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
        property string labelname: section
        property alias summaryText: testsummarytext.text
        property bool open: true

        onOpenChanged: {
            open?progressIcon.source = "artwork/DownArrow.png":progressIcon.source = "artwork/RightArrow.png"
        }

        MouseArea {
            width: parent.width
            height: parent.height
            anchors.fill: parent

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
            id: progressIcon
            source: "artwork/DownArrow.png"
            width: units.gu(2)
            height: units.gu(2)
            anchors {
                verticalCenter: parent.verticalCenter
                left: groupfiller.left

            }
           opacity: enabled ? 1.0 : 0.5
        }


        Text {
            id: grouptext
            text: section
            width: units.gu(20)
            anchors{
                verticalCenter: parent.verticalCenter
                left: progressIcon.right
                leftMargin: units.gu(1)
            }
            font.bold: true
            color: UbuntuColors.coolGrey
        }

        Item {
            id: testsummaryfiller
            width: units.gu(38)
            anchors.left: grouptext.right
        }

        Text {
            id: testsummarytext
            text: ""
            width: units.gu(10)
            anchors.left:  testsummaryfiller.right
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
            color: "green"
            font.bold : true
        }



        ListItem.ThinDivider {}



}
}

