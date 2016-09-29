/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
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

/*! \brief Page with version and copyright information

    This page shows version information and contents of AUTHORS file located in top chekckbox-touch directory
*/
import QtQuick 2.0
import Ubuntu.Components 1.3
import QtQuick.Layouts 1.1

Page {
    id: aboutPage
    property var versionInfo : {
        "converged_app" : "0.0",
        "plainbox" : "0.0"
    }

    onVersionInfoChanged: body.generateVersionText()

    header: PageHeader {
       title: i18n.tr("About")
    }

    ColumnLayout {
        spacing: units.gu(3)
        anchors {
            top: header.bottom
            bottom: aboutPage.bottom
            right: aboutPage.right
            left: aboutPage.left
            topMargin: units.gu(3)
            bottomMargin: units.gu(3)
            leftMargin: units.gu(1)
            rightMargin: units.gu(1)
        }

        Flickable {
            id: flickable
            Layout.fillHeight: true
            Layout.fillWidth: true
            contentHeight: body.height
            contentWidth: body.width
            flickableDirection: Flickable.VerticalFlick
            clip: true

            Text {
                id: body
                Layout.fillHeight: true
                Layout.fillWidth: true
                width: flickable.width
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                textFormat: Text.RichText
                text: versionString + copyrightString

                //custom codde for generating body content
                property string versionString: "";
                property string copyrightString: "";
                function generateVersionText() {
                    body.versionString = "<center><h1><b>Checkbox Converged</b></h1><p>" +
                        i18n.tr("version: ") + aboutPage.versionInfo["converged_app"] + "<br/>" +
                        i18n.tr("Plainbox version: ") + aboutPage.versionInfo["plainbox"] + "<br/></center>";
                }
            }
        }

        Button {
            text: i18n.tr("Close")
            Layout.fillWidth: true
            onTriggered: pageStack.pop()
            color: UbuntuColors.green
        }
    }

    Component.onCompleted: {
        var request = new XMLHttpRequest()
        request.open('GET', '../AUTHORS')
        request.onreadystatechange = function(event) {
            if (request.readyState == XMLHttpRequest.DONE) {
                body.copyrightString = request.responseText;
            }
        }
        request.send()
        body.generateVersionText();
    }
}

