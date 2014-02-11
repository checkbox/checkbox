/*
 * This file is part of Checkbox
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
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
import Ubuntu.Components 0.1
import Ubuntu.Components.ListItems 0.1 as ListItem
import "./artwork"


    Item {
        id: itemdelegate
        width: parent.width
        height: units.gu(7)

        Item {
            id: suitefiller
            width: units.gu(1)
        }

        CheckBox {
            id: suitecheckbox
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: suitefiller.right
            checked: false
            onCheckedChanged: {
                // Update the list of selected whitelists
                update_selection(testname, checked)
                /* Update the ListView, primarily to ensure we dont
                 * uncheck ALL the whitelists.
                 */
                suitelist.ensure_one_selection();
            }
            function suiteSelectHandler() {
                checked = check
            }
            Component.onCompleted: {
                testselection.suiteSelect.connect(suiteSelectHandler)
            }
        }

        function update_selection(testname, checked){
            for (var i = whiteListModel.count - 1; i >= 0; i--){
                var item = whiteListModel.get(i);
                if (item.testname === testname){
                    whiteListModel.setProperty(i, "check", checked);
                }
            }
        }

        function remove_prefix_and_capitalize_first(prefix, suite) {
            var suitename = suite.replace(prefix, '')
            return suitename.substr(0, 1).toUpperCase() + suitename.substr(1)
        }

        Text {
            id: suitetext
            text: remove_prefix_and_capitalize_first('ihv-', testname)
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: suitecheckbox.right
            anchors.leftMargin: units.gu(1)
        }

        ListItem.ThinDivider {}

        MouseArea {
            anchors.fill: parent
            onClicked: {
                suitecheckbox.checked = !suitecheckbox.checked
            }
        }
    }
