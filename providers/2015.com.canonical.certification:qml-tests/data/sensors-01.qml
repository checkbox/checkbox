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
import QtSensors 5.2
import QtQuick.Layouts 1.1
import QtQuick.Window 2.2


Item {
    id: root
    signal testDone(var test)
    property var testingShell

    width: units.gu(100)
    height: units.gu(75)

    readonly property var ballSize: units.gu(5)
    property var posX: mainPage.width/2 - ballSize/2
    property var posY: mainPage.height/8 - ballSize/2

    property var testPassed

    anchors.fill: parent

    Page {
        id: mainPage

        ColumnLayout {
            spacing: units.gu(1)
            anchors {
                margins: units.gu(2)
                fill: parent
            }

            Label {
                id: instruction
                text: i18n.tr("Tilt the device to place the red ball in the green box")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                Layout.fillWidth: true
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                Layout.preferredWidth: units.gu(10)

            }

            Label {
                id: outcomeLabel
                visible: false
                text: testPassed ? i18n.tr("PASSED") : i18n.tr("FAILED")
                color: testPassed ? UbuntuColors.green : UbuntuColors.red
                Layout.fillWidth: true
                Layout.preferredWidth: units.gu(10)
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: units.gu(7)
                function showResult(passed) {
                    ticker.stop();
                    failButton.visible = false;
                    instruction.visible = false;
                    outcomeLabel.visible = true;
                    testPassed = passed;
                    summaryTimer.start();
                }
            }

            Button {
                id: failButton
                text: i18n.tr("I'm unable to move the dot")
                anchors.bottom: parent.bottom
                Layout.fillWidth: true
                onClicked: outcomeLabel.showResult(false)
            }
        }

        Rectangle {
            id: goal
            property var goalSizeX: units.gu(15)
            property var goalSizeY: units.gu(10)
            x: mainPage.width / 2 - goalSizeX / 2
            y: (mainPage.height / 8) * 5 - goalSizeY / 2
            color: "green"
            height: goalSizeY
            width: goalSizeX
        }

        Rectangle {
            id: ball
            x: posX
            y: posY
            color: "red"
            width: ballSize
            height: ballSize
            radius: width*0.5
        }

        Timer {
            id: ticker
            interval: 20
            running: true
            onTriggered: {
                posX-=accelerometer.reading.x;
                posY+=accelerometer.reading.y;

                if(posX < 0) posX = 0;
                if(posX + ballSize > mainPage.width) posX = mainPage.width - ballSize;
                if(posY < 0) posY = 0;
                if(posY + ballSize > mainPage.height) posY = mainPage.height - ballSize;

                if(posX >= goal.x && posX+ballSize < goal.x+goal.goalSizeX &&
                   posY >= goal.y && posY+ballSize < goal.y+goal.goalSizeY) {
                    outcomeLabel.showResult(true);
                }
            }
            repeat: true
        }

        Timer {
            id: summaryTimer
            interval: 1000
            onTriggered: {
                testDone({'outcome': testPassed ? "pass" : "fail"})
            }
        }
    }

    Accelerometer {
        id: accelerometer
        active: true
    }
}


