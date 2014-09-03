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

/*! \brief Test verification page

    This page asks user whether the action was completed successfully
    See design document at: http://goo.gl/ghR9wL
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1

Page {
    property alias testName: testNameLabel.text
    property alias verificationDescription: verificationDescriptionLabel.text

    signal verificationDone(bool result);
    signal testSkipped();

    title: i18n.tr("Verification")

    head {
        actions: [
            Action {
                iconName: "media-seek-forward"
                text: i18n.tr("Skip")
                onTriggered: {
                    testSkipped();
                }
            }
        ]
    }

    ColumnLayout {
        id: descriptionContent
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
            id: verificationDescriptionLabel
            fontSize: "medium"
            Layout.fillWidth: true
            Layout.fillHeight: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        }

        LatchButton {
            unlatchedColor: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Yes")
            onLatchedClicked: {
                verificationDone(true);
            }
        }

        LatchButton {
            unlatchedColor: UbuntuColors.red
            Layout.fillWidth: true
            text: i18n.tr("No")
            onLatchedClicked: {
                verificationDone(false);
            }
        }
    }
}
