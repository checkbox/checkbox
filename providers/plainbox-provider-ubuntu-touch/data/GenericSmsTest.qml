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
import QtQuick 2.2
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1


PageStack {

    id: pageStack
    Component.onCompleted: push(genericSmsTest)

    function setTestActionText(actionText) {
        titleText.text = actionText
    }

    function setPredefinedContent(textString) {
        contentsArea.text = textString
    }

    property var modemPath

    Page {
        id: genericSmsTest

        anchors.fill: parent
        visible: false

        OfonoDbus {
            id: ofonoDbus
        }

        Flickable {
            id: sampleFlickable

            clip: true
            contentHeight: mainColumn.height
            anchors {
                top: parent.top
                left: parent.left
                right: parent.right
                bottom: parent.bottom

                bottomMargin: units.gu(2)
            }

            ColumnLayout {
                id: mainColumn
                spacing: units.gu(2)

                anchors {
                    top: parent.top
                    left: parent.left
                    right: parent.right
                    margins: units.gu(2)
                }

                Label {
                    id: titleText

                    Layout.fillWidth: true
                    width: parent.width

                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    fontSize: "x-large"
                }

                TextField {
                    id: telNumField
                    placeholderText: i18n.tr("Enter number")

                    width: parent.width
                    Layout.alignment: Qt.AlignHCenter

                    inputMethodHints: Qt.ImhDialableCharactersOnly
                }

                TextArea {
                    id: contentsArea

                    placeholderText: i18n.tr("SMS Content")

                    width: parent.width
                    height: units.gu(12)
                    Layout.alignment: Qt.AlignHCenter
                }

                Button {
                    id: sendButton

                    text: i18n.tr("Send SMS")

                    width: parent.width
                    height: units.gu(12)
                    Layout.alignment: Qt.AlignHCenter

                    color: UbuntuColors.green

                    onClicked: {
                        ofonoDbus.ts_send_sms(modemPath, telNumField.text,
                                                contentsArea.text)
                        pageStack.push(genericSummaryPage)
                    }
                }
            }
        }
    }

    Page {
        id: genericSummaryPage

        visible: false
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: units.gu(2)
            Label {
                text: i18n.tr("Was the SMS received correctly?")
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