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
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1

Page {
    property alias resumeText: resumeLabel.text
    signal rerunLast();
    signal continueSession();
    signal restartSession();

    objectName: "resumeSessionPage"
    title: i18n.tr("Resume session")
    visible: false

    ColumnLayout {
        id: columnLayout
        spacing: units.gu(3)
        anchors {
            fill: parent
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
                continueSession();
                columnLayout.latchGroup();
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
