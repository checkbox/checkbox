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
import "."





Page {
    title: i18n.tr("Run Manager")

    // TODO - this timer keeps track of time passing
    // When using plainbox, get tests and advance using it
    // currently itemindex is advanced at each timer interval
    // and the runstatus is updated... which is FAKE.

    // FYI: testsuitelist.itemindex is the index of the current item in the ListElement
    // and item is the current item in the view.
    Timer {
        id: timer
        property int testIndex: 0                       // which test we are running from the list
        property int totalTests: testSuiteModel.count
        property var startTime: new Date()
        property var testStartTime: new Date()


        interval: 1100;
        running: true;
        repeat: true


        onTriggered: {
            if (testIndex == totalTests ){
                // All tests are done

                // update ui
                runbuttons.pauseButtonEnabled = false;
                runbuttons.resultsButtonEnabled = true;
                progress.title = "Completed  (" + utils.formatElapsedTime((new Date() - timer.startTime)) + ")";
                progress.enabled = false;
                running = false;

                // set flags in list (for group details)
                testsuitelist.curSectionInTest = "";
                testsuitelist.testsComplete = true;
            }
            else {
                testSuiteModel.setProperty(testIndex, "runstatus", 2);  // this will come from Plainbox
                // set the group status to the worst runstatus outcome ... failure?  userreq?, check runstatus
                testSuiteModel.setProperty(testIndex, "groupstatus", 2);

                testsuitelist.itemindex = testIndex;    // tell list which item to select
                var stopTime = new Date();
                testSuiteModel.setProperty(testIndex, "elapsedtime", stopTime - timer.testStartTime);

                testStartTime = stopTime;
                progress.value = testIndex + 1;
                progress.title = "Running  (" + utils.formatElapsedTime(stopTime - timer.startTime) + ")";
            }
            testIndex++;
        }
    }

    Item {
        id: filler
        height: units.gu(0)
        anchors.top: parent.top
    }



    Item {
        id: runmanagerlistheaders
        width: parent.width - units.gu(4)
        height: units.gu(3)

        anchors {
            horizontalCenter: parent.horizontalCenter
            top: filler.bottom
            margins: units.gu(2)
        }

        Item {
            id: testcasenamefiller
            width: units.gu(8)
            anchors.left: parent.left
        }
        Text  {
            id: testcasenamelabel
            width: units.gu(12)
            text: i18n.tr("Test Case Name")
            anchors.left: testcasenamefiller.right
        }
        Item {
            id: statusfiller
            width: units.gu(15)
            anchors.left: testcasenamelabel.right
        }

        Text  {
            id: statuslabel
            text: i18n.tr("Status")
            anchors.left: statusfiller.right
            anchors.leftMargin: units.gu(12)
            horizontalAlignment: Text.AlignHCenter
        }

        Item {
            id: eslapsedtimefiller
            width: units.gu(2)
            anchors.left: statuslabel.right
        }

        Text  {
            id: eslapsedtimelabel
            text: i18n.tr("Elapsed Time")
            anchors.left: eslapsedtimefiller.right
            anchors.leftMargin: units.gu(10)
            horizontalAlignment: Text.AlignHCenter
        }

        Item {
            id: actionsfiller
            width: units.gu(6)
            anchors.left: eslapsedtimelabel.right
        }
        Text  {
            id: actionslabel
            width: units.gu(10)
            text: i18n.tr("Actions")
            horizontalAlignment: Text.AlignHCenter
            anchors.left: actionsfiller.right
        }

        Item {
            id: detailsfiller
            width: units.gu(6)
            anchors.left: actionslabel.right
        }
        Text  {
            id: detailslabel
            width: units.gu(10)
            text: i18n.tr("Details")
            horizontalAlignment: Text.AlignHCenter
            anchors.left: detailsfiller.right
        }
    }


    RunManagerListView {
        id: testsuitelist
        width: parent.width - units.gu(4)
        anchors{
            horizontalCenter: parent.horizontalCenter
            top: runmanagerlistheaders.bottom
            bottom: progress.top
            bottomMargin: units.gu(2)
        }
    }

    Progress {
        id: progress
        height: units.gu(4)-1
        width: parent.width - units.gu(20)

        anchors {
            bottom: runbuttons.top
            bottomMargin: units.gu(4)
            horizontalCenter: parent.horizontalCenter
        }
        title: i18n.tr("Running")
        maxValue: testSuiteModel.count //TODO put the number of tests here
        value: 0

    }

    RunManagerButtons {
        id: runbuttons

        anchors{
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
            margins: units.gu(2)
        }

        onExit:{
            Qt.quit()
        }

        onPauseTest: {
            // TODO call into plainbox to pause
            timer.running = false;
            timer.repeat = false;
            progress.title = "Paused"
            console.log("Pause...")
        }
        onResumeTest: {
            // TODO call into plainbox to resume
            timer.testStartTime = new Date()
            timer.running = true;
            timer.repeat = true;
            console.log("Resume...")
        }
        onResults: {
            PopupUtils.open(submission_dialog, runbuttons);
            console.log("Results...")
        }

        Component {
            id: submission_dialog
            SubmissionDialog{
            }
        }

        Component {
            id: manual_dialog
            ManualInteractionDialog{
            }
        }




        Item {
            id: utils
            function formatElapsedTime(elap){
                // strip the miliseconds
                elap = parseInt(elap / 1000);

                // get seconds (Original had 'round' which incorrectly counts 0:28, 0:29, 1:30 ... 1:59, 1:0)
                var seconds = parseInt(Math.round(elap % 60));

                // remove seconds from the date
                elap = parseInt(Math.floor(elap / 60));

                // get minutes
                var minutes = parseInt(Math.round(elap % 60));

                // remove minutes from the date
                elap = parseInt(Math.floor(elap / 60));


                // get hours
                var hours = parseInt(Math.round(elap % 24));

                var timeStr = ""

                if (hours)
                    timeStr = hours + ":";
                timeStr = timeStr +  ("0" + minutes).slice(-2) + ":" + ("0" + seconds).slice(-2);

                return timeStr;
            }
        }

    }
}
