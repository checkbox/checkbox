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
    property bool onlyOneAllowed: false
    property bool emptyAllowed: false
    property bool largeBuffer: false

    visible: false
    flickable: null
    property var selectedCount : 0
    property var disabledSelectedCount: 0
    state : selectedCount > 0 ? "nonempty selection" :
        (disabledSelectedCount > 0 ? "disabled only selection" : "empty selection")

    // A function that needs to be called after changes are done to the model
    // to re-count number of selected items on the list
    function modelUpdated() {
        selectedCount = 0;
        disabledSelectedCount = 0;
        for (var i=0; i < selectionModel.count; i++) {
            if (selectionModel.get(i).mod_selected) {
                if (selectionModel.get(i).mod_disabled) {
                    disabledSelectedCount++;
                } else {
                    selectedCount++;
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
        selectedCount = 0;
        disabledSelectedCount = 0;
        for (var i=0; i<selectionModel.count; i++) {
            if (!selectionModel.get(i)["mod_disabled"]) {
                selectionModel.setProperty(i, "mod_selected", false);
            } else {
                if (selectionModel.get(i).mod_selected) {
                    disabledSelectedCount++;
                }
            }
        }
    }
    function selectAll() {
        selectedCount = 0;
        disabledSelectedCount = 0;
        for (var i=0; i<selectionModel.count; i++) {
            if (!selectionModel.get(i)["mod_disabled"]) {
                selectionModel.setProperty(i, "mod_selected", true);
                selectedCount++;
            } else {
                if (selectionModel.get(i).mod_selected) {
                    disabledSelectedCount++;
                }
            }
        }
    }

    head {
        actions: [
            Action {
                id: toggleSelection
                objectName: "toggleSelectionAction"
                iconName: "select"
                text: i18n.tr("Toggle selection")
                visible: !onlyOneAllowed
                onTriggered: {
                    if (state === "empty selection" || state == "disabled only selection") {
                        selectAll();
                    }
                    else if (state === "nonempty selection") {
                        deselectAll();
                    }

                }
            }
        ]
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

    ColumnLayout {
        spacing: units.gu(3)
        anchors {
            fill: parent
            topMargin: units.gu(3)
            bottomMargin: units.gu(3)
            leftMargin: units.gu(1)
            rightMargin: units.gu(1)
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
                id: selectionModel
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
                            // clear other selections
                            deselectAll();
                        }
                        selectionModel.setProperty(index, 'mod_selected', !checked);
                        selectedCount += checked ? 1 : -1;
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
