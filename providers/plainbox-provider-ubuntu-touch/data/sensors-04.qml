/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Zygmunt Krynicki <zygmunt.krynicki@canonical.com> 
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
import QtFeedback 5.0
import QtQuick 2.0
import QtQuick.Layouts 1.1
import Ubuntu.Components 1.1


Item {
    id: root
    signal testDone(var test)
    property var testingShell

    width: units.gu(100)
    height: units.gu(75)

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
                text: i18n.tr("Tap the button below to use the haptics system of this device")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                Layout.fillWidth: true
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                Layout.preferredWidth: units.gu(10)

            }

            Button {
                objectName: "button"
                width: parent.width
                text: i18n.tr("Activate Haptics")
                Layout.fillWidth: true
                onClicked: {
                    rumbleEffect.start();
                }
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

                Button {
                    text: i18n.tr("Skip")
                    color: "#FF9900"
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    onClicked: testDone({'outcome': 'skip'});
                }
            }

        }

        HapticsEffect {
            id: rumbleEffect
            attackIntensity: 0.0
            attackTime: 250
            intensity: 1.0
            duration: 100
            fadeTime: 250
            fadeIntensity: 0.0
        }
    }
}


