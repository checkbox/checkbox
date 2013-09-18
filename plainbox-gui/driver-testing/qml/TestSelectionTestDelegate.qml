/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
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
import Ubuntu.Components 0.1
import Ubuntu.Components.ListItems 0.1 as ListItem
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
        property alias checked: itemcheckbox.checked
        property string labelname: testname

        // These properties help to simulate the treeview
        property bool open: true
        property bool is_branch: branch
        property int my_depth: depth

        // Select the highlight area
        MouseArea {
            id: selecthighlight
            anchors.fill: parent

            onClicked: {
                currentTestItem = testListModel.get(index);
                groupedList.currentIndex = index;
            }
        }

        onOpenChanged: {
            open?openshutIcon.source = "artwork/DownArrow.png":openshutIcon.source = "artwork/RightArrow.png"
        }

        Item {
            anchors.fill: parent

            Item {
                id: filler

                // this is our indentation level. we get this out of the model
                width: (depth * itemcheckbox.width) + units.gu(2)
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

                MouseArea {
                    id: openshutbutton
                    anchors.fill: parent

                    onClicked: {
                        testitem.open = !testitem.open
                        groupedList.openShutSubgroup(testitem, testitem.open)
                    }
                }
            }

            CheckBox {
                id: itemcheckbox
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: openshutIcon.right
                anchors.leftMargin: units.gu(2)
                checked: check
                onClicked: {

                    // Update the ListView (display)
                    groupedList.setGroupCheck(testitem);

                    // Update the underlying model
                    groupedList.updateListModel();
		    
                    // Update the summary bar at the bottom of TestSelectionView

                    groupedList.setListSummary();


                    // Warn the user if they are de-selecting tests
                    if (!checked)
                        groupedList.showWarning(itemcheckbox);
                }
            }

            Text {
                id: nameLabel
                text: testname
                elide: Text.ElideRight

                anchors.verticalCenter: parent.verticalCenter

                anchors.left: itemcheckbox.right
                anchors.leftMargin: units.gu(2)

                anchors.right: typelabel.left
                anchors.rightMargin: units.gu(2)
            }

            Text {
                id: typelabel
                text: type
                width: units.gu(6)

                anchors.right: esttimelabel.left
                anchors.rightMargin: units.gu(6)

                anchors.verticalCenter: parent.verticalCenter

                horizontalAlignment: Text.AlignHCenter

            }

            Text {
                id: esttimelabel
                text: convertToText(duration)
                width: units.gu(6)

                anchors.right: parent.right
                anchors.rightMargin: units.gu(6)

                anchors.verticalCenter: parent.verticalCenter

                horizontalAlignment: Text.AlignHCenter

                function convertToText(durationTime){
                    var timeStr = "";
                    if (durationTime/60 < 1)
                        timeStr = i18n.tr("< 1 minute");
                    else {
                        var durMinutes = Math.round(duration/60);
                        timeStr = durMinutes.toString() + i18n.tr(" minute");
                        if (durMinutes > 1)
                            timeStr += 's';
                    }
                    return timeStr;
                }
            }
        }

        // Item dividing line
        ListItem.ThinDivider {}
    }
}
