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
            // open the directory dialog
            // FYI, in QT 5.1, here's how to do it
            //                  import QtQuick 2.1
            //                  import QtQuick.Controls 1.0
            // fileDialog.open()

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

                // FIXME - Removed the integrated dialog until we have HTML file
//                PopupUtils.open(log_viewer_results, view_button);

                // Interim solution is to fire up a web browser
                // FIXME: ideally plainbox should generate a file that the app then has to unlink
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

            //onOk:// do nothing and return to submission dialog

            onCancel: PopupUtils.close(dialog)
        }
    }

    // Qt 5.1 can use this in theory rather than the QFileDialog
    //FileDialog {
    //    id: fileDialog
    //    title: "Please select a folder to save to:"
    //    selectFolder : true
    //    onAccepted: {
    //        console.log("You chose: " + fileDialog.fileUrls)
    //    }
     //   onRejected: {
     //       console.log("Canceled")
     //   }

}








