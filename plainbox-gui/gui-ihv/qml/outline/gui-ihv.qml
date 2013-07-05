/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
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
import GuiEngine 1.0
import Ubuntu.Components 0.1
import Ubuntu.Components.Popups 0.1
import Ubuntu.Layouts 0.1
import Ubuntu.Components.ListItems 0.1 as ListItem
import "."



MainView {
    width: units.gu(80)
    height: units.gu(100)

    Page {
        title: "Plainbox"

        Item {
            id: progress
            width: parent.width - units.gu(10)
            anchors.horizontalCenter: parent.horizontalCenter


            Label {
                id: progresslabel

                text: "Working..."
                anchors.left: parent.left
            }
            ProgressBar {
                id: progressbar
                width: parent.width
                anchors.top: progresslabel.bottom
                anchors.topMargin: units.gu(1)
                indeterminate: false
                minimumValue: 0
                maximumValue: 100
                value: 50
                anchors.left: parent.left
            }
        }

        Row {
            id: actionbutton
            width: parent.width - units.gu(20)
            spacing: (parent.width - (140*3))/5  // width - buttons / 5 spaces
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: progress.bottom
            anchors.topMargin: units.gu(10)


            Button {
                 text: "selection"
                 width: 140
            }
            Button {
                 text: "run"
                 width: 140
            }
            Button {
                text: "results"
                width: 140

            }
        }


        Rectangle {
            color: "#f7f7f7"
            width: parent.width - units.gu(10)

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: actionbutton.bottom
            anchors.topMargin: units.gu(5)
            height: groupedList.height

            ListModel {
                id: groupedModel
                ListElement { name: "Orange"; type: "Fruit"}
                ListElement { name: "Apple"; type: "Fruit" }
                ListElement { name: "Tomato"; type: "Fruit" }
                ListElement { name: "Carrot"; type: "Vegetable" }
                ListElement { name: "Potato"; type: "Vegetable" }
            }

            ListView {
                id: groupedList
                model: groupedModel
                width: parent.width
                height: contentHeight
                interactive: false
                delegate: ListItem.Standard {
                    text: i18n.tr(name)
                }
                section.property: "type"
                section.criteria: ViewSection.FullString
                section.delegate: ListItem.Header { text: i18n.tr(section) }
            }
        }




        GuiEngine {
            id: guiengineobj
        }

        MouseArea {
            id: gui_ihv_mouse_area
            anchors.fill: parent
            onClicked: {

                // Just call a simple Plainbox function to exit (proof of concept)
                guiengineobj.Dummy_CallPlainbox_Exit();
                // Qt.quit();

            }
        }

        Component {
            id: warning_dialog
            WarningDialog{
                text: i18n.tr("The hoopla met the poopla and we all could no longer do as we want.  Would you like me to try again?")
                showOK: false
                showCheckbox: true



                onCont: {
                    checkIfChecked();
                    console.log("continue clicked");
                }

                onCancel: {
                    checkIfChecked();
                    console.log("cancel clicked");
                }

                function checkIfChecked(){
                    if (isChecked)
                        console.log("do not warn again!");
                    else
                        console.log("warn again");
                }

            }
        }



        Button {
            id: warning_button
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom : warning_button2.top
            anchors.bottomMargin: 20
            color: UbuntuColors.darkAubergine
            text: "warning..."
            width: 100
            onClicked:{
                PopupUtils.open(warning_dialog, warning_button);
            }
        }


        Button {
            id: warning_button2
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom : parent.bottom
            anchors.bottomMargin: 20
            color: UbuntuColors.lightAubergine
            text: "failed..."
            width: 100
            onClicked:{
                var warningDlg = Qt.createComponent("WarningDialog.qml");
                if (warningDlg.status == Component.Ready) {
                    var warningObj = warningDlg.createObject(parent, {"title": "Failed!",
                                                                 "text": "Oh man!",
                                                                 "showOK": true,
                                                                 "showContinue": false,
                                                                 "showCancel": false,
                                                                 "showCheckbox" :true
                                                             });
                    warningObj.show();

                    // need call this when object is closed (not sure how yet)
                    if (warningObj.isChecked)
                        console.log("do not warn again!");
                    else
                        console.log("warn AGAIN!")
                }
            }
        }

    }
}
