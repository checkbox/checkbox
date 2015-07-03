/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Jonathan Cave <jonathan.cave@canonical.com>
 *
 * Checkbox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3,
 * as published by the Free Software Foundation.
 *
 * Checkbox is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
 */
import QtQuick 2.2

Item {
    id: smsTest

    anchors.fill: parent


    property var testingShell
    signal testDone(var test)
    
    GenericSmsTest {
        id: testPages

        Component.onCompleted: {
            testPages.setTestActionText("Send an SMS Message to a contact"
                + " containing special characters...")
            
            testPages.setPredefinedContent("!\"£$%😆^&*()😁")
        }
    }
}



