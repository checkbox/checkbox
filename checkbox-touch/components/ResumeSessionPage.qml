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

/*! \brief Page for resume session options

    This page lets user resume session they were previously running
    See design document at: http://goo.gl/gpelpD
*/

import QtQuick 2.0
import Ubuntu.Components 1.3
import QtQuick.Layouts 1.1
import "CbtDialogLogic.js" as CbtDialog

Page {
    id: root
    property alias resumeText: resumeLabel.text
    property var incompleteSessionCount: 0
    signal rerunLast();
    signal continueSession(var outcome);
    signal restartSession();
    signal deleteIncomplete();

    objectName: "resumeSessionPage"
    visible: false

    header: PageHeader {
        leadingActionBar { actions: [] }
        title: i18n.tr("Resume session")
    }

    ColumnLayout {
        id: columnLayout
        spacing: units.gu(3)
        anchors {
            top: parent.header.bottom
            bottom: parent.bottom
            right: parent.right
            left: parent.left
            topMargin: units.gu(3)
            bottomMargin: units.gu(3)
            leftMargin: units.gu(1)
            rightMargin: units.gu(1)
        }

        function latchGroup() {
            rerunButton.state = "latched";
            continueButton.state = "latched";
            restartButton.state = "latched";
        }

        Label {
            id: resumeLabel
            fontSize: "x-large"
            Layout.fillWidth: true
            Layout.fillHeight: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        }

        LatchButton {
            id: deleteIncompleteButton
            objectName: "deleteIncompleteButton"
            visible: incompleteSessionCount > 0
            text: i18n.tr("Delete incomplete sessions (%1)").arg(incompleteSessionCount)
            unlatchedColor: UbuntuColors.red
            Layout.fillWidth: true
            onLatchedClicked: {
                deleteIncomplete();
                columnLayout.latchGroup();
            }
        }

        LatchButton {
            id: rerunButton
            objectName: "rerunButton"
            unlatchedColor: UbuntuColors.warmGrey
            Layout.fillWidth: true
            Label {
                objectName: "rerunButtonLabel"
                anchors.centerIn: parent
                Layout.fillHeight: true
                Layout.fillWidth: true
                color: "white"
                text: i18n.tr("Rerun last")
            }
            onLatchedClicked: {
                rerunLast();
                columnLayout.latchGroup();
            }
        }

        LatchButton {
            id: continueButton
            objectName: "continueButton"
            unlatchedColor: UbuntuColors.warmGrey
            Layout.fillWidth: true
            Label {
                objectName: "continueButtonLabel"
                anchors.centerIn: parent
                Layout.fillHeight: true
                Layout.fillWidth: true
                color: "white"
                text: i18n.tr("Continue")
            }
            onLatchedClicked: {
                columnLayout.latchGroup();
                CbtDialog.showDialog(root, i18n.tr('What to do with the last job?'), [
                    {
                        'text': i18n.tr('Pass'),
                        'objectName': 'passBtn',
                        'color': UbuntuColors.green,
                        'onClicked': function() {
                            continueSession('pass')
                        }
                    },
                    {
                        'text': i18n.tr('Skip'),
                        'objectName': 'skipBtn',
                        'color': '#FF9900',
                        'onClicked': function() {
                            continueSession('skip')
                        }
                    },
                    {
                        'text': i18n.tr('Fail'),
                        'objectName': 'failBtn',
                        'color': UbuntuColors.red,
                        'onClicked': function() {
                            continueSession('fail')
                        }
                    },
                ]);
            }
        }

        LatchButton {
            id: restartButton
            objectName: "restartButton"
            unlatchedColor: UbuntuColors.warmGrey
            Layout.fillWidth: true
            Label {
                objectName: "restartButtonLabel"
                anchors.centerIn: parent
                Layout.fillHeight: true
                Layout.fillWidth: true
                color: "white"
                text: i18n.tr("Start new session")
            }
            onLatchedClicked: {
                restartSession();
                columnLayout.latchGroup();
            }
        }
    }
}
