/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
 *
 * Authors:
 * - Maciej Kisielewski <maciej.kisielewski@canonical.com>
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
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1

Page {
    id: screensPreviewPage
    title: i18n.tr("Screens preview")
    visible: false

    ColumnLayout {
        spacing: units.gu(3)
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            margins: units.gu(1)
        }
        Label {
            fontSize: "x-large"
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: i18n.tr("This is a developer screen that allows you to preview particular part of the app.\nSelect which screen to preview")
        }
        Button {
            text: i18n.tr("Welcome page")
            onClicked: {
                var newPage = Qt.createComponent(Qt.resolvedUrl("WelcomePage.qml")).createObject();
                newPage.welcomeText = i18n.tr("This application is under development.\nThere is nothing beyond this screen yet");
                newPage.startTestingTriggered.connect(function() { pageStack.pop() })
                pageStack.push(newPage);
            }
        }
        Button {
            text: i18n.tr("Automated test page")
            onClicked: {
                var newPage = Qt.createComponent(Qt.resolvedUrl("AutomatedTestPage.qml")).createObject();
                newPage.testName = "memory/info";
                newPage.testDescription = "This test checks the amount of memory which is reporting \
in meminfo against the size of the memory modules detected by DMI."
                pageStack.push(newPage);
            }
        }
        Button {
            text: i18n.tr("User-Interact-Verify introduction page")
            onClicked: {
                var newPage = Qt.createComponent(Qt.resolvedUrl("UserInteractVerifyIntroPage.qml")).createObject();
                newPage.testName = "Headphones playback";
                newPage.testDescription = "This test will check that headphones connector works correctly.\n\
STEPS:\n\
  1. Connect a pair of headphones to your audio device\n\
  2. Click the Test button to play a sound to your audio device";
                newPage.testStarted.connect(userInteractVerifyTestStarted);
                //Triggering of timer should change the state on UIV-intro page
                userInteractVerifyIntroTimer.triggered.connect(newPage.stopActivity)
                pageStack.push(newPage);
            }
        }
        Button {
            id: userInteractVerifyVerificationPageButton
            text: i18n.tr("User-Interact-Verify verification page")
            onClicked: {
                console.log(pageStack.currentPage);
                var newPage = Qt.createComponent(Qt.resolvedUrl("UserInteractVerifyVerificationPage.qml")).createObject();
                newPage.testName = "Headphones playback";
                newPage.verificationDescription = "Did you hear a sound through the headphones and did the sound \
play without any distortion, clicks or other strange noises from your headphones?";
                newPage.verificationDone.connect(userInteractVerifyVerificationDone);
                pageStack.push(newPage);
            }
        }
    }
    /*
      This timer emulates running test.
    */
    Timer {
        id: userInteractVerifyIntroTimer
        interval: 2000; running: false; repeat: false
        onTriggered: {
            userInteractVerifyVerificationPageButton.clicked();
        }
    }

    function userInteractVerifyTestStarted() {
        userInteractVerifyIntroTimer.start();
    }

    function userInteractVerifyVerificationDone(result) {
        /*
            This unwind pop until we're on screensPreviewPage
            Ordinary pageStack.pop() would'n work as there might be 1 or 2 pages on stack
        */
        while(pageStack.currentPage!=screensPreviewPage) {
            pageStack.pop();
        }
        console.log("userInteractVerifyVerificationDone called with result: "+result);
    }

}
