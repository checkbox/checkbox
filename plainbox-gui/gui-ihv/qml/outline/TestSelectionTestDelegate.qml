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
import "./artwork"

Component {
    id: testDelegate

    Item{
        id: testitem
        width: parent.width
        height: units.gu(7)
        property string groupname: group
        property alias checked: itemcheckbox.checked
        property string labelname: testname


        MouseArea {
            width: parent.width - itemcheckbox.width
            height: parent.height
            anchors.right: parent.right

            onClicked: {
                testdetails.testItem = testSuiteModel.get(index);
                groupedList.currentIndex = index;
            }
        }

        Item {
            anchors.fill: parent

            Item {
                id: filler
                width: itemcheckbox.width
            }

            CheckBox {
                id: itemcheckbox
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: filler.right
                anchors.leftMargin: units.gu(2)
                checked: check
                onClicked: {
                    testSuiteModel.setProperty(index, "check", checked);
                    groupedList.setGroupCheck(group)
                }
            }


            Text {
                id: nameLabel
                text: testname
                width: units.gu(40)
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: itemcheckbox.right
                anchors.leftMargin: units.gu(1)
            }

            Item {
                id: typefiller
                width: units.gu(2)
                anchors.left: nameLabel.right
            }

            Text {
                id: typelabel
                text: type
                width: units.gu(10)
                anchors.left: typefiller.right
                anchors.verticalCenter: parent.verticalCenter
                horizontalAlignment: Text.AlignHCenter

            }

            Item {
                id: descfiller
                width: units.gu(20)
                anchors.left: typelabel.right
            }

            Text {
                id: descLabel
                text: convertToText(duration)
                width: units.gu(10)
                anchors.left: descfiller.right
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
        ListItem.ThinDivider {}
    }
}
