/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
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

/*! \brief Page displaying an output of running command

*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import Ubuntu.Components.Popups 0.1
import QtQuick.Layouts 1.1

Page {
    id: commandOutputPage

    objectName: "commandOutputPage"

    function addText(text) {
        textArea.text += text;
    }

    function clear() {
        textArea.text = "";
    }

    title: i18n.tr("Command output")

    ColumnLayout {
        spacing: units.gu(1)
        anchors.fill: parent
        anchors.margins: units.gu(3)
        TextArea {
            id: textArea
            Layout.fillHeight: true
            Layout.fillWidth: true
            readOnly: true
            font.family: "Ubuntu Mono"

            wrapMode: TextEdit.WrapAnywhere

            Scrollbar {
                flickableItem: textArea
                align: Qt.AlignTrailing
            }

            MimeData {
                id: mimeData
                text: textArea.text
            }

            MouseArea {
                anchors.fill: parent
                onClicked: Clipboard.push(mimeData);
            }

            Rectangle {
                id: popUp
                anchors.centerIn: parent
                opacity: 0.9
                radius: 10
                color: UbuntuColors.lightGrey
                height: label.height * 3
                width: label.width * 1.5
                Label {
                    id: label
                    anchors.centerIn: parent
                    text: i18n.tr("Tap on the text to copy it to clipboard")
                    color: "white"
                    fontSize: "large"
                }

                Timer {
                    id: fadeOutDelay
                    interval: 3000
                    onTriggered: animateOpacity.start();
                    running: false
                }

                NumberAnimation {
                    id: animateOpacity
                    target: popUp
                    properties: "opacity"
                    from: 0.9
                    to: 0
                    easing {type: Easing.InQuad; overshoot: 500}
                }
            }

            onTextChanged: {
                cursorPosition = text.length;
            }
        }

        Button {
            Layout.fillWidth: true
            text: i18n.tr("Back")
            onClicked: pageStack.pop()
        }

    }
    onVisibleChanged: {
        // Pop-over should be displayed only when page becomes visible (in practice - when it's pushed to the pageStack)
        if (visible == true) fadeOutDelay.start();
    }
}
