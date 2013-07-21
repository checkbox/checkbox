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

Component {
    id: testDelegate

    Item{
        id: testitem
        width: parent.width
        height: units.gu(7)

        property string groupname: group
        property string labelname: testname


        MouseArea {
            width: parent.width;
            height: parent.height
            anchors.fill: parent

            onClicked: {
                groupedList.currentIndex = index;
            }
        }

        Item {
            id: testitemview
            anchors.fill: parent

            Item {
                id: filler
                width: units.gu(6)
            }

            Text {
                id: namelabel
                text: testname
                width: units.gu(42)
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: filler.right
            }

            Item {
                id: statusFiller
                width: units.gu(12)
                anchors.left: namelabel.right
            }

            Image {
                id: statusicon
                property int testStatus: runstatus// TODO this should be coming from the testitem status

                width: units.gu(3)
                height: units.gu(3)
                anchors.left: namelabel.right
                anchors.verticalCenter: parent.verticalCenter
                source: ""



                MouseArea {
                    anchors.fill: parent

                    onClicked:{
                        groupedList.currentIndex = index
                        if (statusicon.testStatus === 5)
                            PopupUtils.open(manual_dialog, runbuttons);

                        if (statusicon.testStatus < 6)
                            statusicon.testStatus++
                        else
                            statusicon.testStatus = 0

                    }
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

            Item {
                id: timefiller
                width: units.gu(10)
                anchors.left: statusicon.right
            }

            Text {
                id: timelabel
                text: {!elapsedtime ? "" : utils.formatElapsedTime(elapsedtime)}
                width: units.gu(10)
                anchors.left: timefiller.right
                anchors.verticalCenter: parent.verticalCenter
                horizontalAlignment: Text.AlignRight

           }

            Item {
                id: actionsfiller
                width: units.gu(12)
                anchors.left: timelabel.right
            }

            Image {
                id: rerunicon
                property int rerunStatus: !runstatus?0:1 // TODO this should be coming if the test has run or not
                                                  // currently assumes 0 = not run yet, 1 == completed 2 == queued for rerun

                width: units.gu(3)
                height: units.gu(3)
                anchors.left: actionsfiller.right
                anchors.verticalCenter: parent.verticalCenter
                source: ""

                MouseArea {
                    anchors.fill: parent
                    onClicked:{
                        groupedList.currentIndex = index
                        if (rerunicon.rerunStatus == 1)
                           rerunicon.rerunStatus = 2;
                        else if (rerunicon.rerunStatus == 2)
                            rerunicon.rerunStatus = 1;
                    }
                 }

                onRerunStatusChanged:{
                    if (rerunStatus == 1)                      // completed
                        source = "./artwork/rerun.svg"
                    else if (rerunStatus == 2){                 // queued for rerun
                        source = "./artwork/rerunq.svg"
                        // reset other icons to blank
                        statusicon.source = ""
                        detailsicon.source = ""
                        timelabel.text = ""
                        testSuiteModel.setProperty(index, "groupstatus", 0);   // reset this as if it hasn't been run yet

                    }
                    else
                        source = ""
                }
            }

            Item {
                id: detailsfiller
                width: units.gu(13)
                anchors.left: rerunicon.right
            }

            Image {
                id: detailsicon
                property bool detailsStatus: {!runstatus?false:true} // TODO this should be coming if the test has run or not
                                                  // currently assumes 0 = not run yet, 1 == completed

                width: units.gu(3)
                height: units.gu(3)
                anchors.left: detailsfiller.right
                anchors.verticalCenter: parent.verticalCenter
                source: ""

                MouseArea {
                    anchors.fill: parent

                    onClicked:{
                        groupedList.currentIndex = index;
                        gedit.launch("./qml/outline/artwork/test.txt");
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
        ListItem.ThinDivider {}
    }
}
