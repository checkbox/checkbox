/*
 * This file is part of Checkbox
 *
 * Copyright 2014-2015 Canonical Ltd.
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
import "ErrorLogic.js" as ErrorLogic


PythonObjectRef {
    id: app
    // Version of the application
    property string applicationVersion
    // Version of the plainbox library
    property string plainboxVersion
    // path to session storage directory
    property string sessionDir

    // Signal sent when the application becomes ready
    signal appReady();

    // Signal sent when a session becomes ready
    signal sessionReady()

    // Create a new session
    //
    // Starts session in plainbox and runs all necessary setup actions.
    // Calling this function will signal sessionReady() once it's finished
    // doing setup.
    function startSession() {
        request("start_session", [], function(result) {
            sessionDir = result['session_dir'];
            sessionReady();
        }, function(error) {
            console.error("Unable to start session: " + error);
            ErrorLogic.showError(mainView,
                                 i18n.tr("Could not start a session. Reason:\n" + error),
                                 Qt.quit,
                                 i18n.tr("Quit"));
        });
    }
    function resumeSession(rerunLastTest, continuation) {
        request("resume_session", [rerunLastTest], function(result) {
            if (!result["session_id"]) {
                pageStack.pop();
                ErrorLogic.showError(mainView,
                                     i18n.tr("Could not resume session"),
                                     function() {
                                         startSession();
                                         return;
                                     },
                                     i18n.tr("Start new session"));
            } else {
                sessionDir = result['session_dir'];
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
        var handleResult = function(result) {
            sessionDir = result['session_dir'];
            continuation();
        }
        request("remember_testplan", [testplan], handleResult, function(error) {
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

    function getRerunCandidates(continuation) {
        request("get_rerun_candidates", [], continuation, function(error) {
            console.error("Unable to get rerun candidates");
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
    function exportResultsWithLauncherSettings(continuation) {
        request("export_results_with_launcher_settings", [], continuation, function(error) {
            console.error("Unable to export test results");
        });
    }
    function getCertificationTransportConfig(continuation) {
        request("get_certification_transport_config", [], continuation, function(error) {
            console.error("Unable to check launcher reports");
        });
    }
    function submitResults(config, continuation, continuation_error) {
        // Use low-level call as the config may contain sensitive information.
        var callable = py.getattr(object, "submit_results");
        if (!callable) {
            console.error("Unable to invoke submit_results!");
            throw "trying to invoke not existing method";
        }
        py.call(callable, [config], function(response) {
            if (response.code == 200) {
                continuation(response.result);
            } else {
                continuation_error(response.error)
            }
        });
    }
    function dropPermissions(appId, services, continuation, continuation_error) {
        request("drop_permissions", [appId, services], continuation, function(error) {
            console.error("Unable to remove permissions");
            if (continuation_error) continuation_error(error);
        });
    }
    function getIncompleteSessions(continuation) {
        request("get_incomplete_sessions", [], continuation, function(error) {
            console.error("Unable to get incomplete sessions")
        });
    }
    function deleteOldSessions(sessionIds, continuation) {
        request("delete_old_sessions", [sessionIds], continuation, function(error) {
            console.error("Unable to remove old sessions")
        });
    }

    function rememberPassword(password, continuation) {
        // using low-level py.call() to 'silently' pass password string through pyotherside
        var callable = py.getattr(object, "remember_password");
        if (!callable) {
            console.error("Unable to invoke remember_password!");
            throw "trying to invoke not existing method";
        }
        py.call(callable, [password], function(response) {
            continuation(response);
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
    onObjectReady: {
        request("load_providers", [appSettings["providersDir"]], function(result) {
            request("get_version_pair", [], function(result) {
                app.applicationVersion = result.application_version;
                app.plainboxVersion = result.plainbox_version;
                appReady();
            }, function(error) {
                console.error("Unable to query for version: " + error);
            });

        }, function(error) {
                console.error("Unable to load providers: " + error);
                ErrorLogic.showError(mainView, i18n.tr("No providers available!"), Qt.quit);
        });
    }
}
