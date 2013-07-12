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
    title: "Choose tests to run on your system:"

    Label {
        id: testselectionlabel
        width: parent.width
        anchors.left: parent.left
        anchors.leftMargin: units.gu(2)
        anchors.topMargin: units.gu(4)


        //text: i18n.tr("Choose tests to run on your system:")
    }

    Item {
        id: testlistheaders
        width: parent.width - units.gu(4)
        height: units.gu(3)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: testselectionlabel.bottom
        anchors.margins: units.gu(2)

        Text  {
            id: complabel
            anchors.left: parent.left
            anchors.leftMargin: units.gu(6)
            text: i18n.tr("Components")
        }
        Text  {
            id: typelabel
            anchors.left: complabel.right
            anchors.leftMargin: units.gu(40)
            text: i18n.tr("Type")
        }
        Text  {
            id: descriptionlabel
            anchors.left: typelabel.right
            anchors.leftMargin: units.gu(30)
            text: i18n.tr("Description")
        }
    }



    TestListView {
        id: testsuitelist
        height: units.gu(56)
        width: parent.width - units.gu(4)

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: testlistheaders.bottom
    }

    TestSelectionDetails {
        id: testdetails
        height: units.gu(20)
        width: parent.width - units.gu(4)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: testsuitelist.bottom
        anchors.topMargin: units.gu(2)
    }


    TestSelectionButtons {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: testdetails.bottom
        anchors.topMargin: units.gu(5)

        onSelectAll:{
            testsuitelist.selectAll(true);
        }

        onDeselectAll: {
            testsuitelist.selectAll(false);
        }

        onStartTesting: {
            mainView.state = "DEMOWARNINGS"
            console.log("Start Testing")
        }
    }
}


