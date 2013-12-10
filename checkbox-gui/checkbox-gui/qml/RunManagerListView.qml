/*
 * This file is part of Checkbox
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

        // The List of Tests
        ListView {
            id: groupedList
            width: parent.width
            height:units.gu(7) * (groupedList.count - groupedList.closedCount)
            interactive: false
            model: testListModel

            // Tree view expansion/collapse support properties
            property int sectionCount: 0                // contain the number of sections for calculating height
            property int closedCount: 0                 // contains number of closed items for calculating height
            property bool userChangingIndex: false      //  indicates if user is changing index so 1 of 4 heading doesn't get messed up
            property string curSectionTested: currentSection // which section is currently under test
            property int curTest: 0                     // test index of test in relation to section
            property int hiddenCount: 0                 // the number of unchecked boxes from Test Selection. We dont show these ever

            delegate: RunManagerTestDelegate {}

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

            // Counts all the hidden items so we get the listview height correct
            function countHiddenItems() {
                var count = 0;

                // We need to find the index for the item passed in as item_id
                for (var i = 0; i < testListModel.count; i++)
                {
                    var item = testListModel.get(i);

                    if (item.check === "true") {
                        // do nothing, this is shown
                    } else {
                        count++;
                    }
                }
                return count;
            }

            //  Open/Close groups
            function openShutSubgroup(item_id, sel){
                var oldCurrent = currentIndex;
                currentIndex = -1

                // We need to find the index for the item passed in as item_id
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var cI = groupedList.contentItem.children[i];

                    var top_depth = cI.my_depth;

                    if (cI === item_id) {
                        // ok, so now we hide/make visible the remaining items
                        // which have a depth greater than our current depth

                        for (var j = i+1; j < groupedList.contentItem.children.length; j++) {
                            // check this item has a greater depth than the top item
                            var cur_depth = groupedList.contentItem.children[j].my_depth;

                            // Should we hide this item?
                            if (top_depth < cur_depth) {
                                // Yes, because its clearly deeper
                                var hideItem = groupedList.contentItem.children[j];
                                hideItem.visible = sel;
                                hideItem.height = sel? units.gu(7):units.gu(0);
                                if (sel)
                                    closedCount--;
                                else
                                    closedCount++;

                            } else {
                                // we must have reached the end, so return
                                return;
                            }
                        }

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

    // Runs when this ListView is fully initialised
    Component.onCompleted:{
        groupedList.sectionCount = groupedList.getSectionCount()

        // Update the number counted to get the right height
        groupedList.hiddenCount = groupedList.countHiddenItems();

        groupedList.height = units.gu(7) * (groupedList.count - groupedList.closedCount - groupedList.hiddenCount)
        listflick.contentHeight = groupedList.height

        /* kick off the real tests now */
        console.log("Start Testing")
        guiEngine.RunJobs();
    }
}
