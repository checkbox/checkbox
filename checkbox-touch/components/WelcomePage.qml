/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
 *
 * Authors:
 * - Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

Page {
    id: welcomePage

    signal startTestingTriggered();
    property alias welcomeText: welcomeText.text

    title: i18n.tr("System Testing")
    visible: false

    Label {
        id: welcomeText

        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            bottom: startTestButton.top
        }

        text: i18n.tr("Welcome text")
        fontSize: "large"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
    }

    Button {
        id: startTestButton

        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: units.gu(2)
        }

        color: UbuntuColors.green
        text: i18n.tr("Start Testing")
        onClicked: startTestingTriggered();
    }
}
