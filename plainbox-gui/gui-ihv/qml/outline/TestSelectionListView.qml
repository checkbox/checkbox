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
    id: suitetestlist
    color: "white"
    height: parent.height
    width: parent.width


    function selectAll(sel) {
        groupedList.selectAll(sel);
    }

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
            width: parent.width
            height: units.gu(12) * groupedList.count + units.gu(1)
            interactive: false
            model: testSuiteModel

            delegate: TestSelectionTestDelegate {}

            section {
                property: "group"
                criteria: ViewSection.FullString
                delegate: TestSelectionSuiteDelegate{}
            }

            highlight: highlight
            highlightFollowsCurrentItem: true

            Component.onCompleted: testdetails.testItem = testSuiteModel.get(currentItem);

            // functions to do something across the whole list

            // select/deselect all items in the list
            function selectAll(sel){
                for (var i = testSuiteModel.count - 1; i >=0; i--)
                    testSuiteModel.setProperty(i, "check", sel);

                // this is to select the group items and to make sure data is updated
                var oldCurrent = currentIndex
                currentIndex = -1
                for (var j = 0; j < groupedList.contentItem.children.length; j++){
                    var curItem = groupedList.contentItem.children[j];
                    curItem.checked = sel;
                }
                currentIndex = oldCurrent
            }


            // when a group item is checked/unchecked the subitems are checked/unchecked
            function selectGroup(groupName, sel){
                for (var i = testSuiteModel.count - 1; i >=0; i--){
                    var item = testSuiteModel.get(i);
                    if (item.group === groupName)
                        testSuiteModel.setProperty(i, "check", sel);
                }

                // this is to select the group items and to make sure data is updated
                var oldCurrent = currentIndex
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];
                    //console.log(i,": ", curItem, "=", curItem.groupname);

                    if (curItem.groupname === groupName)
                        curItem.checked = sel;
                }
                currentIndex = oldCurrent
            }

            // determines if one or more subitems are checked
            // if at least one subitem is checked, the group is checked
            function setGroupCheck(groupName){
                var oldCurrent = currentIndex
                currentIndex = -1
                var setCheck = false
                var i = groupedList.contentItem.children.length - 1

                for (;i >= 0 && setCheck === false; i--)
                {
                    var curItem = groupedList.contentItem.children[i];

                    // determine if subitem is checked
                    if (curItem.groupname === groupName && curItem.labelname !== groupName)
                        if (curItem.checked === true)
                            setCheck = true;

                }

                for (i = groupedList.contentItem.children.length - 1; i >= 0; i--)
                {
                    curItem = groupedList.contentItem.children[i];
                    if (curItem.labelname === groupName)
                        curItem.checked = setCheck

                }

                currentIndex = oldCurrent;
            }

            // If any subitems are selected, group should be selected.
            function isGroupSelected(section){
                var isSel = false;
                for (var i = testSuiteModel.count - 1; i >=0 && isSel === false; i--)
                {
                    var curItem = testSuiteModel.get(i);
                    //console.log("Section: ", section, " ", i,": ", curItem, "=", curItem.group, " check:", curItem.check);

                    if (curItem.group === section && curItem.check === "true"){
                        isSel = true;
                    }
                }
                return isSel;
            }

            // Add up all the selected tests in a group
            function getEstimatedTime(section){
                var estTimeStr = "";
                var estTimeInt=0;

                for (var i = testSuiteModel.count - 1; i >=0; i--)
                {
                    var curItem = testSuiteModel.get(i);

                    //console.log("curItem.group:", curItem.group, "check", curItem.check)
                    if (curItem.group === section && curItem.check === "true")
                        estTimeInt = parseInt(curItem.duration) + parseInt(estTimeInt);

                }
                if (estTimeInt == 0)
                    estTimeStr = "";
                else if (estTimeInt/60 < 1)
                    estTimeStr = i18n.tr("< 1 minute");
                else {
                    var durMinutes = Math.round(estTimeInt/60);
                    estTimeStr = durMinutes.toString() + i18n.tr(" minute");
                    if (durMinutes > 1)
                        estTimeStr += 's';
                }
                return  estTimeStr;
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
    }
}



