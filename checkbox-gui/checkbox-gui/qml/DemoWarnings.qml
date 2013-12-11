/*
 * This file is part of Checkbox
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
import Ubuntu.Components.Popups 0.1

Page {
    title: "Warning Demo (not a production screen)"


    Component {
        id: warning_dialog
        WarningDialog{
            text: i18n.tr("What you are about to do will take a long time.  Are you sure you want to continue?")
            showOK: true
            showContinue: false
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



    Row {
        visible: true
        spacing: units.gu(6)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: units.gu(2)
        Button {
            id: warning_button
            color: "yellow"
            text: "warning..."
            width: units.gu(25)
            onClicked:{
                PopupUtils.open(warning_dialog, warning_button);
            }
        }


        Button {
            color: "pink"
            text: "failed..."
            width: units.gu(25)
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

    Button {
         anchors.centerIn: parent
         text: i18n.tr("Move on to the Welcome Screen")
         color: UbuntuColors.lightAubergine
         width: units.gu(30)
         onClicked: {mainView.state = "WELCOME"}
    }
}

