/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
 * - Andrew Haigh <andrew.haigh@cellsoftware.co.uk>
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

    property alias itemindex: groupedList.currentIndex              // use this to change the current selection
    property alias curSectionTested: groupedList.curSectionTested   // used by suite delegate to display 1 of 4 when tests are executed
    property alias curTest: groupedList.curTest                     // used by suite delegate to display first number of 1 of 4

    color: "white"
    height: parent.height
    width: parent.width



    Flickable {
        id: listflick
        anchors.fill: parent
        height: parent.height
        contentHeight: groupedList.height
        boundsBehavior : Flickable.StopAtBounds
        clip: true
        interactive: true

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

            property int sectionCount: 0                // contain the number of sections for calculating height
            property int closedCount: 0                 // contains number of closed items for calculating height
            property bool userChangingIndex: false      //  indicates if user is changing index so 1 of 4 heading doesn't get messed up
            property string curSectionTested: currentSection // which section is currently under test
            property int curTest: 0                     // test index of test in relation to section

            interactive: false
            width: parent.width
            height:units.gu(7) * (groupedList.count + groupedList.sectionCount - groupedList.closedCount)

            model: testListModel
            highlight: highlight
            highlightFollowsCurrentItem: true

            delegate: RunManagerTestDelegate {}

            section {
                property: "group"
                criteria: ViewSection.FullString
                delegate: RunManagerSuiteDelegate{}
            }


            Component.onCompleted:{
                sectionCount = getSectionCount()
            }

            onCurrentIndexChanged: {
                // This code is used for counting up tests in the section for 1 of 5 header
                // when incrementing through test.  If index is being changed
                // by the user, don't mess up the group summary
                if (!userChangingIndex){
                    if (currentIndex != -1){
                        var item = testListModel.get(currentIndex);
                        if (item.group === groupedList.curSectionTested){
                            groupedList.curTest++;
                        }
                        else {
                            groupedList.curSectionTested = item.group
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
                        if (sel)
                            closedCount--;
                        else
                            closedCount++;
                    }
                }
                currentIndex = oldCurrent;
            }

            // counts the total test in the group
            function getTotalTests(groupName){
                var testcnt = 0
                for (var i = testListModel.count - 1; i >= 0; i--){
                    var item = testListModel.get(i);
                    if (item.group === groupName)
                        testcnt++;
                }
                return testcnt;
            }

            function groupStatus(section){
                var grpstatus = 0
                for (var i = testListModel.count - 1; i >= 0; i--){
                    var item = testListModel.get(i);
                    if (item.group === section){
                        grpstatus = item.groupstatus;
                        i = -1;
                    }
                }
                return grpstatus
            }


            function getSectionCount(){
                // if this is the first time called, count the number of sections
                var secCnt = sectionCount
                if (secCnt === 0){
                    var curItem = testListModel.get(0);
                    var curSec = curItem.group;
                    secCnt = 1;
                    for (var i = 1; i < testListModel.count; i++){
                        curItem = testListModel.get(i);
                        if (curItem.group !== curSec){
                            curSec = curItem.group
                            secCnt++;
                        }
                    }
                }
                return secCnt;
            }

        }
    }
    Scrollbar {
        flickableItem: listflick
        align: Qt.AlignTrailing
    }
}



