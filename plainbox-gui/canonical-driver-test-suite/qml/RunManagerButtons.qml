/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
 * - Sylvain Pineau <sylvain.pineau@canonical.com>
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



Row {
    id: bottombuttons
    spacing: units.gu(12)

    property alias pauseButtonEnabled: pauseButton.enabled
    property alias resultsButtonEnabled: resultsButton.enabled
    property alias rerunButtonShown: pauseButton.showRerun
    property alias rerunButtonEnabled: pauseButton.enabled

    signal exit
    signal pauseTest
    signal resumeTest
    signal reRunTest
    signal results


    Button {
         id:cancelButton // todo rename as the exit button
         text: i18n.tr("Exit")
         color: UbuntuColors.coolGrey
         width: units.gu(18)
         onClicked: {
             bottombuttons.exit();
         }
    }

    // This can be Resume, Pause, or Re-run
    Button {
        id: pauseButton
        property bool showPause: true  // either Pause or Resume
        property bool showRerun: false // We may re-run
        enabled: true
        text: showRerun ? i18n.tr("Re-run") :( showPause ? i18n.tr("Pause") : i18n.tr("Resume"))
        color: UbuntuColors.lightAubergine
        width: units.gu(18)

        onClicked:{

            // Behaviour depends on state
            if (showRerun) {
                // Update the list of things the user _really_ wants to rerun
                testitemFactory.GetSelectedRerunJobs(testListModel);

                // return the button to pause/re-run
                showRerun = false;

                // Get on with it
                reRunTest()
                guiEngine.RunJobs();

            } else {
                showPause?pauseTest():resumeTest()
                showPause = !showPause
            }
        }

    }

    Button {
        id: resultsButton
        enabled: false
        text: i18n.tr("Results")
        color: UbuntuColors.orange
        width: units.gu(18)
        onClicked: {
            bottombuttons.results()
        }

    }


}
