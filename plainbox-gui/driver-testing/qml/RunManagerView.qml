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

    // Updates the test status based on GuiEngine signals
    Item {
        id: updater
        property int completed: 0   // How many tests have we run so far?
        property int testIndex: 0   // which test we are running from the list

        // totalTests: Denotes lines in the testListModel (display) model, NOT real number of tests
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
                progress.title = "Completed  (" + utils.formatElapsedTime((new Date() - updater.startTime)) + ")";
                progress.enabled = false;
                updater.running = false;

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
                        updater.testIndex =i ;
                    }
                }

                // outcome comes from guiengine in this signal
                testListModel.setProperty(updater.testIndex, "runstatus", outcome);

                // We may consider setting the IO Log details too here, but not yet

                // set the group status to the worst runstatus outcome ... failure?  userreq?, check runstatus
                testListModel.setProperty(updater.testIndex, "groupstatus", 2);

                // set elapsed time
                var stopTime = new Date();
                testListModel.setProperty(updater.testIndex, "elapsedtime", stopTime - updater.testStartTime);

                updater.testStartTime = stopTime;

                // Update the progress bar
                progress.maxValue = guiEngine.ValidRunListCount();

                /* +1 because the index is from zero, but we want to show the
                 * zero'th test as test 1
                 */
                progress.value = current_job_index+1; // from onUpdateGuiObjects

                var testname =  testListModel.get(updater.testIndex).testname;
                progress.title = "Running " + (progress.value)
                        + " of "+ progress.maxValue
                        + "  (" + utils.formatElapsedTime(stopTime - updater.startTime) + ")"
                        + "   " + testname;
            }
        }
    }

    Item {
        id: filler
        height: units.gu(0)
        anchors.top: parent.top
    }

    // Test List Header Bar
    Item {
        id: runmanagerlistheaders
        width: parent.width - units.gu(4)
        height: units.gu(3)

        anchors {
            horizontalCenter: parent.horizontalCenter
            top: filler.bottom
            margins: units.gu(2)
        }

        Text  {
            id: testcasenamelabel
            text: i18n.tr("Test Case Name")
            anchors.left: parent.left
            anchors.leftMargin: units.gu(6)

            anchors.right: statuslabel.left
            anchors.rightMargin: units.gu(6)
        }

        Text  {
            id: statuslabel
            text: i18n.tr("Status")

            width: units.gu(6)

            anchors.right: elapsedtimelabel.left
            anchors.rightMargin: units.gu(6)

            horizontalAlignment: Text.AlignHCenter
        }

        Text  {
            id: elapsedtimelabel
            text: i18n.tr("Elapsed Time")

            width: units.gu(6)

            anchors.right: actionslabel.left
            anchors.rightMargin: units.gu(6)

            horizontalAlignment: Text.AlignHCenter
        }

        Text  {
            id: actionslabel
            text: i18n.tr("Actions")

            width: units.gu(6)

            anchors.right: detailslabel.left
            anchors.rightMargin: units.gu(6)

            horizontalAlignment: Text.AlignHCenter
        }

        Text  {
            id: detailslabel
            text: i18n.tr("Details")

            width: units.gu(6)

            anchors.right: parent.right
            anchors.rightMargin: units.gu(6)

            horizontalAlignment: Text.AlignHCenter
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
        height: units.gu(4)
        width: parent.width - units.gu(20)

        anchors {
            bottom: runbuttons.top
            bottomMargin: units.gu(6) // SDK Bug? 0 places it Over the buttons!
            horizontalCenter: parent.horizontalCenter
        }
        title: i18n.tr("Running")
        maxValue: guiEngine.ValidRunListCount();
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
            updater.testStartTime = new Date()
            updater.running = true;
            console.log("Resume...")

            guiEngine.Resume();
        }

        function pause(){
            updater.running = false;
            progress.title = progress.title.replace("Running", "Paused ")
            console.log("Pause...")

            guiEngine.Pause();
        }

        Component {
            id: submission_dialog
            SubmissionDialog{
            }
        }

        Component {
            id: manual_dialog
            ManualInteractionDialog{
                testItem: testListModel.get(updater.testIndex);
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

    Connections {
        id: myconnections
        target: guiEngine
        onRaiseManualInteractionDialog: {
            PopupUtils.open(manual_dialog, runmanagerview);
        }
    }
}
