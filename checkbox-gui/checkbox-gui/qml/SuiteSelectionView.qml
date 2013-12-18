/*
 * This file is part of Checkbox
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
import "."




Page {
    id: suiteselection
    title: i18n.tr("Suite Selection")

    Item {
        id: filler
        height: units.gu(4)
    }

    Rectangle {
        id: suitelist
        width: parent.width - units.gu(4)
        color: "white"
        height: parent.height - filler.height - okbutton.height - units.gu(6)
        anchors{
            horizontalCenter: parent.horizontalCenter
            top: filler.bottom
        }

        ListView {
            id: testselection
            height: parent.height
            width: parent.width
            anchors.fill: parent
            contentHeight: units.gu(12) * whiteListModel.count
            interactive: true
            clip: true
            boundsBehavior : Flickable.StopAtBounds
            model: whiteListModel

            delegate: SuiteSelectionDelegate{}
        }

        Scrollbar {
            flickableItem: testselection
            align: Qt.AlignTrailing
        }

        // At least one whitelist MUST be selected
        function ensure_one_selection() {
            var one_selection = false;

            for (var i = whiteListModel.count - 1; i >= 0; i--){
                var item = whiteListModel.get(i);

                if (item.check === "true") {
                    one_selection = true;
                }
            }

            // If nothing is selected, disable the ok button
            okbutton.enabled = one_selection
        }
    }

    ActivityIndicator {
        id: suite_sel_activity

        running: false

        anchors.horizontalCenter: suitelist.horizontalCenter
        anchors.verticalCenter: suitelist.verticalCenter
    }

    Button {
        id: okbutton
        width: parent.width - units.gu(4)
        anchors {
            horizontalCenter:parent.horizontalCenter
            bottom: parent.bottom
            margins: units.gu(2)
        }
        text: i18n.tr("OK")
        color: UbuntuColors.lightAubergine
        onClicked: {
            // Ensure we only ask the service about this once (Bug 1209284)
            okbutton.enabled = false;

            suite_sel_activity.running = true;

            suitelist.visible = false;

            // Dump the whitelist as finally selected by the user
            guiEngine.dump_whitelist_selection();

            /* Now, we should go run the guiengine update to run the local jobs
              which happen to match the whitelist. Then we can collect the
              test jobs and show them to the user.
             */
            guiEngine.RunLocalJobs();
        }
    }

    Connections {
        target: guiEngine
        onLocalJobsCompleted: {
            suite_sel_activity.running = false;

            // Now, we should repopulate the testlistmodel...
            testitemFactory.CreateTestListModel(testListModel);
            // NOTE: When the user is done, this is where to load up the TestSelection list
            mainView.state = "TESTSELECTION"
        }
    }

}
