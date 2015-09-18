/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
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

/*! \brief Action component for skipping a test. */

import QtQuick 2.0
import Ubuntu.Components 1.1
import Ubuntu.Components.Popups 0.1
import "../ConfirmationLogic.js" as ConfirmationLogic

Action {
    id: skipAction
    objectName: "skip"
    iconName: "media-seek-forward"
    text: i18n.tr("Skip")
    onTriggered: {
        var confirmationOptions = {
            question : i18n.tr("Do you really want to skip this test?"),
            remember : true,
        }
        ConfirmationLogic.confirmRequest(mainView,
            confirmationOptions, function(res) {
                var currentTest = test;
                if (res) {
                    commentsDialog.commentDefaultText = test["comments"] || "";
                    var handler = function(comment) {
                        currentTest["comments"] = comment;
                        currentTest["outcome"] = "skip";
                        commentsDialog.commentAdded.disconnect(handler);
                        testDone(currentTest);
                    };
                    commentsDialog.commentAdded.connect(handler);
                    PopupUtils.open(commentsDialog.dialogComponent);
                }
        });
    }
}
