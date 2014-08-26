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

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1

Page {
    id: screensPreviewPage
    title: i18n.tr("Screens preview")
    visible: false

    ColumnLayout {
        spacing: units.gu(3)
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            margins: units.gu(1)
        }
        Label {
            fontSize: "x-large"
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: i18n.tr("This is a developer screen that allows you to preview particular part of the app.\nSelect which screen to preview")
        }
        Button {
            text: i18n.tr("Welcome page")
            onClicked:{
                pageStack.push(Qt.resolvedUrl("WelcomePage.qml"), {
                                   "welcomeText": i18n.tr("This application is under development.\nThere is nothing beyond this screen yet")
                               })
            }
        }
        Button {
            text: i18n.tr("Automated test page")
            onClicked:{
                pageStack.push(Qt.resolvedUrl("AutomatedTestPage.qml"), {
                                   "testName": "memory/info",
                                   "testDescription": "This test checks the amount of memory which is reporting in meminfo against the size of the memory modules detected by DMI."
                               })
            }
        }
    }
}
