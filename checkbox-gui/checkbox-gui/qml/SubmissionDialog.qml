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

DarkDialog {
    id: dialog

    title: i18n.tr("Report")
    text: settings.value("submission/message", i18n.tr("The following test report has been generated for submission to Launchpad. You may also view it or save it."))

    TextField {
        RegExpValidator {
            id: regex_validator
            regExp: new RegExp(settings.value("submission/regex", ".*"));
        }
        function initialize() {
            var input_type = settings.value("submission/input_type", "")
            if (input_type == "regex") {
                validator = regex_validator;
                visible = true;
            }
            else if (input_type == "none") {
                visible = false;
            }
            else {
                inputMethodHints = Qt.ImhEmailCharactersOnly;
                visible = true;
            }
            var secure_id = settings.value("submission/secure_id","");
            if (secure_id) {
                text = secure_id;
            }
        }

        id: upload_input
        placeholderText: settings.value("submission/input_placeholder", i18n.tr("Launchpad E-Mail Address"))
        Component.onCompleted: initialize()
    }

    Row {
        function initialize() {
            if (settings.value("submission/submit_to_hexr","false").toLowerCase() == "true") {
                visible = true;
            }
        }

        spacing: units.gu(8)
        visible: false
        Label {
            id: submit_to_hexr_label
            text: i18n.tr("Submit to HEXR:")
        }

        CheckBox {
            id: submit_to_hexr
            text: i18n.tr("Submit to HEXR:")
        }
        Component.onCompleted: initialize()

    }

    Button {
        id: submitbutton
        text: settings.value("submission/ok_btn_text", i18n.tr("Submit Results"))
        enabled: upload_input.acceptableInput
        color: UbuntuColors.orange
        onClicked: {
            var submit_to = settings.value("transport/submit_to", "")
            var export_path = settings.value("exporter/xml_export_path", "/tmp/submission.xml")

            if (submit_to == "certification") {
                if (updater.success) {
                    dialog.text = guiEngine.SendSubmissionViaCertificationTransport(export_path,
                                                                                    upload_input.text,
                                                                                    submit_to_hexr.checked);
                }
                else {
                    dialog.text = i18n.tr("Could not export the tests results for uploading.");
                }
            }
            else {
                dialog.text = guiEngine.SendSubmissionViaLaunchpadTransport(export_path,
                                                                            upload_input.text);
            }
        }
    }

    ListModel {
        function initialize() {
            reportTypeModel.append({"type": "xml", "name": i18n.tr("XML Report (*.xml)")})
            reportTypeModel.append({"type": "xlsx", "name": i18n.tr("XLSX Report (*.xlsx)")})
        }

        id: reportTypeModel
        Component.onCompleted: initialize()
    }

    Component {
        id: reportTypeDelegate
        OptionSelectorDelegate {
            text: name
        }
    }

    OptionSelector {
        id: reportTypeSelect
        model: reportTypeModel
        delegate: reportTypeDelegate
    }

    Button {
        id: save_button
        text: i18n.tr("Save Report")
        color: UbuntuColors.lightAubergine
        onClicked: {
            var option_list = new Array("client-name=" + client_name, "with-certification-status");
            var success = false;
            if (reportTypeSelect.selectedIndex == 0) {
                var path = guiEngine.GetSaveFileName('submission.xml',
                    i18n.tr("XML files (*.xml)"))
                success = guiEngine.GuiExportSessionToFileAsXML(path,
                                                                option_list);
            }
            else if (reportTypeSelect.selectedIndex == 1) {
                var path = guiEngine.GetSaveFileName('submission.xlsx',
                    i18n.tr("XLSX files (*.xlsx)"))
                success = guiEngine.GuiExportSessionToFileAsXLSX(path, ["with-sys-info", "with-summary", "with-job-description", "with-text-attachments"]);
            }

            if (success) {
                runmanagerview.reportIsSaved = success;
            }
        }
    }

    Button {
        id: view_button
        text: i18n.tr("View Results")
        color: UbuntuColors.lightAubergine
        onClicked: {
            onClicked:{
                var mysavepath = '/tmp/report.html';
                var option_list = new Array("client-name=" + client_name, "with-certification-status");
                runmanagerview.reportIsSaved = guiEngine.GuiExportSessionToFileAsHTML(mysavepath,
                                                                                      option_list);
                Qt.openUrlExternally(mysavepath);
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
            text: settings.value("submission/cancel_warning", i18n.tr("You are about to exit this test run without saving your results report.  Do you want to save the report?"))

            showContinue: false
            showCheckbox: false

            onCancel: PopupUtils.close(dialog)
        }
    }
}
