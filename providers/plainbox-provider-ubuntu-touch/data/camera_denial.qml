/*
 * This file is part of Checkbox.
 *
 * Copyright 2016 Canonical Ltd.
 * Written by:
 *   Maciej Kisielewski <maciej.kisielewski@canonical.com>
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
import QtQuick 2.0
import Ubuntu.Components 1.1
import QtMultimedia 5.2
import Plainbox 0.1

/*
    This test checks whether camera access was blocked by app armor.
    The test FAILS when the camera was initiated without a problem.
    This test should be launched as a confined QML job.
*/

QmlJob {
    Page {
        anchors.fill: parent
        Label {
            id: label
            text: i18n.tr("Launching camera")
        }
        VideoOutput {
            id: viewfinder
            visible: true
            source: cam
            anchors.fill: parent
            orientation: (Screen.primaryOrientation === Qt.PortraitOrientation) ? 270 : 0;
            fillMode: Image.PreserveAspectCrop
        }
    }
    Timer {
        id: resultTimer
        running: true
        interval: 1000
        onTriggered: {
            if (cam.errorCode) {
                testDone({'outcome': 'pass'});
            } else {
                testDone({'outcome': 'fail'});
            }
        }
    }
    Camera {
        id: cam
        captureMode: Camera.CaptureViewfinder
    }
}
