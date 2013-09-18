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
import Ubuntu.Components.Popups 0.1
import Ubuntu.Layouts 0.1
import Ubuntu.Components.ListItems 0.1 as ListItem
import "."


Page {
    title: i18n.tr("Choose tests to run on your system:")


    Item { // puts a space at the top
        id: filler
        height: units.gu(0)
        anchors {
            left: parent.left
            top: parent.top
        }
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
            anchors.left: parent.left
            anchors.leftMargin: units.gu(6)
            anchors.right: typelabel.left
            anchors.rightMargin: units.gu(2)
        }

        Text  {
            id: typelabel
            text: i18n.tr("Type")
            width: units.gu(6)
            anchors.right: esttimelabel.left
            anchors.rightMargin: units.gu(6)
            horizontalAlignment: Text.AlignHCenter
        }

        Text  {
            id: esttimelabel
            text: i18n.tr("Estimated Time")
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
    }

    Component {
        id: popoverDetails

        Popover {
            id: popover
            opacity: 0.0
            contentWidth: parent.width - units.gu(30)
            callerMargin: units.gu(2)

            Flickable {
                id: flickable
                anchors {
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    rightMargin: units.gu(1)
                }
                height: testdetails.height > mainView.height/2 ? mainView.height/2 : testdetails.height

                contentHeight: testdetails.height
                width: popover.width
                clip: true
                // Test Details (Properties)
                TestSelectionDetails {
                    id: testdetails
                }
            }
            Scrollbar {
                flickableItem: flickable
                align: Qt.AlignTrailing
            }
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
                 onTriggered: PopupUtils.open(actionSelectionPopover, infoButton)
            }
            Button {
                 id:selectButton
                 text: i18n.tr("Select All")
                 color: UbuntuColors.coolGrey
                 width: units.gu(18)
                 onTriggered: testsuitelist.selectAll(true);
            }
            Button {
                 id: deselectButton
                 text: i18n.tr("Deselect All")
                 color: UbuntuColors.coolGrey
                 width: units.gu(18)
                 onTriggered: testsuitelist.selectAll(false);
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
                onTriggered: {
                    mainView.state = "RUNMANAGER"
                    console.log("Start Testing")
                    /* kick off the real tests now */
                    guiEngine.RunJobs();
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
                    onTriggered: PopupUtils.open(popoverDetails)
                }
            }
        }
    }

    // Small blue test summary bar at the bottom of the page
    TestSelectionSummary{
        id: summary
        height: units.gu(2)
        width: parent.width
        anchors {
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
        }
    }
}
