/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Maciej Kisielewski <maciej.kisielewski@canonical.com>
 *
 * Checkbox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3,
 * as published by the Free Software Foundation.
 *
 * Checkbox is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
 */
import QtQuick 2.0
import Ubuntu.Components 1.1
import QtMultimedia 5.2
import QtQuick.Layouts 1.1
import QtQuick.Window 2.0

Item {
    id: root

    anchors.fill: parent

    property var testingShell
    property var recordingSecondsRemaining: 0
    readonly property var recordingLength: 10
    property var recordingPath

    signal testDone(var test)

    function start() {
        state = 'intro';
        cam.start();
    }

    function startRecording() {
        recordingPath = testingShell["sessionDir"] + "/recording.mp4";
        cam.videoRecorder.captureMode = Camera.CaptureVideo;
        cam.videoRecorder.outputLocation = recordingPath
        recordingSecondsRemaining = recordingLength;
        recordingTimer.start();
        cam.videoRecorder.record();
        state = "recording"
    }

    function stopRecording() {
        cam.videoRecorder.stop()
        cam.stop();
        mediaplayer.source = recordingPath
        mediaplayer.play();
        state = "playback"
    }

    function showSummary(prompt) {
        state = "summary"
        mediaplayer.stop();
        cam.stop();
        outcomeLabel.text = prompt || "";
    }

    function intro() {
        state = "intro"
        cam.start();
    }

    function die(msg) {
        console.error(msg);
        showSummary(msg);
    }

    state: ""

    Component.onCompleted: start()

    Camera {
        id: cam
        captureMode: Camera.CaptureViewfinder
        onError: die(i18n.tr("Error when initiating camera component: " + cam.errorString))
        videoRecorder {
            onError: die(i18n.tr("Error encountered in videoRecorder component: " + cam.videoRecorder.errorString))
        }
    }

    VideoOutput {
        id: viewfinder
        visible: root.state != "summary"
        source: cam
        anchors.fill: parent
        orientation: (Screen.primaryOrientation === Qt.PortraitOrientation) ? 270 : 0;
        fillMode: Image.PreserveAspectCrop
    }

    Timer {
        id: recordingTimer
        interval: 1000
        running: false
        repeat: true
        onTriggered: {
            if (!--recordingSecondsRemaining) {
                recordingTimer.stop();
                stopRecording();
            }
        }
    }


    Page {
        id: startingPage

        visible: root.state == "intro"

        Button {
            width: units.gu(20)
            height: units.gu(5)
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            text: i18n.tr("Start recording")
            color: UbuntuColors.green
            onClicked: startRecording()
        }
    }

    Page {
        id: recordingInProgressPage

        visible:  root.state == "recording"

        Text {
            font.pixelSize: units.gu(10)
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            text: recordingSecondsRemaining
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            color: "white"
            style: Text.Outline
            styleColor: "grey"
        }
    }
    Page {
        id: playbackPage

        anchors.fill: parent
        visible:  root.state == "playback"

        MediaPlayer {
            id: mediaplayer
            autoLoad: false
            autoPlay: false
            onStatusChanged: {
                if (status == 3) { // loaded
                    var handleStop = function() {
                        if (playbackState == 0 && root.state == "playback") {
                            showSummary(i18n.tr("Was the recording OK?"));
                        }
                    }
                    onPlaybackStateChanged.connect(handleStop);
                }
            }
            onError: die("Error with playback: " + errorString)
        }

        VideoOutput {
            anchors.fill: parent
            source: mediaplayer
            orientation: (Screen.primaryOrientation === Qt.PortraitOrientation) ? 270 : 0;
            fillMode: Image.PreserveAspectCrop
        }
    }
    Page {
        id: summaryPage

        visible:  root.state == "summary"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: units.gu(5);
            spacing: units.gu(2)

            Label {
                id: outcomeLabel
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                fontSize: "x-large"
                style: Text.Outline
                styleColor: "grey"
            }

            ColumnLayout {
                spacing: units.gu(5)
                Layout.fillWidth: true
                anchors.margins: units.gu(20);
                Layout.preferredHeight: units.gu(50)

                Button {
                    text: i18n.tr("Pass")
                    color: UbuntuColors.green
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    onClicked: testDone({'outcome': 'pass'});
                }

                Button {
                    text: i18n.tr("Fail")
                    color: UbuntuColors.red
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    onClicked: testDone({'outcome': 'fail'});
                }
            }

            Button {
                text: i18n.tr("Restart")
                Layout.preferredHeight: units.gu(5)
                Layout.alignment: Qt.AlignHCenter
                onClicked: start()
            }
        }
    }

    states: [
        State { name: "intro" },
        State { name: "recording" },
        State { name: "playback" },
        State { name: "summary" }
    ]
}
