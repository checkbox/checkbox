/*
 * This file is part of Checkbox
 *
 * Copyright 2016 Canonical Ltd.
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
/*! 
    \brief Header with embedded progress bar
*/
import Ubuntu.Components 1.3
import QtQuick.Layouts 1.1
import QtQuick 2.2

PageHeader {
    id: header
    property alias progressText: _progressText.text
    property alias value: _progressBar.value
    property alias maximumValue: _progressBar.maximumValue

    ColumnLayout{
        anchors {
            fill: parent
            verticalCenter: parent.verticalCenter
            bottomMargin: units.gu(0.5)
            rightMargin: units.gu(2)
            leftMargin: units.gu(5)
        }
        Label {
            id: _progressText
            fontSize: "x-small"
            font.weight: Font.Light
            anchors.right: _progressBar.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: units.gu(0.5)
            text : Number(_progressBar.value / _progressBar.maximumValue * 100.0).toFixed(0) + "% (" + _progressBar.value + "/" + _progressBar.maximumValue + ")";
        }
        ProgressBox {
            id: _progressBar
            value: 0
            maximumValue: 1
            implicitWidth: parent.width - trailingActionBar.width
            anchors.bottom: parent.bottom
        }
    }
}
