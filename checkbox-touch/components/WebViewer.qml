/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
 *
 * Authors:
 * - Chris Wayne <cwayne@ubuntu.com>
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
import Ubuntu.Web 0.2
import Ubuntu.Components 1.3


Page {
    title: i18n.tr("Test Report")
    visible: false
    property var uri

    objectName: "webviewerpage"

	WebView {
		id: wv
		anchors.fill: parent
		url: ""
        contextualActions: ActionList {
            Action {
                text: i18n.tr("Open in a browser")
                onTriggered: Qt.openUrlExternally(wv.url)
            }
            Action {
                text: i18n.tr("Go back one page")
                onTriggered: wv.goBack()
            }
            Action {
                text: i18n.tr("Reload current page")
                onTriggered: wv.reload()
            }
        }
	}

	onUriChanged: {
		wv.url = uri;
		wv.reload();
	}
}
