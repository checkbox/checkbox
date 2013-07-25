/*
 * This file is part of plainbox-gui
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
import Ubuntu.Components.Popups 0.1
import "."

Dialog {
    id: dialog

    title: i18n.tr("Report")
    text: i18n.tr("The following report has be generated for submission to the Launchpad hardware database.")


    Button {
        id: savebutton
        text: i18n.tr("Save Results")
        color: UbuntuColors.orange
        onClicked: {
            // open the directory dialog
            PopupUtils.open(save_as_dialog, savebutton)
            runmanagerview.reportIsSaved = true;
        }
    }
    Button {
        id: view_button
        text: i18n.tr("View Results")
        color: UbuntuColors.lightAubergine
        onClicked: {
            onClicked:{
                PopupUtils.open(log_viewer_results, view_button);
                //cmdTool.exec("gedit", "qml/outline/artwork/test.txt"); // TODO PUT FILENAME HERE
            }
        }
    }
    Button {
        id: donebutton
        text: i18n.tr("Done")
        color: UbuntuColors.warmGrey
        onClicked: {
            if (!runmanagerview.reportIsSaved)
                PopupUtils.open(submission_warning_dialog, donebutton);
            else
                PopupUtils.close(dialog)
        }
    }

    Component {
        id: submission_warning_dialog
        WarningDialog{
            text: i18n.tr("You are about to exit this test run without saving your results report.  Do you want to save the report?");

            showContinue: false
            showCheckbox: false

            //onOk:// do nothing and return to submission dialog

            onCancel: PopupUtils.close(dialog)
        }
    }

    Component {
        id: log_viewer_results
        LogViewer{
            showTroubleShootingLink: false
            logHeight: units.gu(20)         // TODO - There is something wrong with the 'Dialog' that button become inactive when log view is too big

        }
    }

    Component {
        id: save_as_dialog
        FileDialog{
        }
    }



}








