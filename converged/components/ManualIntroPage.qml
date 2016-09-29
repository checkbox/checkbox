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

/*! \brief Page for Manual test - introduction step

    This page shows test name and description of an Manual test.
    See design document at: http://goo.gl/vrD9yn
*/

import QtQuick 2.0
import Ubuntu.Components 1.3
import QtQuick.Layouts 1.1
import Ubuntu.Components.Popups 1.3
import "actions"

Page {
    id: manualIntroPage
    objectName: "manualIntroPage"
    property var test: { "name": "", "description": "", "test_number": 0, "tests_count": 0}

    signal continueClicked();
    signal testDone(var test);

    onTestChanged: {
        header.value = test['test_number']
        header.maximumValue = test['tests_count']
    }
    header: ProgressHeader {
        value: test['test_number']
        maximumValue: test['tests_count']
        title: i18n.tr("Test Description")
        leadingActionBar { actions: [] }
        trailingActionBar {
            objectName: 'trailingActionBar'
            actions: [
                AddCommentAction {
                    id: addCommentAction
                },
                SkipAction {
                    id: skipAction
                }
            ]
        }
    }

    TestPageBody {
        header: test["name"]
        body: test["description"]
        Button {
            id: continueButton
            objectName: "continueButton"
            color: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Start the test")
            onClicked: {
                continueClicked();
            }
        }
    }
    Component.onCompleted: {
        rootKeysDelegator.setHandler('alt+s', manualIntroPage, skipAction.trigger);
        rootKeysDelegator.setHandler('alt+c', manualIntroPage, addCommentAction.trigger);
        rootKeysDelegator.setHandler('alt+t', manualIntroPage, continueButton.clicked);
    }
}
