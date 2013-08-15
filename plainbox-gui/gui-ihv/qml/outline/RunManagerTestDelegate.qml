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
import "./artwork"

/* In order to simulate a tree with ListView, we end up having to embed some knowledge
  in the display component and the underlying model. Qt 5.1 was meant to have a QML TreeView
  but it doesnt seem to have transpired :(

 */

Component {
    id: testDelegate

    Item{
        id: testitem
        width: parent.width
        height: units.gu(7)

        property string groupname: group
        property string labelname: testname

        // These properties help to simulate the treeview
        property bool open: true
        property bool is_branch: branch
        property int my_depth: depth

        onOpenChanged: {
            open?openshutIcon.source = "artwork/DownArrow.png":openshutIcon.source = "artwork/RightArrow.png"
        }

        MouseArea {
            id: openshutbutton
            width: parent.width;
            height: parent.height
            anchors.fill: parent

            onClicked: {
                groupedList.userChangingIndex = true;
                groupedList.currentIndex = index;
                groupedList.userChangingIndex = false;

                testitem.open = !testitem.open
                groupedList.openShutSubgroup(testitem, testitem.open)

            }
        }

        Item {
            id: testitemview
            anchors.fill: parent

            Item {
                id: filler
                // this is our indentation level. we get this out of the model
                width: (depth * openshutIcon.width) + units.gu(2)
            }

            Image {
                id: openshutIcon
                source: "artwork/DownArrow.png"
                width: units.gu(2)
                height: units.gu(2)
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: filler.right

                }
                opacity: enabled ? 1.0 : 0.5

                visible: is_branch
                enabled: is_branch
            }

            Text {
                id: namelabel
                text: testname
                elide: Text.ElideRight

                anchors.verticalCenter: parent.verticalCenter

                anchors.left: openshutIcon.right
                anchors.leftMargin: units.gu(2)

                anchors.right: statusicon.left
                anchors.rightMargin: units.gu(7.5)
            }


            Image {
                id: statusicon
                property int testStatus: runstatus// TODO this should be coming from the testitem status

                width: units.gu(3)
                height: units.gu(3)

                anchors.right: timelabel.left
                anchors.rightMargin: units.gu(6)

                anchors.verticalCenter: parent.verticalCenter

                source: ""



                MouseArea {
                    anchors.fill: parent

                    onClicked:{
                        // set user so the iterating tests continue
                        // change currentindex to cause selection to move
                        groupedList.userChangingIndex = true;
                        groupedList.currentIndex = index

                        switch (statusicon.testStatus){

                        case 2:                         // passed
                            PopupUtils.open(log_viewer, statusicon);
                            break;
                        case 3:                         // failed
                        case 4:                         // error
                            PopupUtils.open(log_viewer_with_trouble, statusicon);
                            break;
                        case 5:                         // user interaction req.
                            PopupUtils.open(manual_dialog, statusicon);
                            break;
                        case 1:
                        default://skipped
                            break;
                        }

                        // TODO remove this --- this is just to try out the different icons behaviour
                        // THIS should NOT really happen!!!!
                        //if (statusicon.testStatus < 6)
                        //    statusicon.testStatus++
                        //else
                        //    statusicon.testStatus = 1
                        // TODO remove items above to the TODO!!!

                        groupedList.userChangingIndex = false;                    }
                }

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

            Text {
                id: timelabel
                text: {!elapsedtime ? "" : utils.formatElapsedTime(elapsedtime)}
                width: units.gu(6)
                anchors.right: rerunicon.left
                anchors.rightMargin: units.gu(9)
                anchors.verticalCenter: parent.verticalCenter
                horizontalAlignment: Text.AlignRight

           }

            Image {
                id: rerunicon
                property int rerunStatus: !runstatus?0:1 // TODO this should be coming if the test has run or not
                                                  // currently assumes 0 = not run yet, 1 == completed 2 == queued for rerun

                width: units.gu(3)
                height: units.gu(3)

                anchors.right: detailsicon.left
                anchors.rightMargin: units.gu(9)
                anchors.verticalCenter: parent.verticalCenter

                source: ""

                MouseArea {
                    anchors.fill: parent
                    onClicked:{
                        groupedList.userChangingIndex = true;
                        groupedList.currentIndex = index

                        if (rerunicon.rerunStatus == 1)
                           rerunicon.rerunStatus = 2;

                        groupedList.userChangingIndex = false;
                    }
                 }

                onRerunStatusChanged:{
                    if (rerunStatus == 0)                       // not run
                        source = ""
                    if (rerunStatus == 1)                      // completed
                        source = "./artwork/rerun.svg"
                    else if (rerunStatus == 2){                 // queued for rerun
                        source = "./artwork/rerunq.svg"
                        // reset other icons to blank
                        statusicon.testStatus = 0
                        detailsicon.detailsStatus = false
                        timelabel.text = ""
                        testListModel.setProperty(index, "groupstatus", 0);   // group
                    }
                }
            }

            Image {
                id: detailsicon
                property bool detailsStatus: {!runstatus?false:true} // TODO this should be coming if the test has run or not
                                                  // currently assumes 0 = not run yet, 1 == completed

                width: units.gu(3)
                height: units.gu(3)

                anchors.right:  parent.right
                anchors.rightMargin: units.gu(7.5)

                anchors.verticalCenter: parent.verticalCenter

                source: ""

                MouseArea {
                    anchors.fill: parent

                    onClicked:{
                        groupedList.userChangingIndex = true;
                        groupedList.currentIndex = index;
                        //cmdTool.exec("gedit", logfileName)

                        // TODO change this back to the log_viewer, this opens the manual_dialog for testing only!
                        //PopupUtils.open(log_viewer, detailsicon);
                        if (detailsicon.detailsStatus == true)
                            PopupUtils.open(manual_dialog, detailsicon);
                        groupedList.userChangingIndex = false;
                    }
                }

                onDetailsStatusChanged:{
                    if (detailsStatus)               // completed
                        source = "./artwork/details.svg"
                    else                            // not run yet
                        source = ""
                }

            }
        }

        // Item dividing line
        ListItem.ThinDivider {}

        Component {
            id: log_viewer
            LogViewer{
//                //  Re-insert this for other/future versions of the GUI
//                showTroubleShootingLink: false
                text:testname
                logText: description
            }
        }

//        //  Re-insert this for other/future versions of the GUI
//        Component {
//            id: log_viewer_with_trouble
//            LogViewer{
//                showTroubleShootingLink: true
//                text:testname
//                logText: description
//            }
//        }

        Component {
            id: manual_dialog
            ManualInteractionDialog{
                testItem: testListModel.get(index);
            }
        }
    }
}

