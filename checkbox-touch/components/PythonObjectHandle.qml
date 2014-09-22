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


QtObject {
    // Reference to pyotherside's Python object
    property var py: null
    // Handle to a python object (via RemoteObjectLifecycleManager)
    // if it is < 0 then it is an error of some kind
    // if it is 0 (default) then the handle is just invalid
    // if it is > 0 then it represents a valid object handle
    property int handle: 0
    // Flag set just prior to sending the handleReady() signal
    property bool _ready: false

    // Signal sent when the handle is initially assigned *and* py is already
    // assigned (so when the python object is ready to be interacted with)
    signal handleReady();

    // Dereference the python object when we are shutting down
    Component.onDestruction: _unref()
    // Maybe send the handleReady signal (once) when handle is changed
    onHandleChanged: _maybeReady()
    // Maybe send the handleReady signal (once) when 'py' is changed
    onPyChanged: _maybeReady()

    /** Send the handleReady() signal (once) if both py and handle are ready */
    function _maybeReady() {
        if (handle > 0 && py !== null && _ready == false) {
            _ready = true;
            handleReady()
        }
    }

    /** Dereference this object */
    function _unref() {
        if (py !== null && handle > 0) {
            console.log("py_unref: " + handle);
            py.call("py_unref", [handle]);
            handle = 0;
        }
    }

    /** Call a method on this object */
    function invoke(func, args, callback) {
        if (py !== null && handle > 0) {
            console.log("py_invoke(" + handle + ", " + func + ", " + args + ") ...");
            py.call("py_invoke", [handle, func, args], function(response) {
                console.log("py_invoke(" + handle + ", " + func + ", " + args + ") -> " + response);
                callback(response);
            });
        } else {
            console.error("unable to py_invoke: " + handle + ", " + func + ", " + args);
            throw "py_invoke called without ready py and handle";
        }
    }
}
