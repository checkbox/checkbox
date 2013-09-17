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

        // Blue Highlight Bar
        Component {
            id: highlight
            Rectangle {
                width: groupedList.width
                height: units.gu(7)
                color: "lightsteelblue";
                radius: 5
            }

        }

        // The List of Tests
        ListView {
            id: groupedList
            width: parent.width
            height: units.gu(7) * (groupedList.count - groupedList.closedCount)
            interactive: false
            model: testListModel

            // Tree view expansion/collapse support properties
            property int sectionCount: 0// this will contain the number of sections
            property int closedCount: 0 // this contains nuber of closed items
            property bool displayWarnings: true

            delegate: TestSelectionTestDelegate {}

            highlight: highlight
            highlightFollowsCurrentItem: true

            // Runs when this ListView is fully initialised
            Component.onCompleted: {
                selectAll(true)
                testdetails.testItem = testListModel.get(currentItem);
                sectionCount = getSectionCount()
                setListSummary();
            }

            function showWarning(caller_button){
                if (displayWarnings === true)
                    PopupUtils.open(warning_dialog, caller_button);
            }

            // Select/De-select all items - Called from TestSelectionButtons.qml
            function selectAll(sel){

                // show the warning if sel is false
                if(!sel) {
                    showWarning(groupedList);
                }

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

                    // cI = The item which was clicked by the user
                    var cI = groupedList.contentItem.children[i];
                    var cI_depth = cI.my_depth;

                    if (cI === item_id) {
                        /* Branch rules:

                          Branch: Set
                            Set all the leaves below us

                          Branch: Un-set
                            Un-set all the leaves below us
                         */
                        for (var j = i+1; j < groupedList.contentItem.children.length; j++) {

                            // check this item has a greater depth than the top item
                            var cur_depth = groupedList.contentItem.children[j].my_depth;

                            // Should we check this item?
                            if (cI_depth < cur_depth) {
                                // Yes, because its deeper
                                var thisItem = groupedList.contentItem.children[j];
                                thisItem.checked = cI.checked;
                            } else {
                                // we've reached the end of this branch, so stop
                                break;
                            }
                        }

                        /* Leaf rules

                            Leaf: Set
                              If any branch above us is unchecked, we must set it.

                            Leaf: Un-set
                              If all the leaves at this level are unchecked, we uncheck
                              the containing branch above us.
                        */

                        // Leaf set case. i is the current item index
                        /* we go up each level and check the box */
                        var interim_depth = cI_depth; // Track progress to the top

                        if (cI.checked) {
                            for (var j=i-1; j >= 0 ; j--) {
                                // We are going UP the list/tree now
                                var thisItem = groupedList.contentItem.children[j];
                                var cur_depth = thisItem.my_depth;

                                if (cur_depth < interim_depth) {
                                    // we have gone up another level
                                    interim_depth--;

                                    // lets check this item
                                    thisItem.checked = true;
                                }

                                // Have we reached the top-most branch?
                                if (cur_depth === 0) {
                                    // We dont need to go any further
                                    break;  // end of for(j)
                                }
                            }
                        } else {
                            // Un set rule
                            // recursive: Update parent
                            updateBranchSelection(i);
                        }
                    }
                }
                currentIndex = oldCurrent;
            }

            /* Updates the item and child items based on whether it has
              selected children.

              Arguments:
                item_index - Index into groupedList.contentItem.children[]

              */
            function updateBranchSelection(item_index) {
                // The starting point (generally the root branch)
                var curItem = groupedList.contentItem.children[item_index]
                var cI_depth = curItem.my_depth;

                // Avoid bad arguments
                if (item_index < 0) {
                    console.log("UpdateBranchSelection - Bad argument")
                    return false;
                }

                // We dont need to do anything if its a root node
                if (cI_depth === 0) {
                    return;
                }

                // we assume its not checked
                var result = false;

                /* Find the bottommost item at this level.
                  then, go up until the depth goes down by one. Then update that
                  item.

                  Example Tree as follows:

                    ...
                    [*]         <- top_Index computed below
                        [ ]     <- Newly unchecked item suppiled as item_Index
                        [*]
                        [ ]
                            [ ] <- bottom_Index computed below
                    [ ]
                    ...
                  */

                // Find bottom_Index
                var bottom_Index = item_index;
                for (var i = item_index+1; i < groupedList.contentItem.children.length; i++) {
                    var this_Item = groupedList.contentItem.children[i];
                    var tI_depth = this_Item.my_depth;

                    // Have we reached the bottom of the tree?
                    if (tI_depth < cI_depth) {
                        bottom_Index = i;
                        break;
                    }

                    // Is this a root node?
                    if (tI_depth === 0) {
                        bottom_Index = i;
                        break;
                    }
                }

                /* we should move up bottom_Index to be the bottom of our tree
                 * and not the start of the next tree
                 */
                bottom_Index--;

                /* top_Index is checked if _anything above bottom_Index
                 * is selected.
                 */
                var result = false; // assume its unchecked
                var top_Index = item_index;
                for(var i = bottom_Index; i>=0; i--) {
                    // have we reached the branch holding these children?
                    if (groupedList.contentItem.children[i].my_depth < cI_depth) {
                        // yes
                        top_Index = i;
                        break;
                    }

                    if (groupedList.contentItem.children[i].checked ) {
                        result = true;  // at least one item is true
                    }
                }

                // Now update the checked status of this box
                groupedList.contentItem.children[top_Index].checked = result;

                // Now, if we havent reached the root, do the next level
                if (groupedList.contentItem.children[top_Index].my_depth >0 ) {
                    updateBranchSelection(top_Index);
                }
            }

            // Update the underlying model based on the UI display of check/uncheck items
            function updateListModel() {

                // do it for each item
                for (var i=0; i < groupedList.contentItem.children.length; i++) {
                    var thisItem = groupedList.contentItem.children[i];
                    var sel = thisItem.checked;

                    testListModel.setProperty(i, "check", sel);
                }
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

            //  Open/Close groups
            function openShutSubgroup(item_id, sel){
                var oldCurrent = currentIndex;
                currentIndex = -1

                // We need to find the index for the item passed in as item_id
                for (var i = 0; i < groupedList.contentItem.children.length; i++)
                {
                    var cI = groupedList.contentItem.children[i];

                    var cI_depth = cI.my_depth;

                    if (cI === item_id) {
                        // ok, so now we hide/make visible the remaining items
                        // which have a depth greater than our current depth

                        for (var j = i+1; j < groupedList.contentItem.children.length; j++) {
                            // check this item has a greater depth than the top item
                            var cur_depth = groupedList.contentItem.children[j].my_depth;

                            // Should we hide this item?
                            if (cI_depth < cur_depth) {
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

            // Update List Summary
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

            // Set List Summary
            function setListSummary(){
                var start = new Date();

                // TODO count how many manuals testListModel
                var testCnt = 0;
                var manualCnt = 0;

                var estTimeInt=0;

                // We count from the bottom up, and we dont count anything
                // that is a "branch" as this is a local/group kind of thing
                for (var i = testListModel.count - 1; i >=0; i--)
                {
                    var curItem = testListModel.get(i);
                    // is it a branch? if so we dont count it
                    if (curItem.branch === "0") {
                        // not a branch
                        if ( curItem.check === "true"){
                            testCnt++;
                            if (curItem.type === "Manual")
                                manualCnt++;
                            estTimeInt = parseInt(curItem.duration) + parseInt(estTimeInt);
                        }
                    }
                }
                summary.totalTests = testCnt;
                summary.totalManualTests = manualCnt;
                summary.totalTimeEst =  estTimeInt;

                /* We should call into guiengine to find out the number of
                 * implicit tests (really we will get a count of ALL of them...
                 */

                // Ok, we shouldnt need to do this tooo often!

                // Update the really selected testsuitelist
                testitemFactory.GetSelectedRealJobs(testListModel);

                // Mark all the jobs for one run-through
                testitemFactory.GetSelectedRerunJobs(testListModel);

                // Prep the jobs (we cant start them without this)
                var total_generated_tests = guiEngine.PrepareJobs();

                // All the above lets us count the number of real jobs
                summary.totalImplicitTests = total_generated_tests - summary.totalTests;

                var total_duration = guiEngine.GetEstimatedDuration();
                console.log("Estimated duration (automated tests):", total_duration["automated_duration"], "s")
                console.log("Estimated duration (manual tests)   :", total_duration["manual_duration"], "s")

                // Not strictly needed here
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
