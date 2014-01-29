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
            var mysavepath = guiEngine.GetSaveFileName();
            runmanagerview.reportIsSaved = guiEngine.GuiExportSessionToFileAsXML(mysavepath);
        }
    }
    Button {
        id: view_button
        text: i18n.tr("View Results")
        color: UbuntuColors.lightAubergine
        onClicked: {
            onClicked:{
                var mysavepath = '/tmp/report.html';
                runmanagerview.reportIsSaved = guiEngine.GuiExportSessionToFileAsHTML(mysavepath);
                cmdTool.exec("xdg-open", mysavepath)
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

            onCancel: PopupUtils.close(dialog)
        }
    }
}
