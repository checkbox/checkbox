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





    Rectangle {
        color: "white"
        height: parent.height


        function selectAll(sel) {
            groupedList.selectAll(sel);
        }

        Flickable {
        id: listflick
        anchors.fill: parent
        height: parent.height
        width: parent.width
        clip: true
        contentHeight: groupedList.height
        boundsBehavior : Flickable.StopAtBounds



        ListView {
            id: groupedList
            width: parent.width
            height: units.gu(12) * groupedList.count
            interactive: false
            model: testSuiteModel



 /*           delegate:  ListItem.Standard {
                id: listitem

                progression: true
                property string groupname: group
                property alias checked: itemcheckbox.checked
                text: i18n.tr("       " + testname)
                control: CheckBox {
                    id: itemcheckbox
                    anchors.verticalCenter: parent.verticalCenter
                    checked: check
                    onClicked: {
                        testSuiteModel.setProperty(index, "check", checked);
                        if (checked == false)
                            groupedList.turnGroupOff(group)
                    }
                }


            }*/
            delegate: Item{
                width: parent.width
                height: units.gu(7)
                property string groupname: group
                property alias checked: itemcheckbox.checked
                property string labelname: testname


                MouseArea {
                    width: parent.width - itemcheckbox.width
                    height: parent.height
                    anchors.right: parent.right

                    onClicked: console.log("Show Details")
                }

                Label {
                    id: filler
                    text: "            "
                }

                CheckBox {
                    id: itemcheckbox
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: filler.right
                    anchors.leftMargin: units.gu(2)
                    checked: check
                    onClicked: {
                        testSuiteModel.setProperty(index, "check", checked);
                        //if (checked == false)
                        //    groupedList.turnGroupOff(group)
                    }
                }


                Text {
                    text: testname
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: itemcheckbox.right
                    anchors.leftMargin: units.gu(1)
                }


                Image {
                    id: progressIcon
                    source: "ListItemProgressionArrow.png"
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                    }

                    opacity: enabled ? 1.0 : 0.5
                }
                ListItem.ThinDivider {}
            }
/*
            section.property: "group"
            section.criteria: ViewSection.FullString
            section.delegate: ListItem.Standard {
                id: groupitem
                progression: false
                text: i18n.tr(section)
                property alias groupname: groupitem.text
                property alias checked: groupcheckbox.checked
                control: CheckBox {
                    id: groupcheckbox
                    anchors.verticalCenter: parent.verticalCenter
                    checked: true
                    onClicked: {
                        groupedList.selectGroup(section, checked)
                    }
                }
            }WELCOME
*/
            section.property: "group"
            section.criteria: ViewSection.FullString
            section.delegate: Item {
                id: itemdelegate
                width: parent.width
                height: units.gu(7)
                property string groupname: section
                property alias checked: groupcheckbox.checked
                property string labelname: section
                property bool open: true

                MouseArea {
                    width: parent.width - groupcheckbox.width
                    height: parent.height
                    anchors.right: parent.right

                    onClicked: {
                        itemdelegate.open = !itemdelegate.open
                        groupedList.openShutSubgroup(section, itemdelegate.open)
                        console.log("Open/Shut items below")
                        }
                }

                Label {
                    id: groupfiller
                    text: " "
                }

                CheckBox {
                    id: groupcheckbox
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: groupfiller.right
                    anchors.leftMargin: units.gu(1)
                    checked: true
                    onClicked: {
                        groupedList.selectGroup(section, checked)
                    }
                }


                Text {
                    id: grouptext
                    text: section
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: groupcheckbox.right
                    anchors.leftMargin: units.gu(1)
                }
                ListItem.ThinDivider {}
            }

            function selectAll(sel){
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];
                    //console.log(i,": ", curItem, "=", curItem.text);
                    curItem.checked = sel;
                }
            }

            function selectGroup(groupName, sel){
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];
                    //console.log(i,": ", curItem, "=", curItem.groupname);

                    if (curItem.groupname === groupName)
                        curItem.checked = sel;
                }
            }

            function turnGroupOff(groupName){
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];
                    //console.log(i,": ", curItem, "=", curItem.text);

                    if (curItem.labelname === groupName)
                        curItem.checked = false;
                }
            }

            function openShutSubgroup(groupName, sel){
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];
                    console.log(i,": ", curItem, "=", curItem.groupname);
                    console.log(i,": ", sel, "=", sel, " height = ", curItem.height);

                    if (curItem.groupname === groupName && curItem.labelname != groupName){

                        curItem.height = sel? units.gu(7):units.gu(0);
                        curItem.visible = sel;
                    }
                }
            }
}


    }

    Scrollbar {
        flickableItem: listflick
        align: Qt.AlignTrailing
    }
}



