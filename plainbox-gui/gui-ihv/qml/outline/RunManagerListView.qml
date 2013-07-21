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
    property alias currentSection: groupedList.currentSection
    property alias curSectionInTest: groupedList.curSectionInTest
    property alias curTest: groupedList.curTest
    property bool testsComplete: false     // this indicates all testings is complete

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

            property string curSectionInTest: currentSection // init this to the first section
            property int curTest: 0 // counts up each test in the section

            onCurrentIndexChanged: {
                if (!testsComplete){
                if (currentIndex != -1){
                    var item = testSuiteModel.get(currentIndex);
                    if (item.group === groupedList.curSectionInTest){
                        groupedList.curTest++;
                    }
                    else {
                        groupedList.curSectionInTest = item.group
                        groupedList.curTest = 1
                    }
                }
                }
            }




            //  Open/Close gruops
            function openShutSubgroup(groupName, sel){
                var oldCurrent = currentIndex;
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];

                    if (curItem.groupname === groupName && curItem.labelname !== groupName){
                        curItem.height = sel? units.gu(7):units.gu(0);
                        curItem.visible = sel;
                        groupedList.height += sel?units.gu(7):-units.gu(7)
                    }
                }
                currentIndex = oldCurrent;
            }

            // TODO --- move to C++ function
            // counts the total test in the group
            function getTotalTests(groupName){
                var testcnt = 0
                for (var i = testSuiteModel.count - 1; i >= 0; i--){
                    var item = testSuiteModel.get(i);
                    if (item.group === groupName)
                        testcnt++;
                }
                return testcnt;
            }

            function isInTest(section){
                var item = testSuiteModel.get(currentIndex);
                if (item.groupName === currentSection)
                    return true;
                return false;
            }

            function groupStatus(section){
                var grpstatus = 0
                for (var i = testSuiteModel.count - 1; i >= 0; i--){
                    var item = testSuiteModel.get(i);
                    if (item.group === section){
                        grpstatus = item.groupstatus;
                        i = -1;
                    }
                }
                return grpstatus
            }
        }


    }
    Scrollbar {
        flickableItem: listflick
        align: Qt.AlignTrailing
    }}



