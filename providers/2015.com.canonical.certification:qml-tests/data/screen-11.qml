/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Jonathan Cave <jonathan.cave@canonical.com>
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
import QtQuick.Layouts 1.1

Item {
    id: root

    anchors.fill: parent

    property var testingShell
    signal testDone(var test)

    Page {
        id: screenTest

        anchors.fill: parent

        ColumnLayout {
            anchors.fill: parent

            Label {
                id: titleText

                Layout.alignment: Qt.AlignHCenter
                Layout.fillWidth: true

                text: i18n.tr("Attempt to perform a"
                                + " long press on the green button below")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                fontSize: "x-large"
            }

            ActivityIndicator {
                id: pressedActivity

                Layout.alignment: Qt.AlignHCenter | Qt.Top

                visible: true
                running: false
            }

            Label {
                id: activityLabel

                Layout.preferredWidth: units.gu(30)
                Layout.minimumHeight: units.gu(10)
                Layout.alignment: Qt.AlignHCenter

                text: i18n.tr("Waiting for press...")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                horizontalAlignment: Text.AlignHCenter
                fontSize: "large"
            }

            Button {
                text: i18n.tr("Press and hold")
                Layout.preferredWidth: units.gu(30)
                Layout.preferredHeight: units.gu(10)
                Layout.alignment: Qt.AlignHCenter
                color: UbuntuColors.green

                MouseArea {
                    anchors.fill: parent

                    onClicked: {
                        pressedActivity.running = false
                        activityLabel.text = i18n.tr("That was a click... try holding for longer")
                    }
                    onPressed: {
                        pressedActivity.running = true
                        activityLabel.text = i18n.tr("Button pressed...")
                    }
                    onReleased: {
                        if (pressedActivity.running == true) {
                            activityLabel.text = i18n.tr("Press aborted.. try again")
                            pressedActivity.running = false
                        }
                    }
                    onPressAndHold: {
                        pressedActivity.running = false
                        activityLabel.text = i18n.tr("Success... Detected a long press")

                        testDone({'outcome': 'pass'})
                    }
                }
            }

            RowLayout {
                id: endTestRow
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter

                Button {
                    id: skipButton
                    text: i18n.tr("Skip the test")
                    Layout.preferredWidth: units.gu(15)
                    Layout.preferredHeight: units.gu(5)
                    Layout.alignment: Qt.AlignHCenter
                    color: "#FF9900"

                    onClicked: testDone({'outcome': 'skip'})
                }

                Button {
                    id: failButton
                    text: i18n.tr("Fail the test")
                    Layout.preferredWidth: units.gu(15)
                    Layout.preferredHeight: units.gu(5)
                    Layout.alignment: Qt.AlignHCenter
                    color: UbuntuColors.red

                    onClicked: testDone({'outcome': 'fail'})
                }
            }
        }
    }
}

