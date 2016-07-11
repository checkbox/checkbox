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
import QtQuick.Layouts 1.1
import Ubuntu.Components 1.3
import Ubuntu.Components.ListItems 0.1 as ListItem

/*! \brief Selection page

    This page lets the user select items from the list. Items can be grouped
    together.
    See design document here: http://goo.gl/vkqvIC
*/

Page {
    id: root
    signal selectionDone(var selected_id_list)
    property string continueText: i18n.tr("Continue")
    readonly property alias model: selectionModel
    property alias keys: keysDelegator
    property bool onlyOneAllowed: false
    property bool emptyAllowed: false
    property bool largeBuffer: false
    property string title: ''

    visible: false
    flickable: null
    property var selectedCount : 0
    property var filteredSelectedCount: 0
    property var disabledSelectedCount: 0
    property var filter: new RegExp('.*');
    state : selectedCount > 0 ? "nonempty selection" :
        (disabledSelectedCount > 0 ? "disabled only selection" : "empty selection")
    ListModel {
        // This model holds all items that can be selected, even when filtered-out
        id: selectionModel
    }

    // A function that needs to be called after changes are done to the model
    // to re-count number of selected items on the list
    function modelUpdated() {
        selectedCount = 0;
        disabledSelectedCount = 0;
        for (var i=0; i < selectionModel.count; i++) {
            var modelItem = selectionModel.get(i);
            if (modelItem.mod_selected) {
                if (modelItem.mod_disabled) {
                    disabledSelectedCount++;
                } else {
                    selectedCount++;
                }
            }
        }
        updateFilteredModel();
    }
    function updateFilteredModel() {
        filteredSelectionModel.clear();
        filteredSelectedCount = 0;
        for (var i=0; i < selectionModel.count; i++) {
            var modelItem = selectionModel.get(i);
            modelItem['fullListIndex'] = i;
            if (modelItem.mod_name.search(filter) > -1) {
                filteredSelectionModel.append(modelItem);
                if (modelItem.mod_selected) {
                    filteredSelectedCount++;
                }
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
    function unlatchContinue() {
        continueButton.unlatch();
    }
    function deselectAll() {
        for (var i=0; i<filteredSelectionModel.count; i++) {
            var modelItem = filteredSelectionModel.get(i);
            if (!modelItem.mod_disabled) {
                if (modelItem.mod_selected) {
                    filteredSelectionModel.setProperty(i, "mod_selected", false);
                    selectionModel.setProperty(modelItem.fullListIndex, "mod_selected", false);
                    selectedCount--;
                    filteredSelectedCount--;
                }
            }
        }
    }
    function selectAll() {
        for (var i=0; i<filteredSelectionModel.count; i++) {
            var modelItem = filteredSelectionModel.get(i);
            if (!modelItem.mod_disabled) {
                if (!modelItem.mod_selected) {
                    filteredSelectionModel.setProperty(i, "mod_selected", true);
                    selectionModel.setProperty(modelItem.fullListIndex, "mod_selected", true);
                    selectedCount++;
                    filteredSelectedCount++;
                }
            }
        }
    }

    header: PageHeader {
        title: root.title
        trailingActionBar {
            objectName: 'trailingActionBar'
            actions: [
                Action {
                    id: toggleSelection
                    objectName: "toggleSelectionAction"
                    iconName: "select"
                    text: i18n.tr("Toggle selection")
                    visible: !onlyOneAllowed
                    onTriggered: {
                        if (state === "empty selection" || state == "disabled only selection") {
                            if (!onlyOneAllowed) // still reachable via key shortcut
                                selectAll();
                        }
                        else if (state === "nonempty selection") {
                            deselectAll();
                        }
                    }
                },
                Action {
                    id: findAction
                    text: i18n.tr("Find")
                    iconName: 'find'
                    onTriggered: {
                        if (!searchBox.visible) {
                            searchBox.visible = true;
                            searchBox.forceActiveFocus();
                        } else {
                            searchBox.visible = false;
                        }
                    }
                }
            ]
        }
    }

    states: [
         State {
            name: "empty selection"
            PropertyChanges { target: continueButton;
                              enabled: false || emptyAllowed }
         },
         State {
            name: "nonempty selection"
            PropertyChanges { target: continueButton; enabled: true }
         },
         State {
            name: "disabled only selection"
            PropertyChanges { target: continueButton; enabled: true }
         }
    ]

    KeysDelegator {
        id: keysDelegator
        onKeyPressed: {
            var c = event.text
            if (event.modifiers == 0 && c.search(/[a-z]/, 'i') > -1) {
                searchBox.insert(searchBox.cursorPosition, c)
                searchBox.forceActiveFocus();
                searchBox.visible = true
                searchBox.focus = true
            }
            if (event.key == Qt.Key_Escape) {
                searchBox.text = '';
                searchBox.focus = false;
                searchBox.visible = false;
            }
        }
        Component.onCompleted: {
            setHandler('alt+c', function() {
                if (selectedCount > 0) {
                    gatherSelection();
                }
            });
            setHandler('alt+t', toggleSelection.trigger);
        }
    }

    ColumnLayout {
        spacing: units.gu(3)
        anchors {
            top: parent.header.bottom
            bottom: parent.bottom
            right: parent.right
            left: parent.left
            topMargin: units.gu(1)
            bottomMargin: units.gu(3)
            leftMargin: units.gu(1)
            rightMargin: units.gu(1)
        }

        TextField {
            id: searchBox
            Layout.fillWidth: true
            visible: false
            onTextChanged: {
                filter = new RegExp('.*' + text, 'i');
                updateFilteredModel();
            }
            onFocusChanged: {
                if (text == '' && focus == false) {
                    visible = false;
                }
            }
        }

        Component {
            id: sectionHeading
            Item {
                height: units.gu(4)
                anchors {
                    left: parent ? parent.left : undefined
                    right: parent ? parent.right : undefined
                }

                Label {
                    fontSize: "medium"
                    font.bold: true
                    text: section
                    anchors {
                        verticalCenter: parent.verticalCenter
                        left: parent.left
                        right: parent.right
                        margins: units.gu(1)
                    }
                }

                ListItem.ThinDivider {
                    anchors {
                        left: parent.left
                        right: parent.right
                        bottom: parent.bottom
                    }
                }
            }
        }

        UbuntuListView {
            model: ListModel {
                id: filteredSelectionModel
            }
            objectName: "listView"
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            cacheBuffer: (largeBuffer) ? cacheBuffer * 10 : cacheBuffer
            delegate: ListItemWrappable {
                objectName: "listItem"
                text: mod_name
                enabled: !mod_disabled
                property var item_mod_id: mod_id
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
                        if (onlyOneAllowed && !checked && selectedCount > 0) {
                            deselectAll();
                            // clear other selections on the original list
                            for (var i=0; i < selectionModel.count; i++) {
                                var modelItem = selectionModel.get(i);
                                if (!modelItem.mod_disabled) {
                                    if (modelItem.mod_selected) {
                                        selectionModel.setProperty(i, "mod_selected", false);
                                        selectedCount--;
                                    }
                                }
                            }
                        }
                        filteredSelectionModel.setProperty(index, 'mod_selected', !checked);
                        selectedCount += checked ? 1 : -1;
                        // propagate selection to the original list
                        selectionModel.setProperty(fullListIndex, 'mod_selected', checked);

                    }
                }
                onClicked: checkBox.clicked()
            }
            section.property: "mod_group" // NOTE: this is a model reference
            section.criteria: ViewSection.FullString
            section.delegate: sectionHeading
            snapMode: ListView.SnapToItem
        }

        LatchButton {
            id: continueButton
            objectName: "continueButton"
            Layout.fillWidth: true
            text: continueText
            unlatchedColor: UbuntuColors.green
            onLatchedClicked: gatherSelection()
        }
    }
}
