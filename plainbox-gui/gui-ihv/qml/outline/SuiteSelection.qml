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
import GuiEngine 1.0
import Ubuntu.Components 0.1
import Ubuntu.Components.Popups 0.1
import Ubuntu.Layouts 0.1
import Ubuntu.Components.ListItems 0.1 as ListItem
import "."



MainView {
    width: units.gu(80)
    height: units.gu(90)

    Page {
        title: "IHV Driver Testing"
        Progress {
            id: progress
            title: i18n.tr("Testing...")
            width: parent.width - units.gu(10)
            anchors.horizontalCenter: parent.horizontalCenter
        }

       // Rectangle {
        //    id: rectangle
        //    anchors.centerIn: parent
        //    width: parent.width
        //    height: parent.height
            //color: UbuntuColors.coolGrey
       // }

        MainButtons {
            id: actionbuttons
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: progress.bottom
            anchors.topMargin: units.gu(8)

            onActionChanged: {
                switch (actionState){
                case "SELECTION":
                    console.log("SELECTION selected")
                    progress.title = "Getting tests..."
                    progress.value =  0
                    progress.indeterminate = false;
                    progress.visible = true
                    break;
                case "RUN":
                    console.log("RUN selected")
                    progress.title = "Running..."
                    progress.visible = true
                    progress.indeterminate = true
                    progress.value = 100
                    break;
                case "RESULTS":
                    console.log("RESULTS selected")
                    progress.visible = false
                    break;
                default:
                    console.log("default")
                    progress.visible = true
                    actionsbuttons.state = "SELECTION"

                }

            }
        }


        SuiteListView {
            id: suitelist
            height: units.gu(43)
            width: parent.width - units.gu(10)

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: actionbuttons.bottom
            anchors.topMargin: units.gu(5)
        }


        BottomButtons {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: suitelist.bottom
            anchors.topMargin: units.gu(5)

            onSelectAll:{
                console.log("Select All")
            }

            onDeselectAll: {
                console.log("Delselect All")
            }

            onStartTesting: {
                console.log("Start Testing")
            }
        }
    }
}

