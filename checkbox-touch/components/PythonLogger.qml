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

/*! \brief Python-driven logger
    \inherits PythonObjectRef

    This component uses pyotherside to forward logging events to python.
    It monkey-patches console.log and console.error to capture their calls
    and forward those calls to python logger.
*/
import QtQuick 2.0

PythonObjectRef {
    id: pythonLogger

    function debug(msg) {
        invoke('debug', [msg], function() {});
    }

    function info(msg) {
       invoke('info', [msg], function() {});
    }

    function warning(msg) {
        invoke('warning', [msg], function() {});
    }

    function error(msg) {
        invoke('error', [msg + "\nStacktrace:\n" + getStackTrace()], function() {});
    }

    function critical(msg) {
        invoke('critical', [msg + "\nStacktrace:\n" + getStackTrace()], function() {});
    }
    /** get string containing pretty-formatted stack trace */
    function getStackTrace() {
        var stackTrace = "";
        var callers = ((new Error).stack).split("\n");
        callers.shift(); // remove current frame from ST (getStackTrace)
        callers.shift(); // remove logging method frame from ST
        for (var lvl in callers) {
            stackTrace += "#" + lvl + " " + callers[lvl] + "\n";
        }
        return stackTrace;
    }

    /** Overridden invoke that doesn't log invoke calls */
    function invoke(func, args, callback) {
        if (py !== null && object !== null) {
            var callable = py.getattr(object, func);
            if (!callable) {
                console.error("Unable to invoke " + func + " on python logger");
                throw "trying to invoke not existing method"
            }
            py.call(callable, args, function(response) {
                callback(response);
            });
        } else {
            _original_console_error("unable to invoke " + func + " on python logger");
            throw "invoke called without py initiated and/or object constructed";
        }
    }

    Component.onCompleted: {
        /* save original logging facilities */
        _original_console_log = console.log;
        _original_console_error = console.error;
    }

    onObjectReady: {
        /* monkey-patch console.log and console.error */
        console.log = function() { info(_argsToString(arguments)); };
        console.error = function() { error(_argsToString(arguments)); };
        debug("Python logger ready");
    }

    /** get string containing unpacked values from arguments object separated by spaces*/
    function _argsToString(argsObj) {
        var args = [];
        for(var i = 0; i < argsObj.length; i++) args.push(argsObj[i]);
        return args.join(" ");
    }

    property var _original_console_log
    property var _original_console_error
}
