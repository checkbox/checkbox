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

/*! \brief Page for Automated Test

    This page shows test name and description of an Automated Test
    See design document at: http://goo.gl/He06jc
*/

Page {
    id: automatedTestPage

    property var test: { "name": "", "description": "" }

    title: i18n.tr("Automated test")

    visible: false

    ColumnLayout {
        spacing: units.gu(3)
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            margins: units.gu(3)
        }

        ProgressBox {
            interlude: i18n.tr("Current job:")
            value: test.test_number
            maximumValue: test.tests_count
            height: units.gu(3)
        }

        Label {
            fontSize: "large"
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            Layout.alignment: Qt.AlignLeft
            text: test["name"]
            font.bold: true
        }

        Label {
            fontSize: "medium"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: test["description"]
        }
    }
    ActivityIndicator {
        id: activity
        anchors {
            bottom: parent.bottom
            left: parent.left
            right: parent.right
            bottomMargin: units.gu(4)
        }
        implicitHeight: units.gu(6)
        implicitWidth: units.gu(6)
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
