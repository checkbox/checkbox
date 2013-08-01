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
import Ubuntu.Components.Popups 0.1
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
            height: units.gu(7) * (groupedList.count - groupedList.closedCount)
            interactive: false
            model: testListModel

            property int sectionCount: 0// this will contain the number of sections
            property int closedCount: 0 // this contains nuber of closed items
            property bool displayWarnings: true

            delegate: TestSelectionTestDelegate {}

            highlight: highlight
            highlightFollowsCurrentItem: true

            Component.onCompleted: {
                testdetails.testItem = testListModel.get(currentItem);
                sectionCount = getSectionCount()
                setListSummary();
            }

            function showWarning(caller_button){
                if (displayWarnings === true)
                    PopupUtils.open(warning_dialog, caller_button);
            }

            // functions to do something across the whole list

            // select/deselect all items in the list
            function selectAll(sel){
                for (var i = testListModel.count - 1; i >=0; i--)
                    testListModel.setProperty(i, "check", sel);

                // make sure the UI is updated
                var oldCurrent = currentIndex
                currentIndex = -1
                for (var j = 0; j < groupedList.contentItem.children.length; j++){
                    var curItem = groupedList.contentItem.children[j];
                    curItem.checked = sel;
                }
                currentIndex = oldCurrent

                // reset the summary
                setListSummary()
            }


            // when a group item is checked/unchecked the subitems are checked/unchecked
            function selectGroup(groupName, sel){
                // select in the model
                for (var i = testListModel.count -                                 1; i >=0; i--){
                   var item = testListModel.get(i);
                    if (item.group === groupName)
                        testListModel.setProperty(i, "check", sel);
                }

                // make sure data is updated on the UI
                var oldCurrent = currentIndex
                currentIndex = -1
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var curItem = groupedList.contentItem.children[i];
                    if (curItem.groupname === groupName)
                        curItem.checked = sel;
                }
                currentIndex = oldCurrent
                setListSummary()
            }

            // determines if one or more subitems are checked
            // if at least one subitem is checked, the group is checked
            function setGroupCheck(item_id){
                var oldCurrent = currentIndex
                currentIndex = -1

                // We need to find the index for the item passed in as item_id
                for (var i = 0; i < groupedList.contentItem.children.length; i++) {
                    var cI = groupedList.contentItem.children[i];

                    var top_depth = cI.my_depth;

                    if (cI === item_id) {
                        // Now, we must make its children checked/unchecked as needed
                        // ok, so now we hide/make visible the remaining items
                        // which have a depth greater than our current depth

                        for (var j = i+1; j < groupedList.contentItem.children.length; j++) {

                            // check this item has a greater depth than the top item
                            var cur_depth = groupedList.contentItem.children[j].my_depth;

                            // Should we check this item?
                            if (top_depth < cur_depth) {
                                // Yes, because its deeper
                                var thisItem = groupedList.contentItem.children[j];
                                thisItem.checked = cI.checked;
                            } else {
                                // we must have reached the end, so return
                                return;
                            }
                        }
                    }
                }
                currentIndex = oldCurrent;

            }

            // Add up all the selected tests in a group
            function getEstimatedTime(section){
                var start = new Date();
                var estTimeStr = "";
                var estTimeInt=0;
                var foundGroup = false;  // list is ordered in groups, after whole group found return

                for (var i = 0; i <testListModel.count; i++)
                {
                    var curItem = testListModel.get(i);

                    //console.log("curItem.group:", curItem.group, "check", curItem.check)
                    if (curItem.group === section && curItem.check === "true"){
                        foundGroup = true;
                        estTimeInt = parseInt(curItem.duration) + parseInt(estTimeInt);
                    }
                    if (foundGroup && curItem.group != section)
                        i = testListModel.count;

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
                var end = new Date();
                console.log("Time for estimated groups:", section, end.getMilliseconds() - start.getMilliseconds());
                return  estTimeStr;
            }

            //  Open/Close gruops
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

            function updateListSummary(testItem, sel){
                if (sel){
                    summary.totalTests += 1;
                    summary.totalTimeEst = parseInt(summary.totalTimeEst ) + parseInt(testItem.duration);
                    if (testItem.type === "Manual")
                        summary.totalManualTests += 1;
                }
                else {
                    summary.totalTests -= 1;
                    summary.totalTimeEst = parseInt(summary.totalTimeEst ) - testItem.duration;
                    if (testItem.type === "Manual")
                        summary.totalManualTests -= 1
                 }
            }


            function setListSummary(){
                var start = new Date();
                // TODO count how many manuals testListModel
                var testCnt = 0;
                var manualCnt = 0;

                var estTimeInt=0;

                for (var i = testListModel.count - 1; i >=0; i--)
                {
                    var curItem = testListModel.get(i);
                    if ( curItem.check === "true"){
                        testCnt++;
                        if (curItem.type === "Manual")
                            manualCnt++;
                        estTimeInt = parseInt(curItem.duration) + parseInt(estTimeInt);
                    }
                }
                summary.totalTests = testCnt;
                summary.totalManualTests = manualCnt;
                summary.totalTimeEst =  estTimeInt;
                var end = new Date();
                console.log("Time for summary:", end.getMilliseconds() - start.getMilliseconds());

            }

            function getSectionCount(){
               var start = new Date();
                // if this is the first time called, find all sections
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
                var end = new Date();
                console.log("Time for Section Count:", end.getMilliseconds() - start.getMilliseconds());
                return secCnt;
            }
        }
    }

    Scrollbar {
        flickableItem: listflick
        align: Qt.AlignTrailing
    }

    Component {
        id: warning_dialog
        WarningDialog{
            text: i18n.tr("Deselecting tests may reduce your ability to detect potential problems with the device driver.");
            showOK: true
            showCancel: false
            showContinue: false
            showCheckbox: true

            onOk: {
                if (isChecked)
                    groupedList.displayWarnings = false;
                console.log("ok clicked");
            }
        }
    }
}



