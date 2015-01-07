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

/*! \brief Page for Qml native test
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1
import "ConfirmationLogic.js" as ConfirmationLogic

Page {
    id: qmlNativePage
    property var test: { "name": "", "description": "", "test_number": 0, "tests_count": 0}

    signal testDone(var test);

    objectName: "qmlNativePage"
    title: i18n.tr("Test Description")

    Object {
        id: testingShell
        property string name: "Checkbox-touch qml shell"

        property alias pageStack: innerPageStack

        function getTest() {
            return test;
        }
    }

    PageStack {
        id: innerPageStack
    }

    head {
        actions: [
            Action {
                id: skipAction
                iconName: "media-seek-forward"
                text: i18n.tr("Skip")
                onTriggered: {
                    var confirmationOptions = {
                        question : i18n.tr("Do you really want to skip this test?"),
                        remember : true,
                    }
                    ConfirmationLogic.confirmRequest(qmlNativePage,
                        confirmationOptions, function(res) {
                            if (res) {
                                test["outcome"] = "skip";
                                testDone(test);
                            }
                    });
                }
            }
        ]
    }

    ColumnLayout {
        id: body
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
                text: test["description"]
            }
        }

        Button {
            objectName: "continueButton"
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Continue")
            onClicked: {
                loader.source = test['qml_file'];
                pageStack.push(innerPageStack);
                loader.item.testDone.connect(function(testResult) {
                    test['outcome'] = testResult['outcome'];
                    test['result'] = testResult;
                    pageStack.pop();
                    testDone(test);
                });
                loader.item.testingShell = testingShell;
                innerPageStack.push(loader.item);
            }
        }
    }

    Loader {
        id: loader
        visible: false
    }
}
