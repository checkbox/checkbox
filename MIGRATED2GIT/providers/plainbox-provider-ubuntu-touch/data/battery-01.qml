/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Sylvain Pineau <sylvain.pineau@canonical.com>
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
import io.thp.pyotherside 1.2
import Ubuntu.Components 0.1
import QtQuick.Layouts 1.1

Item {
    id: root
    signal testDone(var test)

    width: units.gu(100)
    height: units.gu(75)
    anchors.fill: parent

    property var duration: 1801
    property var threshold: 5
    property date startDate: new Date()
    property date endDate: new Date(startDate.getTime() + duration*1000)
    property date countdown: new Date(endDate - new Date());
    property var startPercentage;
    property var currentPercentage;

    Page {
        id: mainPage

        Alarm {
            id: alarm
        }

        Component.onDestruction: alarm.cancel()

        ColumnLayout {
            spacing: units.gu(1)
            anchors {
                margins: units.gu(2)
                fill: parent
                }

            Column {
                anchors.horizontalCenter: parent.horizontalCenter

                Label {
                    fontSize: "x-large"
                    text: "Time remaining:"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                Label {
                    id: time
                    fontSize: "x-large"
                    text: " "
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            Column {
                anchors.horizontalCenter: parent.horizontalCenter

                Label {
                    fontSize: "x-large"
                    text: i18n.tr("Battery level")
                }

                Label {
                    fontSize: "large"
                    text: i18n.tr("Initial: ") + startPercentage + "%"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Label {
                    fontSize: "large"
                    text: i18n.tr("Current: ") + currentPercentage + "%"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Label {
                    fontSize: "large"
                    text: i18n.tr("Limit: ") + (startPercentage - threshold) + "%"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            Button {
                text: i18n.tr("Skip")
                color: "#FF9900"
                Layout.fillWidth: true
                onClicked: {
                    alarm.cancel();
                    testDone({'outcome': 'skip'});
                }
            }
        }

        Timer {
            id: clockTimer
            interval: 1000; running: true; repeat: true
            onTriggered: {
                countdown = new Date(endDate - new Date());
                time.text = ("0" + countdown.getMinutes()).slice(-2) + ":" + ("0" + countdown.getSeconds()).slice(-2);
                if (countdown.valueOf() <= 0) {
                    currentPercentage = python.call_sync('upower.get_battery_percentage');
                    running = false
                    alarm.cancel();
                    batteryLevelTimer.running = false
                    if ((startPercentage - threshold) > currentPercentage) {
                        testDone({'outcome': 'fail'});
                    }
                    else {
                        testDone({'outcome': 'pass'});
                    }
                }
            }
        }

        Timer {
            id: batteryLevelTimer
            interval: 10000; running: true; repeat: true
            onTriggered: {
                python.call('upower.get_battery_percentage', [], function(result) {
                    currentPercentage=result
                });
                if ((startPercentage - threshold) > currentPercentage) {
                    alarm.cancel();
                    testDone({'outcome': 'fail'});
                }
            }
        }

        Python {
            id: python
            Component.onCompleted: {
                addImportPath(Qt.resolvedUrl('.'));
                importModule('upower', function() {});
                call('upower.get_battery_percentage', [], function(result) {startPercentage=result; currentPercentage=result});
                alarm.date = endDate;
                alarm.message = i18n.tr("Battery test completed");
                alarm.save();
                if (alarm.error != Alarm.NoError)
                    print("Error saving alarm, code: " + alarm.error);
            }
        }
    }
}
