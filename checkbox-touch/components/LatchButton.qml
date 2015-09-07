/*
 * This file is part of Checkbox
 *
 * Copyright 2014, 2015 Canonical Ltd.
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

/*! \brief Latch button.
    \inherits Button

    This widget is a Button with latch functionality. I.e. once the button is
    clicked it cannot be clicked again until 'unlatch' method is called.
    The button also changes color depending on which state it is in.
*/
Button {
    id: root

    /*!
        Gets signalled when button is clicked while in 'unlatched' state
     */
    signal latchedClicked();

    /*!
        Call this method to change the state to 'unlatched'
     */
    function unlatch() {
        state="unlatched"
    }


    /*!
        Color of the button while in 'unlatched' state
     */
    property var unlatchedColor: UbuntuColors.green

    /*!
        Color of the button while in 'latched' state
     */
    property var latchedColor: UbuntuColors.warmGrey

    /*!
      Read-only property informing if button is currently latched.
     */
    readonly property bool isLatched: state === "latched"

    state: "unlatched"
    states: [
         State {
            name: "unlatched"
            PropertyChanges{ target: root; color: unlatchedColor }
            PropertyChanges{ target: root; enabled: true }
         },
         State {
            name: "latched"
            PropertyChanges{ target: root; color: latchedColor}
            PropertyChanges{ target: root; enabled: false }
         }
     ]

    onClicked: {
        if (state=="unlatched"){
            state="latched"
            latchedClicked();
        }
    }
}
