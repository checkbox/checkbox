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

    Item {
        id: testlistheaders
        width: parent.width - units.gu(4)
        height: units.gu(3)

        anchors {
            horizontalCenter: parent.horizontalCenter
            top: filler.bottom
            margins: units.gu(2)
        }

        Item {
            id: compfiller
            width: units.gu(6)
            anchors.left: parent.left
        }
        Text  {
            id: complabel
            width: units.gu(12)
            text: i18n.tr("Components")
            anchors.left: compfiller.right
        }
        Item {
            id: typefiller
            width: units.gu(20)
            anchors.left: complabel.right
        }

        Text  {
            id: typelabel
            text: i18n.tr("Type")
            anchors.left: typefiller.right
            anchors.leftMargin: units.gu(10)
            horizontalAlignment: Text.AlignHCenter
        }

        Item {
            id: esttimefiller
            width: units.gu(4)
            anchors.left: typelabel.right
        }

        Text  {
            id: esttimelabel
            text: i18n.tr("Estimated Time")
            anchors.left: esttimefiller.right
            anchors.leftMargin: units.gu(10)
            horizontalAlignment: Text.AlignHCenter
        }

        Item {
            id: descfiller
            width: units.gu(12)
            anchors.left: esttimelabel.right
        }
        Text  {
            id: descriptionlabel
            width: units.gu(10)
            text: i18n.tr("Description")
            horizontalAlignment: Text.AlignHCenter
            anchors.left: descfiller.right
        }
    }

    TestSelectionListView {
        id: testsuitelist
        height: parent.height - filler.height - testlistheaders.height - summary.height - testbuttons.height - units.gu(12)

        width: testlistheaders.width

        anchors{
            horizontalCenter: parent.horizontalCenter
            top: testlistheaders.bottom
        }
    }



    TestSelectionDetails {
        id: testdetails
        height: units.gu(4)
        width: testlistheaders.width

        anchors{
            horizontalCenter: parent.horizontalCenter
            top: testsuitelist.bottom
            topMargin: units.gu(1)
        }
    }


    TestSelectionButtons {
        id: testbuttons
        anchors{
             horizontalCenter: parent.horizontalCenter
             bottom: parent.bottom
             bottomMargin: units.gu(4)
        }

        onSelectAll:{
            testsuitelist.selectAll(true);
        }

        onDeselectAll: {
            testsuitelist.selectAll(false);
        }

        onStartTesting: {
            // CHANGE THIS TO NEXT PAGE TO BRING UP
            mainView.state = "RUNMANAGER"
            console.log("Start Testing")
        }
    }

    TestSelectionSummary{
        id: summary
        width: parent.width
        anchors {
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
        }
    }
}


