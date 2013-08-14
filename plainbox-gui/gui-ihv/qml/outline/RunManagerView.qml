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
    id: runmanagerview
    title: i18n.tr("Run Manager")

    property bool reportIsSaved: false;
    property bool testingComplete: false

    // TODO - this timer keeps track of time passing
    // When using plainbox, get tests and advance using it
    // currently itemindex is advanced at each timer interval
    // and the runstatus is updated... which is FAKE.

    // Need to do:
    // set testsuitelist.itemindex to the index of the current item in the ModelSectionCounter
    // testsuitelist.curSectionTested = "" when done completed
    // and item is the current item in the view.

    Item {
        id: timer	// TODO - This is a legacy name from the prototype. It should be renamed
        property int testIndex: 0                       // which test we are running from the list
        property int totalTests: testListModel.count
        property var startTime: new Date()
        property var testStartTime: new Date()

        property bool running;

        Connections {
            target: guiEngine

            onJobsCompleted: {
                console.log("onJobsCompleted");

                // All tests are done
                runmanagerview.testingComplete = true;
                // update ui
                runbuttons.pauseButtonEnabled = false;
                runbuttons.resultsButtonEnabled = true;
                progress.title = "Completed  (" + utils.formatElapsedTime((new Date() - timer.startTime)) + ")";
                progress.enabled = false;
                timer.running = false;

                // set flags in list (for group details)
                testsuitelist.curSectionTested = "";  // set this as there is no more tested
            }

            onUpdateGuiObjects: {
                /* we must translate from job_id ("/plainbox/job/<id_string>
                 * Into the index for one of the displayed items
                 */
                var i = 0;
                for (i = testListModel.count -1; i>=0; i--) {

                    // Compare the m_path to the job_id
                    var item = testListModel.get(i);

                    if (item.objectpath === job_id ) {
                        timer.testIndex =i ;
                    }
                }
                // TODO - this is hardcoding the properties.... PB shuold be doing this
                testListModel.setProperty(timer.testIndex, "runstatus", 2);  // this will come from Plainbox
                // set the group status to the worst runstatus outcome ... failure?  userreq?, check runstatus
                testListModel.setProperty(timer.testIndex, "groupstatus", 2);


                // set elapsed time
                var stopTime = new Date();
                testListModel.setProperty(timer.testIndex, "elapsedtime", stopTime - timer.testStartTime);

                timer.testStartTime = stopTime;
                progress.value = timer.testIndex + 1;
                var testname =  testListModel.get(timer.testIndex).testname;
                progress.title = "Running " + (timer.testIndex + 1)
                        + " of "+ testListModel.count
                        + "  (" + utils.formatElapsedTime(stopTime - timer.startTime) + ")"
                        + "   " + testname;
            }
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
            bottomMargin: units.gu(6) // SDK Bug? 0 places it Over the buttons!
            horizontalCenter: parent.horizontalCenter
        }
        title: i18n.tr("Running")
        maxValue: testListModel.count //TODO put the number of tests here
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
            if (!runmanagerview.testingComplete){
                PopupUtils.open(incomplete_warning_dialog, runbuttons);
                pause();
            }
            else if (!reportIsSaved)
                PopupUtils.open(submission_warning_dialog, runbuttons);
            else
                Qt.quit();
        }

        onPauseTest: {
            pause();
        }
        onResumeTest: {
            resume();
        }
        onResults: {
            PopupUtils.open(submission_dialog, runbuttons);
        }

        function resume(){
            // TODO call into plainbox to resume
            timer.testStartTime = new Date()
            timer.running = true;
            timer.repeat = true;
            console.log("Resume...")
        }

        function pause(){
            // TODO call into plainbox to pause
            timer.running = false;
            timer.repeat = false;
            progress.title = progress.title.replace("Running", "Paused ")
            console.log("Pause...")
        }

        Component {
            id: submission_dialog
            SubmissionDialog{
            }
        }

        Component {
            id: manual_dialog
            ManualInteractionDialog{
                testItem: testListModel.get(timer.testIndex);
            }
        }

        Component {
            id: submission_warning_dialog
            WarningDialog{
                text: i18n.tr("You are about to exit this test run without saving your results report. \n\nAre you sure? \n\n(Press Continue to Quit)");

                showOK: false
                showContinue: true
                showCheckbox: false

                onCont: {Qt.quit();}
            }
        }

        Component {
            id: incomplete_warning_dialog
            WarningDialog{
                text: i18n.tr("You are about to cancel an active test run.  Your system might be left in an unstable state.  Are you sure you want to exit?");
                showOK: true
                showCancel: true
                showContinue: false
                showCheckbox: false

                onOk: {
                    Qt.quit();
                }

                onCancel: {
                    // resume
                    runbuttons.resume()
                }
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
