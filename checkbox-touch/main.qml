/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
 *
 * Authors:
 * - Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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
import io.thp.pyotherside 1.2
import "components"
import "components/ErrorLogic.js" as ErrorLogic


/*!
    \brief MainView with a Label and Button elements.
*/

MainView {
    id: mainView

    // objectName for functional testing purposes (autopilot-qt5)
    objectName: "mainView"

    // Note! applicationName needs to match the "name" field of the click manifest
    applicationName: "com.canonical.certification.checkbox-touch"

    /*
     This property enables the application to change orientation
     when the device is rotated. The default is false.
    */
    //automaticOrientation: true

    width: units.gu(100)
    height: units.gu(75)

    useDeprecatedToolbar: false

    // appSettings serves as application-wide storage for global variables
    // it has to have at least one entry to be constructed
    property var appSettings: {
        "applicationName" : applicationName,
        "revision": "unknown revision",
        "testplan": ""
    }

    Component.onCompleted: {
        var xhr = new XMLHttpRequest;
        xhr.open("GET", "settings.json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                try {
                    appSettings = JSON.parse(xhr.responseText);
                } catch (x) {
                    // if we cannot parse settings.json, we should leave
                    // deafult values of appSettings
                    console.log("Could not parse settings.json. Using default values")
                }
            }
        }
        xhr.send();
    }


    // Pyotherside python object that we use to talk to all of plainbox
    Python {
        id: py
        Component.onCompleted: {
            console.log("Pyotherside version " + pluginVersion());
            console.log("Python version " + pythonVersion());
            // A bit hacky but that's where the python code is
            addImportPath(Qt.resolvedUrl('py/'));
            // Import path for plainbox and potentially other python libraries
            addImportPath(Qt.resolvedUrl('lib/py'))
            // Import the checkbox_touch module on startup then call the
            // create_app_object() function and assign the resulting handle
            // back to the application component.
            py.importModule("checkbox_touch", function() {
                call("checkbox_touch.create_app_object", [], function(handle) {
                    app.handle = handle;
                });
            });
        }
        onError: {
            console.error("python error: " + traceback);
            ErrorLogic.showError(mainView, "python error: " + traceback, Qt.quit);
        }
        onReceived: console.log("pyotherside.send: " + data)
    }

    // Component representing our application
    CheckboxTouchApplication {
        id: app
        py: py
        onAppReady: {
            console.log("Plainbox version " + plainboxVersion);
            console.log("Checkbox Touch version " + applicationVersion);
            resumeOrStartSession();
        }
        onSessionReady: {
            welcomePage.enableButton()
        }
    }

    PageStack {
        id: pageStack
        Component.onCompleted: push(welcomePage)
    }

    WelcomePage {
        id: welcomePage
        welcomeText: i18n.tr("Welcome to Checkbox Touch\nVersion: " + appSettings.revision)
        onStartTestingTriggered: {
            if (appSettings.testplan != "") {
                app.rememberTestplan(appSettings.testplan, function() {
                    categorySelectionPage.setup();
                });
            } else {
                app.getTestplans(function(response) {
                    var tp_list = response.testplan_info_list;
                    if (tp_list.length < 2 && tp_list.length > 0) {
                        app.rememberTestplan(tp_list[0].mod_id, function() {
                            categorySelectionPage.setup();
                        });
                    }
                    else {
                        testplanSelectionPage.setup(tp_list)
                    }
                });
            }
            enableButton();
        }
        onAboutClicked: pageStack.push(aboutPage)
    }

    AboutPage {
        id: aboutPage
        visible: false
    }

    ResumeSessionPage {
        id: resumeSessionPage
        onRerunLast: app.resumeSession(true, processNextTest)
        onContinueSession: app.resumeSession(false, processNextTest)
        onRestartSession: {
            pageStack.clear();
            pageStack.push(welcomePage);
            app.startSession();
        }
    }

    SelectionPage {
        id: testplanSelectionPage
        title: i18n.tr("Testplan Selection")
        onlyOneAllowed: true
        function setup(testplan_info_list) {
            if (testplan_info_list.length<1) {
                ErrorLogic.showError(mainView, "Test plan missing", Qt.quit);
            }

            model.clear();
            for (var i=0; i<testplan_info_list.length; i++) {
                var testplan_info = testplan_info_list[i];
                model.append(testplan_info);
            }
            modelUpdated();
            pageStack.push(testplanSelectionPage);
        }
        onSelectionDone: {
            app.rememberTestplan(selected_id_list[0], function(response) {
                unlatchContinue();
                categorySelectionPage.setup();
            });
        }
    }

    SelectionPage {
        id: categorySelectionPage
        title: i18n.tr("Suite Selection")

        function setup() {
            app.getCategories(function(response) {
                var category_info_list = response.category_info_list;
                model.clear();
                for (var i=0; i<category_info_list.length; i++) {
                    var category_info = category_info_list[i]; 
                    model.append(category_info);
                }
                modelUpdated();
                pageStack.push(categorySelectionPage);
            });
        }

        onSelectionDone: {
            app.rememberCategorySelection(selected_id_list, function(response) {
                unlatchContinue();
                testSelectionPage.setup();
            });
        }

    }

    SelectionPage {
        id: testSelectionPage
        title: i18n.tr("Test selection")
        continueText: i18n.tr("Start Testing")
        
        function setup(selected_category_list) {
            app.getTests(function(response) {
                model.clear();
                var test_info_list = response.test_info_list;
                for (var i=0; i<test_info_list.length; i++) {
                    model.append(test_info_list[i]);
                }
                modelUpdated();
                pageStack.push(testSelectionPage);
            });
        }
        
        onSelectionDone: {
            app.rememberTestSelection(selected_id_list, function() {
                processNextTest();
            });
        }
    }
    function resumeOrStartSession() {
        app.isSessionResumable(function(result) {
            if(result.resumable === true) {
                pageStack.push(resumeSessionPage);
            } else {
                app.startSession();
            }
        });
    }

    function processNextTest() {
        app.getNextTest(function(test) {
            if (test.plugin === undefined) { 
                return showResultsScreen();
            }
            switch (test['plugin']) {
                case 'manual':
                    performManualTest(test);
                    break;
                case 'user-interact-verify':
                    performUserInteractVerifyTest(test);
                    break;
                case 'shell':
                    performAutomatedTest(test);
                    break;
                case 'user-verify':
                    performUserVerifyTest(test);
                    break;
                case 'user-interact':
                    performUserInteractTest(test);
                    break;
                default:
                    test.outcome = "skip";
                    completeTest(test);
            }
        });
    }

    function completeTest(test) {
        pageStack.clear();
        app.registerTestResult(test, processNextTest);
    }

    function showResultsScreen() {
        app.getResults(function(results) {
            var resultsPage = Qt.createComponent(Qt.resolvedUrl("components/ResultsPage.qml")).createObject();
            resultsPage.results = results;
            resultsPage.endTesting.connect(function() {
                pageStack.clear();
                app.clearSession(function() {
                    app.startSession();
                    pageStack.push(welcomePage);
                });
            });
            resultsPage.saveReportClicked.connect(function() {
                app.exportResults('html', [], function(uri) {
                    console.log(uri)
                });
                app.exportResults('xlsx', ["with-sys-info", "with-summary", "with-job-description", "with-text-attachments"], function(uri) {
                    console.log(uri)
                });
            });
            pageStack.push(resultsPage);
        });
    }

    function performAutomatedTest(test) {
        var automatedTestPage = Qt.createComponent(Qt.resolvedUrl("components/AutomatedTestPage.qml")).createObject();
        automatedTestPage.test = test;
        pageStack.push(automatedTestPage);
        app.runTestActivity(test, completeTest);
    }

    function performManualTest(test) {
        var manualIntroPage = Qt.createComponent(Qt.resolvedUrl("components/ManualIntroPage.qml")).createObject();
        manualIntroPage.test = test
        manualIntroPage.testDone.connect(completeTest);
        manualIntroPage.continueClicked.connect(function() { showVerificationScreen(test); });
        pageStack.push(manualIntroPage);
    }

    function performUserInteractVerifyTest(test) {
        var InteractIntroPage = Qt.createComponent(Qt.resolvedUrl("components/InteractIntroPage.qml")).createObject();
        InteractIntroPage.test = test;
        InteractIntroPage.testStarted.connect(function() {
            app.runTestActivity(test, function(test) {
                InteractIntroPage.stopActivity();
                showVerificationScreen(test);
            });
        });
        InteractIntroPage.testDone.connect(completeTest);
        pageStack.push(InteractIntroPage);
    }

    function performUserInteractTest(test) {
        var InteractIntroPage = Qt.createComponent(Qt.resolvedUrl("components/InteractIntroPage.qml")).createObject();
        InteractIntroPage.test = test;
        InteractIntroPage.testStarted.connect(function() {
            app.runTestActivity(test, function(test) {
                InteractIntroPage.stopActivity();
                var userInteractSummaryPage = Qt.createComponent(Qt.resolvedUrl("components/UserInteractSummaryPage.qml")).createObject();
                userInteractSummaryPage.test = test;
                userInteractSummaryPage.testDone.connect(completeTest);
                pageStack.push(userInteractSummaryPage);
            });
        });
        InteractIntroPage.testDone.connect(completeTest);
        pageStack.push(InteractIntroPage);
    }

    function performUserVerifyTest(test) {
        var InteractIntroPage = Qt.createComponent(Qt.resolvedUrl("components/InteractIntroPage.qml")).createObject();
        InteractIntroPage.test = test;
        InteractIntroPage.testDone.connect(completeTest);
        InteractIntroPage.testStarted.connect(function() {
            app.runTestActivity(test, function(test) { showVerificationScreen(test); } );
        });
        pageStack.push(InteractIntroPage);
    }

    function showVerificationScreen(test) {
        var verificationPage = Qt.createComponent(Qt.resolvedUrl("components/TestVerificationPage.qml")).createObject();
        verificationPage.test = test
        verificationPage.testDone.connect(completeTest);
        pageStack.push(verificationPage);
    }

}
