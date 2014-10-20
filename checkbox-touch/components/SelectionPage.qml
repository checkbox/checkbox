/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
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
import Ubuntu.Components 1.1
import Ubuntu.Components.ListItems 0.1 as ListItem

/*! \brief Selection page

    This page lets the user select items from the list. Items can be grouped
    together.
    See design document here: http://goo.gl/vkqvIC
*/

Page {
    signal selectionDone(var selected_id_list)
    property string continueText: i18n.tr("Continue")
    readonly property alias model: selectionModel

    visible: false
    property var selectedCount : 0
    state : selectedCount > 0 ? "nonempty selection" : "empty selection"

    // A function that needs to be called after changes are done to the model
    // to re-count number of selected items on the list
    function modelUpdated() {
        selectedCount = 0;
        for (var i=0; i < selectionModel.count; i++) {
            if (selectionModel.get(i).mod_selected) {
                selectedCount++;
            }
        }
    }
    function gatherSelection() {
        var selected_id_list = [];
        for (var i=0; i<selectionModel.count; ++i) {
            var model_item = selectionModel.get(i)
            if (model_item.mod_selected) {
                selected_id_list.push(model_item.mod_id);
            }
        }
        selectionDone(selected_id_list);
    }

    head {
        actions: [
            Action {
                id: continueAction
                iconName: "media-playback-start"
                text: continueText
                onTriggered: gatherSelection()
            },
            Action {
                id: selectAllAction
                iconName: "select"
                text: i18n.tr("Select All")
                onTriggered: {
                    for (var i=0; i<selectionModel.count; i++) {
                        selectionModel.setProperty(i, "mod_selected", true);
                    }
                    selectedCount = selectionModel.count;
                }
            },
            Action {
                id: deselectAllAction
                iconName: "clear-search"
                text: i18n.tr("Deselect All")
                onTriggered: {
                    for (var i=0; i<selectionModel.count; i++) {
                        selectionModel.setProperty(i, "mod_selected", false);
                    }
                    selectedCount = 0;
                }
            }
        ]
    }

    states: [
         State {
            name: "empty selection"
            PropertyChanges { target: continueAction; enabled: false }
         },
         State {
            name: "nonempty selection"
            PropertyChanges { target: continueAction; enabled: true }
         }
    ]

    UbuntuListView {
        model: ListModel { 
            id: selectionModel
        }
        anchors.fill: parent
        delegate: ListItem.Standard {
            text: mod_name
            /* Create a checkbox-lookalike that doesn't have the internal onTrigger
             * signal handler that overrides the binding to the model.mod_selected
             * property. If we use the normal CheckBox component here then the
             * state gets desynchronized after every click (which simply does
             * checked = !checked via javascript, thus erasing the property binding
             *
             * TODO: file a bug on this.
             */
            control: AbstractButton {
                id: checkBox
                readonly property bool checked: mod_selected
                style: Theme.createStyleComponent("CheckBoxStyle.qml", checkBox)
                // Toggle the mod_selected property
                onClicked: {
                    selectionModel.setProperty(index, 'mod_selected', !checked);
                    selectedCount += checked ? 1 : -1;
                }
            }
        }
        section.property: "mod_group" // NOTE: this is a model reference
        section.criteria: ViewSection.FullString
        section.delegate: ListItem.Header {
            text: section
        }
        snapMode: ListView.SnapToItem
        footer: Button {
            id: continueButton
            anchors {
                left: parent.left
                right: parent.right
                margins: units.gu(2)
            }
            enabled: continueAction.enabled
            text: continueText
            color: UbuntuColors.green
            onClicked: gatherSelection()
        }
    }
}
