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
import QtTest 1.0
import Ubuntu.Components 0.1
import "../../components"

Item {

    /*
        This test checks if only one latchedClicked is emited even when
        multiple clicked calls are made to the underlaying button
    */
    TestCase{
        LatchButton {
            id: lb_latching
            onLatchedClicked: {
                tc_test_latching.counter++
            }
        }
        id: tc_test_latching
        property var counter: 0

        function test_latching() {
            for (var i = 0; i < 10; i++) {
                lb_latching.clicked()
            }
            compare(1, counter,
                "latchedClicked should be signalled signalled 1 time. Got " +
                 counter + " times.")
        }
    }

    /*
        This test checks if latchedClicked signal is emited next time button
        is clicked after unlatch method was called.
    */
    TestCase{
        LatchButton {
            id: lb_unlatching
            onLatchedClicked: {
                tc_test_unlatching.counter++
            }
        }
        id: tc_test_unlatching
        property var counter: 0

        function test_unlatching() {
            for (var i = 0; i < 3; i++) {
                lb_unlatching.clicked()
            }
            lb_unlatching.unlatch()
            for (var i = 0; i < 3; i++) {
                lb_unlatching.clicked()
            }
            compare(2, counter,
                "latchedClicked should be signalled signalled 2 times. Got "
                + counter + " times.")
        }
    }
}
