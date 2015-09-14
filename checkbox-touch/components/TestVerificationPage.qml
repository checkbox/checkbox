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

/*! \brief Test verification page

    This page asks user whether the action was completed successfully
    See design document at: http://goo.gl/ghR9wL
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1
import Ubuntu.Components.Popups 0.1
import "actions"

Page {
    id: testVerification
    property var test: { "name": "", "verificationDescription": "", "test_number": 0, "tests_count": 0}

    signal testDone(var test);

    objectName: "testVerificationPage"
    title: i18n.tr("Verification")

    head {
        actions: [
            AddCommentAction {},
            SkipAction {}
        ]
    }

    ColumnLayout {
        id: descriptionContent
        spacing: units.gu(3)
        anchors {
            fill: parent
            topMargin: units.gu(3)
            bottomMargin: units.gu(3)
            leftMargin: units.gu(1)
            rightMargin: units.gu(1)
        }

        Label {
            fontSize: "large"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: test["name"]
            font.bold: true
        }

        Flickable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentHeight: childrenRect.height
            flickableDirection: Flickable.VerticalFlick
            clip: true
            Label {
                fontSize: "medium"
                anchors.fill: parent
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                text: test["verificationDescription"]
            }
        }

        Button {
            id: showOutputButton
            objectName: "showOutputButton"
            visible: ((test["command"]) ? true : false)
            color: "white"
            Layout.fillWidth: true
            text: "Output"
            onClicked: {
                pageStack.push(commandOutputPage);
            }
        }

        LatchButton {
            id: passButton
            objectName: "passButton"
            unlatchedColor: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Pass")
            onLatchedClicked: {
                test["outcome"] = "pass";
                latchingTestDone();

            }
        }

        LatchButton {
            id: failButton
            objectName: "failButton"
            unlatchedColor: UbuntuColors.red
            Layout.fillWidth: true
            text: i18n.tr("Fail")
            onLatchedClicked: {
                test["outcome"] = "fail";
                latchingTestDone();
            }
        }
    }

    function latchingTestDone() {
        passButton.state = "latched";
        failButton.state = "latched";
        testDone(test);
    }
}
