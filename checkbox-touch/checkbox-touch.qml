/*
 * This file is part of Checkbox
 *
 * Copyright 2014, 2015 Canonical Ltd.
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
        "providersDir": "providers",
        "submission": null
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
        i18n.domain = "com.ubuntu.checkbox";
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
            resumeOrStartSession();
        }
        onSessionReady: {
            welcomePage.enableButton()
        }
        Component.onCompleted: {
            // register to py.initiated signal
            py.onInitiated.connect(function() {
                construct("checkbox_touch.create_app_object", [
                    appSettings["providersDir"]]);
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
        // TRANSLATORS: %1 means program version, %2 repository revision and %3
        // date when the package was built
        // TRANSLATORS: keep the '\n' characters at the end of each line
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
        onRerunLast: app.resumeSession(true, processNextTest)
        onContinueSession: app.resumeSession(false, processNextTest)
        resumeText: i18n.tr("Previous session did not finish completely.\nDo you want \
 to rerun last test, continue to the next test, or start a new session?")
        onRestartSession: {
            pageStack.clear();
            pageStack.push(welcomePage);
            app.startSession();
        }
    }

    SelectionPage {
        id: testplanSelectionPage
        title: i18n.tr("Select test plan")
        onlyOneAllowed: true
        largeBuffer: args.values["autopilot"]

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
        largeBuffer: args.values["autopilot"]

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
        continueText: i18n.tr("Start testing")
        largeBuffer: args.values["autopilot"]

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

    SelectionPage {
        id: rerunSelectionPage
        objectName: "rerunSelectionPage"
        title: i18n.tr("Select tests to re-run")
        continueText: state == "empty selection" ?
            i18n.tr("Finish") : i18n.tr("Re-run")
        emptyAllowed: true
        largeBuffer: args.values["autopilot"]

        function setup(rerunCandidates, continuation) {
            model.clear();
            for (var i=0; i<rerunCandidates.length; i++) {
                model.append(rerunCandidates[i]);
            }
            modelUpdated();
            pageStack.push(rerunSelectionPage)
        }
        onSelectionDone: {
            app.rememberTestSelection(selected_id_list, function() {
                processNextTest();
                unlatchContinue();
            });
        }
    }
    CommentsDialog {
        id: commentsDialog
    }

    PasswordDialog {
        id: passwordDialog
    }

    CommandOutputPage {
        id: commandOutputPage
        visible: false
        __customHeaderContents: progressHeader;
    }
    /*
     * Create a page from a Component defined in `url` with a common
     * progress header if `test` is supplied.
     * If Component definition has errors, display a proper popup.
     */
    function createPage(url, test) {
        var pageComponent = Qt.createComponent(Qt.resolvedUrl(url));
        if (pageComponent.status == Component.Error) {
            var msg = i18n.tr("Could not create component '") + url + "'\n" + pageComponent.errorString();
            console.error(msg);
            ErrorLogic.showError(mainView, msg, Qt.quit, i18n.tr("Quit"));
        } else {
            var pageObject = pageComponent.createObject();
            if (test) {
                pageObject.test = test;
                pageObject.__customHeaderContents = progressHeader;
                progressHeader.update(test)
            }
            return pageObject;
        }
    }

    function resumeOrStartSession() {
        app.isSessionResumable(function(result) {
            if(result.resumable === true) {
                pageStack.clear();
                pageStack.push(resumeSessionPage);
            } else {
                if (result.errors_encountered) {
                    ErrorLogic.showError(mainView, i18n.tr("Could not resume session."),
                                         app.startSession(),
                                         i18n.tr("Start new session"));
                } else {
                    app.startSession();
                }
            }
        });
    }

    function processNextTest() {
        app.getNextTest(function(test) {
            pageStack.clear();
            if (test.plugin === undefined) { 
                return maybeShowRerunScreen();
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
            case 'local':
            case 'shell':
            case 'attachment':
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
                if (test.flags.indexOf("confined") > -1)
                    performConfinedQmlTest(test);
                else
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
    function maybeShowRerunScreen() {
        app.getRerunCandidates(function(result) {
            if (result == false) {
                 showResultsScreen();
                 return;
            }
            rerunSelectionPage.setup(result);
        });
    }

    function showResultsScreen() {
        pageStack.clear();
        app.getResults(function(results) {
            var resultsPage = createPage("components/ResultsPage.qml");
            resultsPage.results = results;
            if (appSettings["submission"]) {
                resultsPage.submissionName = appSettings["submission"].name;
            }
            resultsPage.endTesting.connect(function() {
                pageStack.clear();
                app.clearSession(function() {
                    app.startSession();
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
                                                  [{ "text": i18n.tr("OK"), "color": UbuntuColors.green}, {"text": i18n.tr("View report"), "color": UbuntuColors.green, "onClicked": function(uri) {
                                                      var webviewer = Qt.createComponent(Qt.resolvedUrl("components/WebViewer.qml")).createObject();
                                                      webviewer.uri = htmlReportUrl;
                                                      pageStack.push(webviewer);
                                                  }}]);
                    });
                });
            });
            resultsPage.submitReportClicked.connect(function() {
                getSubmissionInput(function() {
                    app.submitResults(appSettings["submission"], function(reply) {
                        // pretty-stringify reply
                        var s = ""
                        for (var i in reply) {
                            s += i + ': ' + reply[i] + '\n';
                        }
                        CbtDialogLogic.showDialog(
                            resultsPage,
                            i18n.tr("Report has been submited.\n" + s),
                            [{"text": i18n.tr("OK"), "color": UbuntuColors.green}]);
                    },
                    function(error) {
                        ErrorLogic.showError(mainView,
                                             i18n.tr("Could not submit report. Reason:\n" + error),
                                             function(){},
                                             i18n.tr("OK"));
                        resultsPage.unlatchSubmission();
                    })
                },
                function() {
                    resultsPage.unlatchSubmission();
                });
            });
            pageStack.push(resultsPage);
        });
    }

    function performAutomatedTest(test) {
        var automatedTestPage = createPage("components/AutomatedTestPage.qml", test);
        pageStack.push(automatedTestPage);
        runTestActivity(test, completeTest);
    }

    function performManualTest(test) {
        runTestActivity(test, function(test) {
            var manualIntroPage = createPage("components/ManualIntroPage.qml", test);
            manualIntroPage.testDone.connect(completeTest);
            manualIntroPage.continueClicked.connect(function() { showVerificationScreen(test); });
            pageStack.push(manualIntroPage);
        });
    }

    function performUserInteractVerifyTest(test) {
        var InteractIntroPage = createPage("components/InteractIntroPage.qml", test);
        InteractIntroPage.testStarted.connect(function() {
            runTestActivity(test, function(test) {
                InteractIntroPage.stopActivity();
                showVerificationScreen(test);
            });
        });
        InteractIntroPage.testDone.connect(completeTest);
        pageStack.push(InteractIntroPage);
    }

    function performUserInteractTest(test) {
        var InteractIntroPage = createPage("components/InteractIntroPage.qml", test);
        InteractIntroPage.testStarted.connect(function() {
            runTestActivity(test, function(test) {
                InteractIntroPage.stopActivity();
                var userInteractSummaryPage = createPage("components/UserInteractSummaryPage.qml", test);
                userInteractSummaryPage.testDone.connect(completeTest);
                pageStack.push(userInteractSummaryPage);
            });
        });
        InteractIntroPage.testDone.connect(completeTest);
        pageStack.push(InteractIntroPage);
    }

    function performUserVerifyTest(test) {
        var InteractIntroPage = createPage("components/InteractIntroPage.qml", test);
        InteractIntroPage.testDone.connect(completeTest);
        InteractIntroPage.testStarted.connect(function() {
            runTestActivity(test, function(test) { showVerificationScreen(test); } );
        });
        pageStack.push(InteractIntroPage);
    }

    function performQmlTest(test) {
        runTestActivity(test, function(test) {
            var qmlNativePage = createPage("components/QmlNativePage.qml", test);
            qmlNativePage.testDone.connect(completeTest);
            pageStack.push(qmlNativePage);
        });
    }
    function performConfinedQmlTest(test) {
        runTestActivity(test, function(test) {
            var qmlNativePage = createPage("components/QmlConfinedPage.qml");
            qmlNativePage.applicationVersion = app.applicationVersion;
            qmlNativePage.testDone.connect(completeTest);
            pageStack.push(qmlNativePage);
        });
    }

    function showVerificationScreen(test) {
        var verificationPage = createPage("components/TestVerificationPage.qml", test);
        verificationPage.testDone.connect(completeTest);
        pageStack.push(verificationPage);
    }
    function getSubmissionInput(continuation, cancelContinuation) {
        if (appSettings.submission.inputForm) {
            var dlg_cmp = Qt.createComponent(Qt.resolvedUrl(appSettings.submission.inputForm));
            var dlg = dlg_cmp.createObject(mainView);

            dlg.cancelClicked.connect(function() {
                cancelContinuation();
                return;
            });

            dlg.submissionDetailsFilled.connect(function(submissionDetails) {
                for (var attr in submissionDetails) {
                    appSettings.submission[attr] = submissionDetails[attr];
                }
                continuation();
            });
            PopupUtils.open(dlg.dialogComponent);
            return; // inputForm gets precedence over input
        }

        if (!appSettings.submission.input) {
            // no input to process
            continuation();
            return;
        }
        var input_vars = appSettings.submission.input.slice(); //copy array

        // Because of the asynchronous nature of qml we cannot just launch
        // N number of popups each asking for one submission variable
        var process_input = function() {
            if (input_vars.length > 0) {
                var input = input_vars.shift();
                var dlg = Qt.createComponent(Qt.resolvedUrl("components/InputDialog.qml")).createObject(mainView);
                dlg.prompt = input.prompt;
                dlg.textEntered.connect(function(text) {
                    appSettings.submission[input.paramName] = text;
                    process_input();
                });
                dlg.cancelClicked.connect(function() {
                    cancelContinuation();
                    return;
                });
                PopupUtils.open(dlg.dialogComponent);
                return;
            }
            continuation();
        }
        process_input();
    }

}
