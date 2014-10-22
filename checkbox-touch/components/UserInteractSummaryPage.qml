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

/*! \brief Page for User-Interact test - summary step

    This page shows result of automated verification of a test.
    See design document at: http://goo.gl/6pNAFE
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1

Page {
    property var test: { "name": "", "outcome": "pass"}

    signal testDone(var test);

    title: i18n.tr("Verification")

    head {
        actions: [
            Action {
                iconName: "media-seek-forward"
                text: i18n.tr("Skip")
                onTriggered: {
                    test["outcome"] = 'skip';
                    testDone(test);
                }
            }
        ]
    }

    ColumnLayout {
        spacing: units.gu(3)
        anchors.fill: parent
        anchors.margins: units.gu(3)

        Label {
            fontSize: "large"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: test["name"]
            font.bold: true
        }

        Row {
            Layout.fillWidth: true
            Label {
                fontSize: "large"
                Layout.fillHeight: true
                text : i18n.tr("This test ")
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            }

            Rectangle {
                height: resultLabel.height
                width: resultLabel.width + units.gu(1)
                Layout.alignment: Qt.AlignCenter
                radius: 2
                color: test["outcome"] == "pass" ? UbuntuColors.green : UbuntuColors.red

                Label {
                    id: resultLabel
                    height: paintedHeight
                    fontSize: "large"
                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                    color: "white"
                    text : test["outcome"] == "pass" ? i18n.tr("PASSED") : i18n.tr("FAILED")
                    anchors.centerIn: parent
                }
            }
        }

        Label {
            fontSize: "large"
            Layout.fillHeight: true
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text : i18n.tr("You can go back to rerun it or continue to the next test.")
        }

        Button {
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Continue")
            onClicked: {
                testDone(test);
            }
        }
    }
}
