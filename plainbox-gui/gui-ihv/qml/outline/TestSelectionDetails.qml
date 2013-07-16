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
    property bool showDetails;


    onTestItemChanged: {
        // fill in details here
        nameText.text = testItem.testname;
    }

    onShowDetailsChanged:{
        if (showDetails){
            progressIcon.source = "DownArrow.png";
            detailsFlick.height = testseldetails.height;
        }
        else{
            progressIcon.source = "RightArrow.png";
            detailsFlick.height = 0
        }
    }

    // Open Details
    Item {
        id: detailsItem
        height: parent.height
        width: detailsLabel.width + progressIcon.width + units.gu(2)

        Label {
            id: detailsLabel
            text: i18n.tr("Test Details")
            anchors {
                left: parent.left
                top: parent.top
                margins: units.gu(1)
            }
        }

        Image {
            id: progressIcon
            source: "RightArrow.png"
            anchors {
                left: detailsLabel.right
                top: parent.top
                margins: units.gu(1)
            }

            opacity: enabled ? 1.0 : 0.5

        }
        MouseArea {
            anchors.fill: detailsItem
            onClicked: {showDetails = !showDetails}
        }
    }



    // Right side of the details
    Flickable {
        id: detailsFlick
        anchors.left: detailsItem.right
        anchors.top: parent.top
        anchors.leftMargin: units.gu(2)
        width: parent.width - detailsItem.width - units.gu(2)
        height: 0  // initialize to closed
        contentHeight: rightRect.height
        clip: true
        boundsBehavior : Flickable.StopAtBounds

        Rectangle {
            id: rightRect
            anchors.right: parent.right
            anchors.top: parent.top

            height: testseldetails.height + units.gu(10)
            width: parent.width
            border.color: "black"
            border.width: 1

            Label {
                id: nameLabel
                text: i18n.tr("     name:  ")
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
                anchors.right: rightRect.right
                anchors.top: parent.top
                anchors.margins: units.gu(1)
            }
            Text {
                id: nameText
                anchors.fill: nameRect
                anchors.margins: units.gu(1)
                text:""
            }

            Label {
                id: dependsLabel
                text: i18n.tr("depends: ")
                anchors.left: parent.left
                anchors.top: nameRect.bottom
                anchors.margins: units.gu(2)
            }

            Rectangle {
                id: dependsRect
                height: units.gu(4)
                border.color: UbuntuColors.warmGrey
                border.width: 1
                anchors.left: dependsLabel.right
                anchors.right: rightRect.right
                anchors.top: nameRect.bottom
                anchors.margins: units.gu(1)
            }
            Text {
                id: dependsText
                anchors.fill: dependsRect
                anchors.margins: units.gu(1)
                anchors.top: nameRect.bottom
                text:""
            }
            Label {
                id: requiresLabel
                text: i18n.tr(" requires: ")
                anchors.left: parent.left
                anchors.top: dependsRect.bottom
                anchors.margins: units.gu(2)
            }

            Rectangle {
                id: requiresRect
                height: units.gu(4)
                border.color: UbuntuColors.warmGrey
                border.width: 1
                anchors.left: requiresLabel.right
                anchors.right: rightRect.right
                anchors.top: dependsRect.bottom
                anchors.margins: units.gu(1)
            }
            Text {
                id: requiresText
                anchors.fill: requiresRect
                anchors.margins: units.gu(1)
                anchors.top: dependsRect.bottom
                text:""
            }

            Label {
                id: otherLabel
                text: i18n.tr("     other: ")
                anchors.left: parent.left
                anchors.top: requiresRect.bottom
                anchors.margins: units.gu(2)
            }

            Rectangle {
                id: otherRect
                height: units.gu(4)
                border.color: UbuntuColors.warmGrey
                border.width: 1
                anchors.left: requiresLabel.right
                anchors.right: parent.right
                anchors.top: requiresRect.bottom
                anchors.margins: units.gu(1)
            }
            Text {
                id: otherText
                anchors.fill: requiresRect
                anchors.margins: units.gu(1)
                anchors.top: requiresRect.bottom
                text:""
            }

        }

    }
    Scrollbar {
        flickableItem: detailsFlick
        align: Qt.AlignTrailing
    }
}

