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
import QtQuick 2.0


QtObject {
    id: pythonObjectRef

    // Reference to pyotherside's Python object
    property var py: null

    // PyObjectRef to the object
    property var object: null

    // Signal sent when the object reference is ready to use
    signal objectReady()

    // Creation method name that were used to get the reference to the object
    property var creationMethodName: null

    function construct(creationMethodName, args) {
        if (!py) {
            console.error("Trying to get reference to python object without py initiated!");
        } else {
            console.info("Getting reference to python object via " + creationMethodName);
            py.call(creationMethodName, args, function(result) {
                if (!result) {
                    var msg = "Object construction failed. " + creationMethodName + " did not return a valid object";
                    console.error(msg);
                    throw msg;
                } else {
                    object = result;
                    pythonObjectRef.creationMethodName = creationMethodName;
                    objectReady();
                }
            });
        }
    }
    /** Call a method on this object */
    function invoke(func, args, callback) {
        if (py !== null && object !== null) {
            console.log("invoking " + func + " on object created with" + pythonObjectRef.creationMethodName + ", with args: " + JSON.stringify(args) + " ...");
            var callable = py.getattr(object, func);
            if (!callable) {
                console.log("Unable to invoke " + func + " on object " + JSON.stringify(pythonObjectRef));
                throw "trying to invoke inexistent method"
            }
            py.call(callable,  args, function(response) {
                console.log(func + " on object created with" + pythonObjectRef.creationMethodName + ", with args: " + JSON.stringify(args) + " returned: " + JSON.stringify(response));
                callback(response);
            });
        } else {
            console.error("Unable to invoke " + func + " on object " + JSON.stringify(pythonObjectRef));
            throw "invoke called without py initiated and/or object constructed";
        }
    }
}
