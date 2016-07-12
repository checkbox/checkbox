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

/*! \brief Page for Qml native test
*/

import QtQuick 2.0
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 0.1
import QtQuick.Layouts 1.1
import Ubuntu.Content 1.1
import "actions"

Page {
    id: qmlNativePage
    property var test: { "name": "", "description": "", "test_number": 0, "tests_count": 0}
    property var applicationVersion: ""

    signal testDone(var test);

    objectName: "qmlNativePage"

    /* testingShell serves as the interface to the external world from the
     * qml-test. */
    Object {
        id: testingShell
        property string name: "Checkbox-touch qml confined shell"
        property alias pageStack: qmlNativePage.pageStack
        property string sessionDir: app.sessionDir
        property var python: app.py
        function getTest() {
            return test;
        }
    }

    Connections {
        target: ContentHub
        onImportRequested: {
            var resultFile = String(transfer.items[0].url).replace(
                'file://', '');
            var xhr = new XMLHttpRequest;
            xhr.open("GET", resultFile);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    try {
                        var result = JSON.parse(xhr.responseText);
                        test["outcome"] = result["outcome"];
                        testDone(test);
                    } catch (x) {
                        console.error("ERROR when parsing result json obj.")
                    }
                }
            }
            xhr.send();
            transfer.finalize();
        }
    }

    onTestChanged: {
        header.value = test['test_number']
        header.maximumValue = test['tests_count']
    }
    header: ProgressHeader {
        value: test['test_number']
        maximumValue: test['tests_count']
        title: i18n.tr("Test Description")
        leadingActionBar { actions: [] }
        trailingActionBar {
            objectName: 'trailingActionBar'
            actions: [
                AddCommentAction {
                    id: addCommentAction
                },
                SkipAction {
                    id: skipAction
                }
            ]
        }
    }

    TestPageBody {
        header: test["name"]
        body: test["description"]

        ColumnLayout {
            id: busyIndicatorGroup
            visible: false
            Layout.fillWidth: true
            Layout.fillHeight: true

            Label {
                fontSize: "large"
                Layout.fillWidth: true
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                text: i18n.tr("Waiting for the test to finish")
                font.bold: true
            }
        }

        LatchButton {
            id: continueButton
            objectName: "continueButton"
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Start the test")
            onClicked: {
                var appName = "com.ubuntu.checkbox_" + test["partial_id"];
                // load the test qml file to check which permissions should be cleared
                var testItemComponent = Qt.createComponent(Qt.resolvedUrl(test['qml_file']));
                if (testItemComponent.status == Component.Error) {
                    console.error("Error creating testItemComponent. Possible cause: Problem with job's qml file. Error:", testItemComponent.errorString());
                    test['outcome'] = 'fail';
                    testDone(test);
                    return;
                }
                var testItem = testItemComponent.createObject(dummyContainer, {"testingShell": testingShell});
                var clearedPermissions = testItem.clearedPermissions;
                testItem.destroy();
                var runConfinedTestApp = function() {
                    busyIndicatorGroup.visible = true;
                    Qt.openUrlExternally("application:///" + appName + "_" + applicationVersion+ ".desktop");
                }
                if (clearedPermissions) {
                    app.dropPermissions(appName, clearedPermissions, function() {
                        runConfinedTestApp();
                    });
                } else {
                    runConfinedTestApp();
                }

            }
        }
        Item {
            id: dummyContainer
            visible: false
        }
    }
    Component.onCompleted: {
        rootKeysDelegator.setHandler('alt+s', qmlNativePage, skipAction.trigger);
        rootKeysDelegator.setHandler('alt+c', qmlNativePage, addCommentAction.trigger);
        rootKeysDelegator.setHandler('alt+t', qmlNativePage, continueButton.clicked);
    }
}
