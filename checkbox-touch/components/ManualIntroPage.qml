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

/*! \brief Page for Manual test - introduction step

    This page shows test name and description of an Manual test.
    See design document at: http://goo.gl/vrD9yn
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1

Page {
    property alias testName: testNameLabel.text
    property alias testDescription: testDescrptionLabel.text

    signal continueClicked();
    signal testSkipped();

    objectName: "manualIntroPage"
    title: i18n.tr("Test Description")
    head {
        actions: [
            Action {
                id: skipAction
                iconName: "media-seek-forward"
                text: i18n.tr("Skip")
                onTriggered: {
                    testSkipped();
                }
            }
        ]
    }

    ColumnLayout {
        spacing: units.gu(3)
        anchors.fill: parent
        anchors.margins: units.gu(3)

        Label {
            id: testNameLabel
            fontSize: "large"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        }

        Label {
            id: testDescrptionLabel
            fontSize: "medium"
            Layout.fillWidth: true
            Layout.fillHeight: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        }

        Button {
            objectName: "continueButton"
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Continue")
            onClicked: {
                continueClicked();
            }
        }
    }
}
