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
import QtMultimedia 5.0
import QtQuick.Layouts 1.1
Item {
    id: root
    signal testDone(var test)
    property var testingShell

    Component.onCompleted: testingShell.pageStack.push(introPage)

    Page {
        id: introPage
        title: i18n.tr("Camera test")
        visible: false

        ColumnLayout {
            spacing: units.gu(5)
            anchors.fill: parent
            anchors.margins: units.gu(3)
            Label {
                fontSize: "large"
                Layout.fillWidth: true
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                text: i18n.tr("On the next screen you'll see video feed from \
your camera. Decide whether camera is working correctly, and tap corresponding \
button.")
                font.bold: true
            }
            Button {
                text: i18n.tr("Start the test")
                Layout.fillWidth: true
                onClicked: {
                    testingShell.pageStack.push(subpage);
                }
            }
        }
    }

    Page {
        id: subpage
        visible: false
        title: i18n.tr("Camera test")
        VideoOutput {
            id: viewfinder
            source: cam
            anchors.fill: parent
            orientation: 270
        }

        Camera {
            id: cam
        }

        ColumnLayout {
            spacing: units.gu(1)
            anchors {
                fill: parent
            }
            Button {
                width: units.gu(10)
                height: units.gu(5)
                Layout.alignment: Qt.AlignHCenter
                text: i18n.tr("Camera works")
                color: UbuntuColors.green
                onClicked: {
                    testDone({'outcome': 'pass'});
                }
            }
            Button {
                width: units.gu(10)
                height: units.gu(5)
                Layout.alignment: Qt.AlignHCenter
                text: i18n.tr("Camera doesn't work")
                color: UbuntuColors.red
                onClicked: {
                    testDone({'outcome': 'fail'});
                }
            }
        }
    }
}
