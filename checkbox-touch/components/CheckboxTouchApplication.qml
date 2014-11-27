/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
 *
 * Authors:
 * - Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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
import "ErrorLogic.js" as ErrorLogic


PythonObjectHandle {
    id: app
    // Version of the application
    property string applicationVersion
    // Version of the plainbox library
    property string plainboxVersion

    // Signal sent when the application becomes ready
    signal appReady();

    // Signal sent when a session becomes ready
    signal sessionReady();

    // Create a new session
    //
    // Starts session in plainbox and runs all necessary setup actions.
    // Calling this function will signal sessionReady() once it's finished
    // doing setup.
    function startSession() {
        request("start_session", [], function(result) {
            sessionReady();
        }, function(error) {
            console.error("Unable to start session: " + error);
        });
    }
    function resumeSession(rerunLastTest, continuation) {
        request("resume_session", [rerunLastTest], function(result) {
            if (!result["session_id"]) {
                pageStack.pop();
                ErrorLogic.showError(mainView,
                                     i18n.tr("Could not resume session ") + app.sessionId,
                                     function() {
                                         startSession();
                                         return;
                                     },
                                     i18n.tr("Start new session"));
            } else {
                sessionReady();
                continuation();
            }

        }, function(error) {
            console.error("Unable to resume session: " + error);
        });
    }
    function clearSession(continuation) {
        request("clear_session", [], continuation, function(error) {
            console.error("Unable to clear session: " + error);
        });
    }

    function isSessionResumable(continuation) {
        request("is_session_resumable", [], continuation, function(error) {
            console.error("Unable to check session resumability");
        });
    }

    function getTestplans(continuation) {
        request("get_testplans", [], continuation, function(error) {
            console.error("Unable to get testplans");
        });
    }
    function rememberTestplan(testplan, continuation) {
        request("remember_testplan", [testplan], continuation, function(error) {
            console.error("Unable to save testplan selection");
        });
    }

    function getCategories(continuation) {
        request("get_categories", [], continuation, function(error) {
            console.error("Unable to get categories");
        });
    }

    function rememberCategorySelection(categories, continuation) {
        request("remember_categories", [categories], continuation, function(error) {
            console.error("Unable to save category selection");
        });
    }

    function getTests(continuation) {
        request("get_available_tests", [], continuation, function(error) {
            console.error("Unable to get tests");
        });
    }

    function rememberTestSelection(tests, continuation) {
        request("remember_tests", [tests], continuation, function(error) {
            console.error("Unable to save test selection");
        });
    }

    function getNextTest(continuation) {
        request("get_next_test", [], continuation, function(error) {
            console.error("Unable to get next test");
        });
    }

    function registerTestResult(test, continuation) {
        request("register_test_result", [test], continuation, function(error) {
            console.error("Unable to save test result");
        });
    }

    function runTestActivity(test, continuation) {
        request("run_test_activity", [test], continuation, function(error) {
            console.error("Unable to run test activity");
        });
    }

    function getResults(continuation) {
        request("get_results", [], continuation, function(error) {
            console.error("Unable to get test results");
        });
    }

    function exportResults(output_format, option_list, continuation) {
        request("export_results", [output_format, option_list], continuation, function(error) {
            console.error("Unable to export test results");
        });
    }

    // A wrapper around invoke() that works with the @view decorator. The fn_ok
    // and fn_err are called on a normal reply and on error, respectively.
    function request(name, args, fn_ok, fn_err) {
        invoke(name, args, function(response) {
            if (response.code == 200) {
                fn_ok(response.result);
            } else {
                fn_err(response.error);
            }
        });
    }

    // Internal handler that triggers a call to python to query for runtime and
    // application versions.
    onHandleReady: {
        request("get_version_pair", [], function(result) {
            app.applicationVersion = result.application_version;
            app.plainboxVersion = result.plainbox_version;
            appReady();
        }, function(error) {
            console.error("Unable to query for version: " + error);
        });
    }
}
