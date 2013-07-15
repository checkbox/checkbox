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

Item {
    id: testseldetails
    property var testItem;


    onTestItemChanged: {
        // fill in details here
        nameText.text = testItem.testname;
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.palette.normal.overlay
        border.color: "black"
        border.width: 1

        Text {
            anchors.centerIn: parent
            text: "Test details"
        }

        // Left side of the details
        Rectangle {
            id: leftRect
            height: parent.height
            width: parent.width - rightRect.width
            anchors {
                left: parent.left
                top: parent.top
                bottom: parent.bottom
            }
            color: Theme.palette.normal.overlay

            Column {
                anchors.horizontalCenter: leftRect.horizontalCenter

                spacing: units.gu(1)

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18n.tr("Test Details: ")
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18n.tr("Test Run Time")
                }
                Text {
                    id: testTimeRunText
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: "green"
                    text: i18n.tr("< 1 min")
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18n.tr("Suite Time Run")
                }
                Text {
                    id: suiteTimeRunText
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: "green"
                    text: i18n.tr("90 minutes")
                }
            }
        }



        // Right side of the details

        Rectangle {
            id: rightRect
            anchors.right: parent.right
            anchors.top: parent.top

            height: parent.height
            width: parent.width - units.gu(20)
            color: Theme.palette.normal.overlay
            border.color: "black"
            border.width: 1

            Label {
                id: nameLabel
                text: i18n.tr("name: ")
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.margins: units.gu(2)
            }

            Rectangle {
                id: nameRect
                height: units.gu(4)
                border.color: UbuntuColors.warmGrey
                border.width: 1
                anchors.left: nameLabel.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: units.gu(1)
            }
            Text {
                id: nameText
                anchors.fill: nameRect
                anchors.margins: units.gu(1)
                text:""
            }
        }

    }
}

