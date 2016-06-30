/*
 * This file is part of Checkbox
 *
 * Copyright 2014, 2015 Canonical Ltd.
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
import Ubuntu.Components 1.3
import QtQuick.Layouts 1.1

/*! \brief Page for Automated Test

    This page shows test name and description of an Automated Test
    See design document at: http://goo.gl/He06jc
*/

Page {
    id: automatedTestPage

    objectName: "automatedTestPage"

    property var test: { "name": "", "description": "", "test_number": 0, "tests_count": 0}

    visible: false

    header: ProgressHeader {
        value: test['test_number']
        maximumValue: test['tests_count']
        title: i18n.tr("Automated test")
    }

    TestPageBody {
        header: test["name"]
        body: test["description"]
    }
    ColumnLayout {
        anchors {
            bottom: parent.bottom
            left: parent.left
            right: parent.right
            bottomMargin: units.gu(4)
        }
        ActivityIndicator {
            Layout.alignment: Qt.AlignHCenter
            id: activity
            implicitHeight: units.gu(6)
            implicitWidth: units.gu(6)
        }
        Button {
            id: showOutputButton
            objectName: "showOutputButton"
            visible: ((test["command"]) ? true : false) && activity.running
            color: "white"
            Layout.fillWidth: true
            text: "Output"
            onClicked: {
                pageStack.push(commandOutputPage);
            }
        }
    }
    function startActivity() {
        activity.running = true;
    }
    function stopActivity() {
        activity.running = false;
    }
    Component.onCompleted: {
        startActivity();
    }
}
