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
import Ubuntu.Components 1.3

Page {
    id: welcomePage

    objectName: "welcomePage"

    signal startTestingTriggered();
    signal aboutClicked();
    property alias welcomeText: welcomeText.text

    title: i18n.tr("System Testing")
    visible: false

    function enableButton() {
        startTestButton.unlatch();
        state = "loaded";
    }
    header: PageHeader {
        Component.onCompleted: {
            console.log('DEPTH: ', pageStack.depth)
        }
        leadingActionBar { actions: [] }
        trailingActionBar {
            actions: [
                Action {
                    id: continueAction
                    iconName: "info"
                    text: i18n.tr("About")
                    onTriggered: aboutClicked()
                }
            ]
        }
    }


    Label {
        id: welcomeText

        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            bottom: startTestButton.top
        }

        text: ""
        fontSize: "large"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
    }
    state: "loading"
    states: [
        State {
            name: "loading"
            PropertyChanges { target: startTestButton; enabled: false; color: UbuntuColors.warmGrey; text: i18n.tr("Checkbox is loading...") }
            PropertyChanges { target: loadingSpinner; running: true}

        },
        State {
            name: "loaded"
            PropertyChanges { target: startTestButton; enabled: true; color: UbuntuColors.green; text: i18n.tr("Start testing")}
            PropertyChanges { target: loadingSpinner; running: false}
        }
    ]
    transitions: Transition {
        from: "loading"; to: "loaded"
        ColorAnimation {
            duration: 250
        }
    }


    ActivityIndicator {
        id: loadingSpinner
        anchors {
            bottom: startTestButton.top
            left: parent.left
            right: parent.right
            bottomMargin: units.gu(4)
        }
        implicitHeight: units.gu(6)
        implicitWidth: units.gu(6)
    }

    LatchButton {
        id: startTestButton
        objectName: "startTestButton"
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            topMargin: units.gu(3)
            bottomMargin: units.gu(3)
            leftMargin: units.gu(1)
            rightMargin: units.gu(1)
        }

        unlatchedColor: UbuntuColors.green
        text: i18n.tr("Start testing")
        onLatchedClicked: startTestingTriggered();
    }
}
