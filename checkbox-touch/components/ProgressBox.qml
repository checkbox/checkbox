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
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1

/*! \brief Progress Box.
    \inherits Item

    This widget is a ProgressBar-like item with some changes compared to
    ProgressBar found in Ubuntu Components. This one uses layouts, so it can
    fills the width of the components it is placed in. ProgressBox can display
    an information about the progress prefixes by text set in `interlude` var.
    If the box is to be narrower then the space required by full text,
    interlude is ommited. The formatting of the text is as follows:
    "$interlude $vlaue / $maximumValue"
*/

Item {
    id: progressBox

    /*!
      Value to be used when filling progress bar.
      */
    property alias value: progressBar.value

    /*!
      Progress bar is entirely when value reaches maximumValue
     */
    property real maximumValue: 100

    /*!
      Prefix text to show on top of progress bar
     */
    property string interlude: ""

    /*!
      Gets signalled when the user taps/clicks on the component.
     */
    signal clicked()

    anchors.right: parent.right
    anchors.left: parent.left
    anchors.top: parent.top

    Layout.fillWidth: true


    StyledItem {
        id: progressBar
        anchors.fill: parent

        property real value: 50
        property real maximumValue: progressBox.maximumValue
        property real minimumValue: 0
        property bool showProgressPercentage: false // for compability with underlaying styling
        property bool indeterminate: false // for compability with underlaying styling
        style: Theme.createStyleComponent("ProgressBarStyle.qml", progressBar)

    }
    Label {
        id: longDescription
        Layout.fillWidth: true
        anchors.fill: parent
        color: "black"
        text: progressBox.interlude + " " + progressBar.value + " / " + progressBar.maximumValue
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        visible: paintedWidth < width // visible only if full text fits into the progressBox, otherwise use short label

    }
    Label {
        id: shortDescription
        Layout.fillWidth: true
        anchors.fill: parent
        text: progressBar.value + " / " + progressBar.maximumValue
        color: "black"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        visible: !longDescription.visible // it's always one or the other
    }
    MouseArea {
        anchors.fill: parent
        onClicked: progressBox.clicked()
    }
}
