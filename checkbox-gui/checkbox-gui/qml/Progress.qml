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

Item {
    property alias title: progresslabel.text
    property alias value: progressbar.value
    property alias maxValue: progressbar.maximumValue

    Label {
        id: progresslabel
        text: ""
        anchors.left: parent.left
    }

    ProgressBar {
        id: progressbar
        width: parent.width
        anchors.top: progresslabel.bottom
        anchors.topMargin: units.gu(1)
        indeterminate: false
        minimumValue: 0
        maximumValue: 100
        value: 0
        anchors.left: parent.left
    }
}
