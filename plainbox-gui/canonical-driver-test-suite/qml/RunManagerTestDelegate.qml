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

        property string groupname: group
        property string labelname: testname

        // visibility - now follows what the user selected in test selection
        visible: check
        height: check ? units.gu(7) : units.gu(0);

        // These properties help to simulate the treeview
        property bool open: true
        property bool is_branch: branch
        property int my_depth: depth

        property int icon_size_gu: 4    // Adjustable icon size based on this

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
                anchors.rightMargin: units.gu(9-(icon_size_gu/2))
            }


            Image {
                id: statusicon
                property int testStatus: runstatus// TODO this should be coming from the testitem status

                width: units.gu(icon_size_gu)
                height: units.gu(icon_size_gu)

                sourceSize.width: parent.width
                sourceSize.height: parent.height

                anchors.right: timelabel.left
                anchors.rightMargin: units.gu(6)

                anchors.verticalCenter: parent.verticalCenter

                source: ""

                onTestStatusChanged: {
                    // Update the other icons once the status is run
                    if (testStatus !== 0 /* PBJobResult_NotRun*/) {
                        // reset the re-run action if appropriate
                        rerunicon.rerunStatus = 1;

                        // Update the timelabel
                        timelabel.text = utils.formatElapsedTime(elapsedtime);
                    }


                    // These numbers match PBTreeNode.h:PBJobResult enums
                    switch (testStatus){
                    case 0: // PBJobResult_NotRun
                        // not executed
                        source = ""
                        break;
                    case 1: // PBJobResult_Skip
                        source = "./artwork/pictogram-skip-orange-hex.svg"
                        break;
                    case 2: // PBJobResult_Pass
                        source = "./artwork/pictogram-pass-green-hex.svg"
                        break;
                    case 3: // PBJobResult_Fail
                        source = "./artwork/pictogram-fail-red-hex.svg"
                        break;
                    case 4: // PBJobResult_Error (doesnt seem to be used/useful?)
                        source = "./artwork/error.svg" // todo
                        break;
                    case 5: // PBJobResult_UserInteraction
                        source = "./artwork/userreq.svg" // todo
                        break;
                    case 6: // PBJobResult_DepsNotMet
                        source = "./artwork/pictogram-skip-grey-hex.svg"
                        break;
                    case 7: // PBJobResult_Running
                        source = ""
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
                anchors.rightMargin: units.gu(12-icon_size_gu)
                anchors.verticalCenter: parent.verticalCenter
                horizontalAlignment: Text.AlignRight

           }

            Image {
                id: rerunicon
                property int rerunStatus: !runstatus?0:1 // TODO this should be coming if the test has run or not
                                                  // currently assumes 0 = not run yet, 1 == completed 2 == queued for rerun

                width: units.gu(icon_size_gu)
                height: units.gu(icon_size_gu)

                sourceSize.width: parent.width
                sourceSize.height: parent.height

                anchors.right: detailsicon.left
                anchors.rightMargin: units.gu(12-icon_size_gu)
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
                        source = "./artwork/pictogram-execute-grey-hex.svg"
                    else if (rerunStatus == 2){                 // queued for rerun
                        source = "./artwork/pictogram-reexecute-obergine-hex.svg"
                        // reset other icons to blank
                        timelabel.text = ""
                        testListModel.setProperty(index, "groupstatus", 0);   // group
                        testListModel.setProperty(index,"runstatus",0); // As if its not run

                        testListModel.setProperty(index,"rerun",1); // mark this for rerun

                        runbuttons.rerunButtonEnabled = true;
                    }
                }
            }

            Image {
                id: detailsicon
                property bool detailsStatus: {!runstatus?false:true} // TODO this should be coming if the test has run or not
                                                  // currently assumes 0 = not run yet, 1 == completed

                width: units.gu(icon_size_gu)
                height: units.gu(icon_size_gu)

                sourceSize.width: parent.width
                sourceSize.height: parent.height

                anchors.right:  parent.right
                anchors.rightMargin: units.gu(9-(icon_size_gu/2))

                anchors.verticalCenter: parent.verticalCenter

                source: ""

                MouseArea {
                    anchors.fill: parent

                    onClicked:{
                        groupedList.userChangingIndex = true;
                        groupedList.currentIndex = index;

                        detailsicon.source = "./artwork/pictogram-articles-grey-hex.svg"
                        // start timer with 1 ms delay,
                        // this has to be enough for the GUI to redraw
                        myTimer.start()

                        groupedList.userChangingIndex = false;
                    }
                }

                onDetailsStatusChanged:{
                    if (detailsStatus)               // completed
                        source = "./artwork/pictogram-articles-orange-hex.svg"
                    else                            // not run yet
                        source = ""
                }
            }

        Timer {
            id: myTimer
            interval: 1; running: false; repeat: false
            onTriggered: {
                // Open the log viewer
                PopupUtils.open(log_viewer)
                detailsicon.source = "./artwork/pictogram-articles-orange-hex.svg"
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
               jobPath: objectpath
               title: testname
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

