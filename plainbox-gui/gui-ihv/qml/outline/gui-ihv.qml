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
import "."

SuiteSelection {
    id: mainview
    height: units.gu(90)


    // Below is test code, shows how to put up a warning dialog
    // TODO == move this to WarningDialog.qml
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
        visible: false
        spacing: 2
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: units.gu(2)
        Button {
            id: warning_button
            color: "yellow"
            text: "warning..."
            width: 100
            onClicked:{
                PopupUtils.open(warning_dialog, warning_button);
            }
        }


        Button {
            color: "pink"
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

