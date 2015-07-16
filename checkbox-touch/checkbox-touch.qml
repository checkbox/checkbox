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
import Ubuntu.Components.Popups 0.1
import QtQuick.Layouts 1.1
import io.thp.pyotherside 1.4
import "components"
import "components/ErrorLogic.js" as ErrorLogic
import "components/CbtDialogLogic.js" as CbtDialogLogic


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
        "testplan": "",
        "providersDir": "providers"
    }

    Arguments {
        id: args
        Argument {
            name: "autopilot"
            help: i18n.tr("Run Checkbox-Touch in autopilot-testing mode")
            required: false
        }
        Argument {
            name: "quiet"
            help: i18n.tr("Write only warnings and errors to standard error")
            required: false
        }
        Argument {
            name: "settings"
            valueNames: "PATH_TO_SETTINGS"
            help: i18n.tr("Path to a file containing checkbox-touch settings")
            required: true
        }
    }

    Component.onCompleted: {
        if (args.values["autopilot"]) {
            // autopilot-testing mode
            appSettings["testplan"] = "2015.com.canonical.certification::checkbox-touch-autopilot";
            appSettings["providersDir"] = "tests/autopilot/autopilot-provider";
            appSettings["log-level"] = "warning";
        } else {
            // normal execution - load settings.json file
            var xhr = new XMLHttpRequest;
            xhr.open("GET", args.values["settings"]);
            xhr.onreadystatechange = function() {
                if (xhr.readyState == XMLHttpRequest.DONE) {
                    try {
                        var newAppSettings = JSON.parse(xhr.responseText);
                    } catch (x) {
                        // if we cannot parse settings.json, we should leave
                        // deafult values of appSettings
                        console.error("Could not parse settings.json. Using default values");
                    }
                    // overwrite/add appSettings' attributes that got loaded
                    for (var attr in newAppSettings) {
                        appSettings[attr] = newAppSettings[attr];
                    }
                }
            }
            xhr.send();
        }
        if (args.values["quiet"]) {
            // monkey-patch console.log and console.info to do nothing
            console.log = function() {};
            console.info = function() {};
            appSettings["log-level"] = "warning";
        }
        py.init()
    }


    // Pyotherside python object that we use to talk to all of plainbox
    Python {
        id: py

        function init() {
            console.log("Pyotherside version " + pluginVersion());
            console.log("Python version " + pythonVersion());
            // A bit hacky but that's where the python code is
            addImportPath(Qt.resolvedUrl('py/'));
            // Import path for plainbox and potentially other python libraries
            addImportPath(Qt.resolvedUrl('lib/py'))
            setHandler('command_output', commandOutputPage.addText);
            initiated();
        }

        // gets triggered when python object is ready to be used
        signal initiated

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
            aboutPage.versionInfo = {
                "checkbox_touch" : applicationVersion,
                "plainbox" : plainboxVersion
            };
            resumeOrStartSession(appSettings["providersDir"]);
        }
        onSessionReady: {
            welcomePage.enableButton()
        }
        Component.onCompleted: {
            // register to py.initiated signal
            py.onInitiated.connect(function() {
                construct("checkbox_touch.create_app_object", []);
            });
        }
    }

    PythonLogger {
        id: logger
        py: py
        Component.onCompleted: {
            // register to py.initiated signal
            py.onInitiated.connect(function() {
                py.importModule("checkbox_touch", function() {
                    construct("checkbox_touch.get_qml_logger",
                             [appSettings["log-level"] || "info"]);
                });
            });
        }
    }

    PageStack {
        id: pageStack
        Component.onCompleted: push(welcomePage)
    }

    WelcomePage {
        id: welcomePage
        welcomeText: i18n.tr("Welcome to Checkbox Touch\nVersion: %1\n(%2 %3)")
            .arg(app.applicationVersion).arg(appSettings.revision).arg(appSettings.clickBuildDate)
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

    Item {
        id: progressHeader
        visible: false
        property alias progressText: _progressText.text
        property alias value: _progressBar.value
        property alias maximumValue: _progressBar.maximumValue
        ColumnLayout{
            anchors {
                fill: parent
                verticalCenter: parent.verticalCenter
                bottomMargin: units.gu(1.5)
                rightMargin: units.gu(1)
                // leftMargin should compensate for potential 'back' action that might appear on next page
                // so the whole progressHeader stays in the same spot on the screen throughout the session
                leftMargin:  pageStack.depth == 1 ? units.gu(5) : units.gu(1)

            }
            Label {
                text: pageStack.currentPage ? pageStack.currentPage.title : ""
                fontSize: "x-large"
                font.weight: Font.Light
                anchors.verticalCenter: parent.verticalCenter
            }
            Label {
                id: _progressText
                fontSize: "x-small"
                font.weight: Font.Light
                anchors.right: parent.right
                anchors.bottom: parent.bottom
            }
            ProgressBox {
                id: _progressBar
                value: 0
                maximumValue: 1
                implicitWidth: parent.width
            }
        }

        function update(test) {
            progressHeader.visible = true;
            progressHeader.progressText = Number(test.test_number / test.tests_count * 100.0).toFixed(0) + "% ("+test.test_number + "/" + test.tests_count + ")";
            progressHeader.value = test.test_number
            progressHeader.maximumValue = test.tests_count
        }
    }

    ResumeSessionPage {
        id: resumeSessionPage
        onRerunLast: app.resumeSession(true, appSettings["providersDir"], processNextTest)
        onContinueSession: app.resumeSession(false, appSettings["providersDir"], processNextTest)
        resumeText: i18n.tr("Checkbox did not finish completely.\nDo you want \
 to rerun last test, continue to the next test, or restart from the beginning?")
        onRestartSession: {
            pageStack.clear();
            pageStack.push(welcomePage);
            app.startSession(appSettings["providersDir"]);
        }
    }

    SelectionPage {
        id: testplanSelectionPage
        title: i18n.tr("Select test plan")
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
                categorySelectionPage.setup(unlatchContinue);
            });
        }
    }

    SelectionPage {
        id: categorySelectionPage
        objectName: "categorySelectionPage"
        title: i18n.tr("Select categories")

        function setup(continuation) {
            app.getCategories(function(response) {
                var category_info_list = response.category_info_list;
                model.clear();
                for (var i=0; i<category_info_list.length; i++) {
                    var category_info = category_info_list[i]; 
                    model.append(category_info);
                }
                modelUpdated();
                pageStack.push(categorySelectionPage);
                // if called from welcome page, no continuation is given
                if (continuation) continuation();
            });
        }

        onSelectionDone: {
            app.rememberCategorySelection(selected_id_list, function(response) {
                testSelectionPage.setup(unlatchContinue);
            });
        }

    }

    SelectionPage {
        id: testSelectionPage
        objectName: "testSelectionPage"
        title: i18n.tr("Select tests")
        continueText: i18n.tr("Start Testing")
        
        function setup(continuation) {
            app.getTests(function(response) {
                model.clear();
                var test_info_list = response.test_info_list;
                for (var i=0; i<test_info_list.length; i++) {
                    model.append(test_info_list[i]);
                }
                modelUpdated();
                pageStack.push(testSelectionPage);
                continuation();
            });
        }
        
        onSelectionDone: {
            app.rememberTestSelection(selected_id_list, function() {
                processNextTest();
                unlatchContinue();
            });
        }
    }

    PasswordDialog {
        id: passwordDialog
    }

    CommandOutputPage {
        id: commandOutputPage
        visible: false
        __customHeaderContents: progressHeader;
    }

    function resumeOrStartSession() {
        app.isSessionResumable(function(result) {
            if(result.resumable === true) {
                pageStack.clear();
                pageStack.push(resumeSessionPage);
            } else {
                if (result.errors_encountered) {
                    ErrorLogic.showError(mainView, i18n.tr("Could not resume session."),
                                         app.startSession(appSettings["providersDir"]),
                                         i18n.tr("Start new session"));
                } else {
                    app.startSession(appSettings["providersDir"]);
                }
            }
        });
    }

    function processNextTest() {
        app.getNextTest(function(test) {
            pageStack.clear();
            if (test.plugin === undefined) { 
                return showResultsScreen();
            }
            if (test.user) {
                // running this test will require to be run as a different
                // user (therefore requiring user to enter sudo password)
                if (!appSettings.sudoPasswordProvided) {
                    // ask user for password
                    passwordDialog.passwordEntered.connect(function(pass) {
                        app.rememberPassword(pass, function(){
                            appSettings.sudoPasswordProvided = true;
                            performTest(test);
                        });
                    });
                    passwordDialog.dialogCancelled.connect(function() {
                        test.outcome = "skip";
                        completeTest(test);
                    });
                    PopupUtils.open(passwordDialog.dialogComponent);
                    return;
                }
            }
            performTest(test);
        });
    }

    function performTest(test) {
        switch (test['plugin']) {
            case 'manual':
                performManualTest(test);
                break;
            case 'user-interact-verify':
                performUserInteractVerifyTest(test);
                break;
            case 'shell':
            case 'resource':
                performAutomatedTest(test);
                break;
            case 'user-verify':
                performUserVerifyTest(test);
                break;
            case 'user-interact':
                performUserInteractTest(test);
                break;
            case 'qml':
                performQmlTest(test);
                break;
            default:
                test.outcome = "skip";
                completeTest(test);
        }
    }

    function completeTest(test) {
        app.registerTestResult(test, processNextTest);
    }

    function runTestActivity(test, continuation) {
        commandOutputPage.clear();
        app.runTestActivity(test, continuation);

    }

    function showResultsScreen() {
        pageStack.clear();
        app.getResults(function(results) {
            var resultsPage = Qt.createComponent(Qt.resolvedUrl("components/ResultsPage.qml")).createObject();
            resultsPage.results = results;
            resultsPage.endTesting.connect(function() {
                pageStack.clear();
                app.clearSession(function() {
                    app.startSession(appSettings["providersDir"]);
                    pageStack.push(welcomePage);
                });
            });
            resultsPage.saveReportClicked.connect(function() {
                app.exportResults('2013.com.canonical.plainbox::html', [], function(uri) {
                    console.log(uri)
                    var htmlReportUrl = uri;
                    app.exportResults('2013.com.canonical.plainbox::xlsx', ["with-sys-info", "with-summary", "with-job-description", "with-text-attachments", "with-unit-categories"], function(uri) {
                        console.log(uri)
                        CbtDialogLogic.showDialog(resultsPage, i18n.tr("Reports have been saved to your Documents folder"),
                                                  [{ "text": i18n.tr("OK"), "color": UbuntuColors.green}, {"text": i18n.tr("View Report"), "color": UbuntuColors.green, "onClicked": function(uri) {
                                                      var webviewer = Qt.createComponent(Qt.resolvedUrl("components/WebViewer.qml")).createObject();
                                                      webviewer.uri = htmlReportUrl;
                                                      pageStack.push(webviewer);
                                                  }}]);
                    });
                });
            });
            pageStack.push(resultsPage);
        });
    }

    function performAutomatedTest(test) {
        var automatedTestPage = Qt.createComponent(Qt.resolvedUrl("components/AutomatedTestPage.qml")).createObject();
        automatedTestPage.test = test;
        automatedTestPage.__customHeaderContents = progressHeader;
        progressHeader.update(test);
        pageStack.push(automatedTestPage);
        runTestActivity(test, completeTest);
    }

    function performManualTest(test) {
        var manualIntroPage = Qt.createComponent(Qt.resolvedUrl("components/ManualIntroPage.qml")).createObject();
        manualIntroPage.test = test
        manualIntroPage.testDone.connect(completeTest);
        manualIntroPage.continueClicked.connect(function() { showVerificationScreen(test); });
        manualIntroPage.__customHeaderContents = progressHeader;
        progressHeader.update(test);
        pageStack.push(manualIntroPage);
    }

    function performUserInteractVerifyTest(test) {
        var InteractIntroPage = Qt.createComponent(Qt.resolvedUrl("components/InteractIntroPage.qml")).createObject();
        InteractIntroPage.test = test;
        InteractIntroPage.testStarted.connect(function() {
            runTestActivity(test, function(test) {
                InteractIntroPage.stopActivity();
                showVerificationScreen(test);
            });
        });
        InteractIntroPage.testDone.connect(completeTest);
        InteractIntroPage.__customHeaderContents = progressHeader;
        progressHeader.update(test);
        pageStack.push(InteractIntroPage);
    }

    function performUserInteractTest(test) {
        var InteractIntroPage = Qt.createComponent(Qt.resolvedUrl("components/InteractIntroPage.qml")).createObject();
        InteractIntroPage.test = test;
        InteractIntroPage.testStarted.connect(function() {
            runTestActivity(test, function(test) {
                InteractIntroPage.stopActivity();
                var userInteractSummaryPage = Qt.createComponent(Qt.resolvedUrl("components/UserInteractSummaryPage.qml")).createObject();
                userInteractSummaryPage.test = test;
                userInteractSummaryPage.testDone.connect(completeTest);
                userInteractSummaryPage.__customHeaderContents = progressHeader;
                progressHeader.update(test);
                pageStack.push(userInteractSummaryPage);
            });
        });
        InteractIntroPage.testDone.connect(completeTest);
        InteractIntroPage.__customHeaderContents = progressHeader;
        progressHeader.update(test);
        pageStack.push(InteractIntroPage);
    }

    function performUserVerifyTest(test) {
        var InteractIntroPage = Qt.createComponent(Qt.resolvedUrl("components/InteractIntroPage.qml")).createObject();
        InteractIntroPage.test = test;
        InteractIntroPage.testDone.connect(completeTest);
        InteractIntroPage.testStarted.connect(function() {
            runTestActivity(test, function(test) { showVerificationScreen(test); } );
        });
        InteractIntroPage.__customHeaderContents = progressHeader;
        progressHeader.update(test);
        pageStack.push(InteractIntroPage);
    }

    function performQmlTest(test) {
        var comp = Qt.createComponent(Qt.resolvedUrl("components/QmlNativePage.qml"))
        console.log(comp.errorString());
        var qmlNativePage = comp.createObject();
        qmlNativePage.test = test
        qmlNativePage.testDone.connect(completeTest);
        qmlNativePage.__customHeaderContents = progressHeader;
        progressHeader.update(test);
        pageStack.push(qmlNativePage);
    }

    function showVerificationScreen(test) {
        var verificationPage = Qt.createComponent(Qt.resolvedUrl("components/TestVerificationPage.qml")).createObject();
        verificationPage.test = test
        verificationPage.testDone.connect(completeTest);
        verificationPage.__customHeaderContents = progressHeader;
        progressHeader.update(test);
        pageStack.push(verificationPage);
    }

}
