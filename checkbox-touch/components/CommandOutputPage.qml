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
    property var bufferedIO;

    function addText(text) {
        bufferedIO += text
    }

    function clear() {
        bufferedIO = "";
        textArea.text = "";
    }

    title: i18n.tr("Command output")
    head {
        actions: [
            Action {
                id: skipAction
                objectName: "copyOutputAction"
                iconName: "edit-copy"
                // TRANSLATORS: a verb (call to action)
                text: i18n.tr("Copy")
                onTriggered: Clipboard.push(mimeData)
            }
        ]
    }

    Timer {
        id: timer
        interval: 300
        running: false
        repeat: true
        onTriggered: {
            textArea.text += bufferedIO
            bufferedIO = ""
        }
    }

    ColumnLayout {
        spacing: units.gu(1)
        anchors.fill: parent
        anchors.margins: units.gu(3)
        TextArea {
            id: textArea
            objectName: "textArea"
            Layout.fillHeight: true
            Layout.fillWidth: true
            readOnly: true
            font.family: "Ubuntu Mono"

            wrapMode: TextEdit.WrapAnywhere

            MimeData {
                id: mimeData
                text: textArea.text
            }

            onTextChanged: {
                cursorPosition = text.length;
            }
        }

        Button {
            Layout.fillWidth: true
            // TRANSLATORS: This is a label on the button that goes back a page
            text: i18n.tr("Back")
            onClicked: pageStack.pop()
        }

    }
    onVisibleChanged: {
        // Pop-over should be displayed only when page becomes visible (in practice - when it's pushed to the pageStack)
        if (visible == true) {
            timer.running = true;
        }
        else {
            timer.running = false;
        }
    }
}
