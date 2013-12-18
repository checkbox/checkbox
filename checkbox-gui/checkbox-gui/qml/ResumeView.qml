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


Page {
    title: i18n.tr("Resume")


    Text {
        id: querylabel
        width: parent.width - units.gu(40)
        wrapMode: Text.Wrap
        anchors {
            horizontalCenter: parent.horizontalCenter
            top: parent.top
            topMargin: units.gu(10)
        }

        text: "Checkbox did not finish completely.  \nDo you want to rerun the last test, \ncontinue to the next test, \nor restart from the begining?"
        color: "black"
        horizontalAlignment: Text.AlignHCenter
        font.pointSize: 20
    }

    Column {
        id: buttoncol
        spacing: units.gu(6)
        anchors {
            top: querylabel.bottom
            topMargin: units.gu(12)
            horizontalCenter: parent.horizontalCenter
        }
        property int buttonWidth: parent.width - units.gu(40)


        Button {
            id: rerunButton
            text: i18n.tr("Rerun last test")
            width: buttoncol.buttonWidth
            color: UbuntuColors.orange
            onClicked: {

                // Prepare for the run
                guiEngine.GuiResumeSession(true /* re-run last test */);

                // We need this to show the list of stuff
                testitemFactory.CreateTestListModel(testListModel);

                mainView.state = "RUNMANAGER"
            }
        }

        Button {
            id: continueButton
            text: i18n.tr("Continue")
            width: buttoncol.buttonWidth
            color: UbuntuColors.lightAubergine
            onClicked: {


                // Prepare for the run
                guiEngine.GuiResumeSession(false /* re-run last test */);

                // We need this to show the list of stuff
                testitemFactory.CreateTestListModel(testListModel);

                mainView.state = "RUNMANAGER"
            }
        }

        Button {
            id: restartButton
            text: i18n.tr("Restart")
            width: buttoncol.buttonWidth
            color: UbuntuColors.warmGrey
            onClicked: {

                // Lets clean up the old session
                guiEngine.GuiSessionRemove();

                // And create a fresh one
                guiEngine.GuiCreateSession();

                mainView.state = "WELCOME"
            }
        }
    }

}
