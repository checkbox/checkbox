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
    id: runmanagerrect

    property alias itemindex: groupedList.currentIndex
    property alias item: groupedList.currentItem

    color: "white"
    height: parent.height
    width: parent.width


    Flickable {
        id: listflick
        anchors.fill: parent
        height: parent.height

        clip: true
        contentHeight: groupedList.height
        boundsBehavior : Flickable.StopAtBounds


        Component {
            id: highlight
            Rectangle {
                width: groupedList.width
                height: units.gu(7)
                color: "lightsteelblue";
                radius: 5
            }
        }


        ListView {
            id: groupedList

            interactive: false
            width: parent.width

            height: units.gu(12) * testSuiteModel.count + units.gu(2)

            //boundsBehavior : Flickable.StopAtBounds
            model: testSuiteModel
            highlight: highlight
            highlightFollowsCurrentItem: true


            delegate: RunManagerTestDelegate {}

            section {
                property: "group"
                criteria: ViewSection.FullString
                delegate: RunManagerSuiteDelegate{}
            }



            //  Open/Close gruops
            function openShutSubgroup(groupName, sel){
                var oldCurrent = currentIndex;
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];
                    //console.log(i,": ", curItem, "=", curItem.groupname);
                    //console.log(i,": ", sel, "=", sel, " height = ", curItem.height);

                    if (curItem.groupname === groupName && curItem.labelname !== groupName){
                        curItem.height = sel? units.gu(7):units.gu(0);
                        curItem.visible = sel;
                        groupedList.height += sel?units.gu(7):-units.gu(7)
                    }
                }
                currentIndex = oldCurrent;
            }
        }


    }
    Scrollbar {
        flickableItem: listflick
        align: Qt.AlignTrailing
    }}



