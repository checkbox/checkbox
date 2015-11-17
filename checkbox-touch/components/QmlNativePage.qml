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

/*! \brief Page for Qml native test
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import Ubuntu.Components.Popups 0.1
import QtQuick.Layouts 1.1
import "actions"

Page {
    id: qmlNativePage
    property var test: { "name": "", "description": "", "test_number": 0, "tests_count": 0}

    signal testDone(var test);

    objectName: "qmlNativePage"
    title: i18n.tr("Test Description")

    Object {
        id: testingShell
        property string name: "Checkbox-touch qml shell"
        property alias pageStack: qmlNativePage.pageStack
        property string sessionDir: app.sessionDir
        property var python: app.py
        function getTest() {
            return test;
        }
    }

    head {
        actions: [
            AddCommentAction {},
            SkipAction {}
        ]
    }

    TestPageBody {
        header: test["name"]
        body: test["description"]

        LatchButton {
            objectName: "continueButton"
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Start the test")
            onClicked: {
                pageStack.pop(); // pop the description page
                // altough there shouldn't be anything on the page stack
                // dump it to savedStack and clear page stack,
                // to let qml job use fresh playground
                var savedStack = [];
                while(pageStack.depth) {
                    savedStack.push(pageStack.currentPage);
                    pageStack.pop();
                }
                // prepare page with the test
                var testItemComponent = Qt.createComponent(Qt.resolvedUrl(test['qml_file']));
                if (testItemComponent.status == Component.Error) {
                    console.error("Error creating testItemComponent. Possible cause: Problem with job's qml file. Error:", testItemComponent.errorString());
                    test['outcome'] = 'fail';
                    testDone(test);
                    return;
                }

                var testItem = testItemComponent.createObject(mainView, {"testingShell": testingShell});
                testItem.testDone.connect(function(testResult) {
                    test['outcome'] = testResult['outcome'];
                    test['qmlResult'] = testResult;
                    pageStack.clear(); // clean test's left-overs from the stack
                    while(savedStack.length) {
                        pageStack.push(savedStack.pop());
                    }
                    testItem.destroy();
                    testDone(test);
                });
            }
        }
    }
}
