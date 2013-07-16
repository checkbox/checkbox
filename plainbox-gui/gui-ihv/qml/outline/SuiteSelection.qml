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




Page {
    title: i18n.tr("Suite Selection")

    Item {
        id: filler
        height: units.gu(4)
    }

    Rectangle {
        id: suitelist
        width: parent.width - units.gu(4)
        color: "white"
        height: parent.height - filler.height - okbutton.height - units.gu(10)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: filler.bottom

        ListView {
            id: testselection
            height: parent.height
            width: parent.width
            contentHeight: testSuiteModel.count
            interactive: true
            clip: true
            model: testSuiteModel
            delegate: Item {}
            section.property: "group"
            section.criteria: ViewSection.FullString
            section.delegate: SuiteSelectionDelegate{
                onSelectSuite: {
                    // In the model, select all tests in the suite
                    for (var i = testSuiteModel.count - 1; i >= 0; i--){
                        var item = testSuiteModel.get(i);
                        if (item.group === suite)
                            testSuiteModel.setProperty(i, "check", sel);
                     }
                }
            }
        }
    }


    Button {
        id: okbutton
        anchors.horizontalCenter:parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.margins: units.gu(2)
        text: i18n.tr("OK")
        color: UbuntuColors.lightAubergine
        onClicked: {mainView.state = "TESTSELECTION"}
    }

}
