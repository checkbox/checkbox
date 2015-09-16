/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
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

/*! \brief ColumnLayout components with header and body labels already included
 *  and some common UX properties already set.
 */

import QtQuick 2.0
import QtQuick.Layouts 1.1
import Ubuntu.Components 1.1
import Ubuntu.Components.Popups 0.1

ColumnLayout {
    /* this property is the text to be shown in the top label */
    property var header: ""

    /* this property is the text that's used as the main body of the page. It
     * will be wrapping itself, filling width of the page (column), and will be
     * flickable */
    property var body: ""

    /* set fullHeightBody to false if you want to have control over layout in
     * the code that uses TestPageBody. You might want for instance have one
     * item that dominates the page.
     * If left set as true the layout is split evenly between children. */
    property var fullHeightBody: true

    spacing: units.gu(3)
    anchors {
        fill: parent
        topMargin: units.gu(3)
        bottomMargin: units.gu(3)
        leftMargin: units.gu(1)
        rightMargin: units.gu(1)
    }

    Label {
        objectName: "headerLabel"
        fontSize: "large"
        Layout.fillWidth: true
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        text: header
        font.bold: true
    }

    Flickable {
        Layout.fillWidth: true
        Layout.fillHeight: fullHeightBody
        contentHeight: childrenRect.height
        flickableDirection: Flickable.VerticalFlick
        clip: true
        Label {
            fontSize: "medium"
            anchors.fill: parent
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: body
        }
    }
}
