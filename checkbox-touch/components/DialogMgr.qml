/*
 * This file is part of Checkbox
 *
 * Copyright 2016 Canonical Ltd.
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
import QtQuick 2.0
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3

Item {
    function showDialog(caller, message, buttons) {
        var p = Qt.createComponent(Qt.resolvedUrl("CbtDialog.qml")).createObject(caller);
        p.buttons = buttons || [{ "text": i18n.tr("OK"), "color": "UbuntuColors.green"}];
        p.label = message;
        PopupUtils.open(p.dialog);
    }

    function confirmRequest(caller, options, continuation) {
        // if the question was answered before and user selected to
        // remember their selection - 'returning' true
        if (mainView.appSettings[options.question]) {
            continuation(true);
            return;
        }
        var p = Qt.createComponent(Qt.resolvedUrl("ConfirmationDialog.qml")).createObject(caller);
        p.withRemember = options.remember;
        p.question = options.question;
        p.answer.connect(function(result, remember) {
            mainView.appSettings[options.question] = remember;
            continuation(result);
        });
        PopupUtils.open(p.dialog);
    }

    function showError(caller, errorMessage, continuation, finalLabel) {
        // stackDepth keeps track of how many popups are stacked on the screen
        // we need this so continuation is called only if the last (the bottom one) popup
        // is closed
        showError.stackDepth = ++showError.stackDepth || 1;
        var p = Qt.createComponent(Qt.resolvedUrl("ErrorDialog.qml")).createObject(caller);
        p.errorMessage = errorMessage;
        if (showError.stackDepth > 1) {
            p.buttonLabel = i18n.tr("Continue")
        } else {
            p.buttonLabel = finalLabel || i18n.tr("Quit")
            p.done.connect(function() {
                continuation();
            });
        }
        PopupUtils.open(p.dialog);
    }

}
