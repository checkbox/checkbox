/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Maciej Kisielewski <maciej.kisielewski@canonical.com>
 *
 * Checkbox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3,
 * as published by the Free Software Foundation.
 *
 * Checkbox is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
 */
import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Window 2.0

/*! \brief Generic Screen Test.
    \inherits Page

    This widget is a page drawing fields that user should click in order to
    satisfy test requiremets. Fields that have to be clicked appear in the same
    order as they were added using add* methods. The first field will appear
    once the runTest method is called.
*/

Page {
    id: screenTest

    anchors.fill: parent

    /*!
        Gets triggered when the last of queued targets receives fieldClicked.
     */
    signal allTargetsHit;

    /*!
        Gets triggered when user clicks or taps the screen three times in a
        quick succession (maximum of 400ms between taps/clicks).
        This signal might be used to display a menu of advanced test options.
     */
    signal tripleClicked;

    /*!
        Gets triggered when any of the fields (visible or not) are
        tapped/clicked/dragged onto.
        By default this signal is used by internal logic of the whole test.
        Connect to this signala if you need fine control over the test.
     */
    signal fieldClicked(var row, var col);

    /*!
        resolution sets the number of rows that the grid of fields should have.
        Number of columns is set automatically to produce fields of the shape
        as close to square as possible.
     */
    property var resolution: 20

    /*!
        call addTarget to add a new target to the queue of to-be-clicked
        fields. The argument should contain `x` and `y` members that represent
        coordinates in the grid.
        Negative values mean index from the back. E.g. -1, -3 on a 10x10 grid
        means indecies of: 9,7.
     */
    function addTarget(target) {
        if (target.x < 0) target.x += _grid.cols;
        if (target.y < 0) target.y += _grid.rows;
        _targets.push(target);
    }

    /*!
        addRandomTargets adds `count` of targets with random coordinates
     */
    function addRandomTargets(count) {
        for (var i = 0; i < count; i++) {
            var randomField = {
                "x": Math.floor(Math.random() * _grid.cols),
                "y": Math.floor(Math.random() * _grid.rows)}
            addTarget(randomField);
        }
    }

    /*!
        Call addEdge to add set of targets that consitute the edge of the
        screen. `edgeName` is the string specifying which edge should be added.
        This might be one of the following: 'top', 'bottom', 'right', 'left'.
     */
    function addEdge(edgeName) {
        switch(edgeName) {
        case "top":
            for(var i = 0; i < _grid.cols; i++)
                addTarget({"x": i, "y": 0});
            break;
        case "bottom":
            for(var i = _grid.cols - 1; i >= 0; i--)
                addTarget({"x": i, "y": _grid.rows-1});
            break;
        case "left":
            for(var i = _grid.rows - 1; i >= 0; i--)
                addTarget({"x": 0, "y": i});
            break;
        case"right":
            for(var i = 0; i < _grid.rows; i++)
                addTarget({"x": _grid.cols-1, "y": i});
            break;
        }
    }

    /*!
        Call runTest() to start processing test fields.
        Testing procedure normally ends with `onAllTargetsHit` signal being
        triggered.
     */
    function runTest() {
        var currentTarget = _targets.shift();
        var col = currentTarget.x;
        var row = currentTarget.y;

        // create component
        var fieldComponentName = "touchField-" + row.toString() +
                                 "x" + col.toString();
        var currentField = Qt.createQmlObject(
            _touchFieldDefinition, screenTest, fieldComponentName);
        currentField.width = _grid.fieldWidth;
        currentField.height = _grid.fieldHeight;
        currentField.x = _grid.fieldWidth*col;
        currentField.y = _grid.fieldHeight*row;
        currentField.color = UbuntuColors.green;
        _grid[row][col].component = currentField

        fieldClicked.connect(function(row, col) {
            if(row === currentTarget.y && col === currentTarget.x) {
                // disconnect self, so we don't activate ALL next fields while
                // touching the current one
                fieldClicked.disconnect(arguments.callee);
                _grid[row][col].component.color = "grey";
                if(_targets.length === 0) {
                    allTargetsHit();
                } else {
                    runTest(_targets);
                }
            }
        });
    }

    MultiPointTouchArea {
        anchors.fill: parent
        mouseEnabled: true
        Timer {
            id: tripleClickTimeout
            interval: 400

            property var clickCount: 0
            onTriggered: {
                clickCount = 0;
                stop();
            }
        }

        onPressed: {
            // signalling touchUpdated makes clicking with mouse without moving
            // the cursor work as expected
            touchUpdated(touchPoints)
            tripleClickTimeout.restart();
            if (++tripleClickTimeout.clickCount > 2) {
                tripleClicked();
                tripleClickTimeout.stop();
                tripleClickTimeout.clickCount = 0;
            }
        }

        onTouchUpdated: {
            for (var i in touchPoints) {
                _grid.click(touchPoints[i].x, touchPoints[i].y);
            }
        }
    }

    Component.onCompleted: {
        _grid = _createGrid(resolution);
    }

    function _createGrid(resolution) {
        // initiate the grid of fields
        // NOTE: components creation is deferred until they are needed
        var _grid = {};
        _grid.cols = Math.round(resolution*(width/height));
        _grid.rows = resolution;
        _grid.fieldWidth = width/_grid.cols;
        _grid.fieldHeight = height/_grid.rows;
        for (var row = 0; row<_grid.rows; row++) {
            _grid[row] = {};
            for (var col = 0; col<_grid.cols; col++) {
                _grid[row][col] = {};
                _grid[row][col].label = row.toString() + "x" + col.toString();
                _grid[row][col].multi = row*col;
            }
        }
        _grid.click = function(x, y) {
            //compute indecies of the field from page coords
            var col = Math.floor(x / _grid.fieldWidth);
            var row = Math.floor(y / _grid.fieldHeight);
            fieldClicked(row, col)
        }
        return _grid;
    }

    property var _grid
    property var _targets: [];
    // string used for dynamic creation of fields
    property var _touchFieldDefinition: "
    import QtQuick 2.0
        Rectangle {
            id: rectangle
            radius: 0.2 * width
        }
    "
}
