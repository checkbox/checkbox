/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
 * - Sylvain Pineau <sylvain.pineau@canonical.com>
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
import Ubuntu.Layouts 0.1
import Ubuntu.Components.ListItems 0.1 as ListItem
import "."


Page {
    title: i18n.tr("Choose tests to run on your system:")

    property var currentTestItem;
    property int totalTests: 6
    property int totalManualTests: 2
    property int totalImplicitTests: 999

    Item { // puts a space at the top
        id: filler
        height: units.gu(0)
        anchors {
            left: parent.left
            top: parent.top
        }
    }

    function formatTotalTime(s){
        var estTimeStr = ""
        if (s == 0)
            estTimeStr = "0 min";
        else if (s < 0)
            estTimeStr = "N/A";
        else if (s / 60 < 1)
            estTimeStr = "< 1 min";
        else if (Math.round(s / 60) < 60){
            var durMinutes = Math.round(s / 60);
            estTimeStr = durMinutes.toString() + " min";
        }
        else {
            var hr = Math.round(s / (60 * 60));
            s -= hr * (60 * 60);
            estTimeStr = hr + " h " + Math.round(s / 60) + " min"
        }
        return  estTimeStr;
    }

    function validTotalTime(total_duration){
        return Object.keys(total_duration).map(function (key) {return total_duration[key]}).indexOf(-1)
    }

    // Test List Header Bar
    Item {
        id: testlistheaders
        width: parent.width - units.gu(4)
        height: units.gu(3)

        anchors {
            horizontalCenter: parent.horizontalCenter
            top: filler.bottom
            margins: units.gu(2)
        }

        Text  {
            id: complabel
            text: i18n.tr("Components")
            font.bold: true
            anchors.left: parent.left
            anchors.leftMargin: units.gu(6)
            anchors.right: typelabel.left
            anchors.rightMargin: units.gu(2)
        }

        Text  {
            id: typelabel
            text: i18n.tr("Type")
            font.bold: true
            width: units.gu(6)
            anchors.right: esttimelabel.left
            anchors.rightMargin: units.gu(6)
            horizontalAlignment: Text.AlignHCenter
        }

        Text  {
            id: esttimelabel
            text: i18n.tr("Estimated Time")
            font.bold: true
            width: units.gu(6)
            anchors.right: parent.right
            anchors.rightMargin: units.gu(6)
            horizontalAlignment: Text.AlignHCenter
        }
    }

    // List of actual Tests.
    TestSelectionListView {
        id: testsuitelist
        width: testlistheaders.width

        anchors{
            horizontalCenter: parent.horizontalCenter
            top: testlistheaders.bottom
        }

   	    // At least one test MUST be selected
    	function ensure_one_selection() {
            var one_selection = false;
            for (var i = testListModel.count - 1; i >= 0; i--){
                var item = testListModel.get(i);
                if (item.check === "true") {
                    one_selection = true;
                }
            }

            // If nothing is selected, disable the ok button
            startTesting.enabled = one_selection
        }
    }

    Component {
        id: details_dialog
        // Test Details (Properties)
        TestSelectionDetails {
            id: testdetails
        }
    }

    // Select All, Deselect All, Start Testing Buttons
    tools: ToolbarItems {
        back: Row {
            anchors {
                verticalCenter: parent.verticalCenter
            }
            spacing: units.gu(1)
            Button {
                 id: infoButton
                 text: i18n.tr("Info")
                 color: UbuntuColors.lightAubergine
                 onClicked: {
                     PopupUtils.open(actionSelectionPopover, infoButton)
                 }
            }
            Button {
                 id:selectButton
                 text: i18n.tr("Select All")
                 color: UbuntuColors.coolGrey
                 width: units.gu(18)
                 onClicked: {
                     testsuitelist.selectAll(true)
                     testsuitelist.ensure_one_selection()
                 }
            }
            Button {
                 id: deselectButton
                 text: i18n.tr("Deselect All")
                 color: UbuntuColors.coolGrey
                 width: units.gu(18)
                 onClicked: {
                     testsuitelist.selectAll(false)
                     testsuitelist.ensure_one_selection()
                 }
            }
        }
        Row {
            anchors {
                verticalCenter: parent.verticalCenter
            }
            Button {
                id: startTesting
                text: i18n.tr("Start Testing")
                width: units.gu(18)
                onClicked: {
                    mainView.state = "RUNMANAGER"

                }
            }
        }
        locked: true
        opened: true
    }

    Component {
        id: actionSelectionPopover
        ActionSelectionPopover {
            callerMargin: units.gu(1)
            contentWidth: units.gu(15)
            actions: ActionList {
                Action {
                    text: i18n.tr("Selection Stats")
                    onTriggered: {
                        PopupUtils.open(stats_dialog)
                    }
                }
                Action {
                    text: i18n.tr("Test Details")
                    onTriggered: PopupUtils.open(details_dialog)
                }
            }
        }
    }
    Component {
        id: stats_dialog
        Dialog{
            id: dialog
            title: i18n.tr("Selection Stats")
            property var total_duration: guiEngine.GetEstimatedDuration();
            Rectangle {
                id: statrect
                color: "transparent"
                height: statrow.height + okButton.height
                Row {
                    id: statrow
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: units.gu(4)
                    Column {
                        id: col1
                        Label {text: i18n.tr("Total tests");fontSize: "large"; color: "white"}
                        Label {text: i18n.tr("Selected")}
                        Label {text: i18n.tr("Manual")}
                        Label {text: i18n.tr("Implicit")}
                        Label {text: i18n.tr(" "); fontSize: "large"}
                        Label {text: i18n.tr("Estimated time"); fontSize: "large"; color: "white"}
                        Label {text: i18n.tr("Automated")}
                        Label {text: i18n.tr("Manual")}
                    }
                    Column {
                        id: col2
                        Label {
                            text: (parseInt(totalTests) + parseInt(totalImplicitTests));
                            anchors.right: col2.right;
                            fontSize: "large"; color: "white"
                        }
                        Label {text: totalTests; anchors.right: col2.right}
                        Label {text: totalManualTests; anchors.right: col2.right}
                        Label {text: totalImplicitTests; anchors.right: col2.right}
                        Label {text: i18n.tr(" "); fontSize: "large"}
                        Label {
                            text: validTotalTime(total_duration)?formatTotalTime(total_duration["automated_duration"] + total_duration["manual_duration"]):"N/A";
                            anchors.right: col2.right;
                            fontSize: "large"; color: "white"
                        }
                        Label {text: formatTotalTime(total_duration["automated_duration"]); anchors.right: col2.right}
                        Label {text: formatTotalTime(total_duration["manual_duration"]); anchors.right: col2.right}
                    }
                }
            }
            Button {
                id: okButton
                text: i18n.tr("Back")
                onClicked: {
                    PopupUtils.close(dialog);
                }
            }
        }
    }
}
