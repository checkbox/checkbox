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
import Ubuntu.Components.Popups 0.1
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
        property alias pageStack: qmlNativePage.pageStack
        property string sessionDir: app.sessionDir
        function getTest() {
            return test;
        }
    }

    head {
        actions: [
            Action {
                id: addCommentAction
                iconName: "document-new-symbolic"
                text: i18n.tr("Add comment")
                onTriggered: {
                    commentsDialog.commentDefaultText = test["comments"] || "";
                    commentsDialog.commentAdded.connect(function(comment) {
                        test["comments"] = comment;
                    });
                    PopupUtils.open(commentsDialog.dialogComponent);
                }
            },
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
                text: test["description"]
            }
        }

        LatchButton {
            objectName: "continueButton"
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Continue")
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
