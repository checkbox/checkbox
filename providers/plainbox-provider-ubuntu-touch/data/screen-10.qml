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
import QtQuick.Layouts 1.1

Item {
    id: root

    anchors.fill: parent

    property var testingShell
    signal testDone(var test)

    Page {
        id: introPage
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: units.gu(2)
            Label {
                text: i18n.tr("Tap or click on the green squares that show up"
                              + " on the screen\nIf you're unable to complete"
                              + " the test, tap or click the screen 3 times")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                Layout.fillWidth: true
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                fontSize: "large"
            }
            Button {
                text: i18n.tr("Start")
                Layout.preferredWidth: units.gu(30)
                Layout.preferredHeight: units.gu(10)
                Layout.alignment: Qt.AlignHCenter
                color: UbuntuColors.green
                onClicked: {
                    introPage.visible = false;
                    screenTest.visible = true;
                    var myRandom = function() {
                        // generate random integer close to 0 (from both sides)
                        var max = 5;
                        return Math.floor(Math.random() * max * 2 - max);
                    }
                    for (var i = 0; i < 10; i++) {
                        // x should be near edges, so small negative or small
                        // positive number
                        // y should be near the bottom, so small negative
                        // numbers(no zeros)
                        screenTest.addTarget(
                            {"x": myRandom(),
                             "y": - (Math.ceil(Math.random() * 8))});
                    }
                    screenTest.runTest();
                }
            }
            Button {
                text: i18n.tr("Skip the test")
                Layout.preferredWidth: units.gu(30)
                Layout.preferredHeight: units.gu(10)
                Layout.alignment: Qt.AlignHCenter
                color: "#FF9900"
                onClicked: testDone({'outcome': 'skip'})
            }
        }
    }

    ScreenTest {
        id: screenTest
        visible: false
        onAllTargetsHit: {
            screenTest.visible = false;
            summaryPage.visible = true;
        }
        onTripleClicked: allTargetsHit()
    }
    Page {
        id: summaryPage

        visible: false
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: units.gu(2)
            Label {
                text: i18n.tr("Are you satisfied with screen's accuracy?")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                Layout.fillWidth: true
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                fontSize: "x-large"
            }
            Button {
                text: i18n.tr("Yes")
                Layout.preferredWidth: units.gu(30)
                Layout.preferredHeight: units.gu(10)
                Layout.alignment: Qt.AlignHCenter
                color: UbuntuColors.green
                onClicked: testDone({'outcome': 'pass'})
            }
            Button {
                text: i18n.tr("No")
                Layout.preferredWidth: units.gu(30)
                Layout.preferredHeight: units.gu(10)
                Layout.alignment: Qt.AlignHCenter
                color: UbuntuColors.red
                onClicked: testDone({'outcome': 'fail'})
            }
            Button {
                text: i18n.tr("Skip the test")
                Layout.preferredWidth: units.gu(30)
                Layout.preferredHeight: units.gu(10)
                Layout.alignment: Qt.AlignHCenter
                color: "#FF9900"
                onClicked: testDone({'outcome': 'skip'})
            }
        }
    }
}
