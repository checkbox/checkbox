/*
 * This file is part of Checkbox
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

        // properties for opening/closing sections
        property string groupname: section
        property string labelname: section
        property bool open: true

        onOpenChanged: {
            open?progressIcon.source = "artwork/DownArrow.png":progressIcon.source = "artwork/RightArrow.png"
        }

        MouseArea {
            width: parent.width
            height: parent.height
            anchors.fill: parent

            onClicked: {
                groupedList.userChangingIndex = true;
                itemdelegate.open = !itemdelegate.open
                groupedList.openShutSubgroup(section, itemdelegate.open)
                //console.log("Open/Shut items below")
                groupedList.userChangingIndex = false;
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
            id: progressfiller
            width: units.gu(22)
            anchors.left: grouptext.right
        }

        Text {
            id: progresstext

            property int totalTests: groupedList.getTotalTests(section)
            property int testCnt: groupedList.curTest
            property bool inTest: (section === groupedList.curSectionTested)


            text: {inTest && !groupedList.testsComplete ? testCnt + " of " + totalTests: ""}
            width: units.gu(10)
            anchors.left:  progressfiller.right
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
            color: "green"
            font.bold : true
        }

        Image {
            id: statusicon
            property int testStatus: {
                if (!progresstext.inTest)
                    return groupedList.groupStatus(section);
                return 0;
            }


            width: units.gu(3)
            height: units.gu(3)

            sourceSize.width: parent.width
            sourceSize.height: parent.height

            anchors{
                left: progressfiller.right
                verticalCenter: parent.verticalCenter
                leftMargin: units.gu(3)
            }
            source: ""

            onTestStatusChanged: {
                // TODO these number are made up, change to what comes out of plainbox
                switch (testStatus){
                case 0:
                    // not executed
                    source = ""
                    break;
                case 1:
                    source = "./artwork/skipped.svg"
                    break;
                case 2:                 // pass
                    source = "./artwork/passed.svg"
                    break;
                case 3:                 // fail
                    source = "./artwork/failed.svg"
                    break;
                case 4:                 // error
                    source = "./artwork/error.svg"
                    break;
                case 5:                 // user info required
                    source = "./artwork/userreq.svg"
                    break;
                default:
                    source = ""
                    break;
                }

            }

        }
        ListItem.ThinDivider {}
    }
}

