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


Page {
    title: i18n.tr("Welcome!")

    Image {
        id: logo
        anchors {
            left: parent.left
            right: parent.right
            margins: units.gu(2)
        }
        source:"artwork/checkbox-qt-head.png"
    }



    Rectangle{
        color: "white"//Theme.palette.normal.background
        anchors {
            left: parent.left
            right: parent.right
            top: logo.bottom
            bottom: continueButton.top
            margins: units.gu(2)
        }

        TextEdit{
            id: welcometext

            anchors {
                fill: parent
                margins: units.gu(2)
            }

            // TODO load text from Plainbox
            text: "<p>Welcome to the Canonical Hardware Driver Testing.</p>
                <p></p>
                <p>This program contains automated and manual tests to help you discover issues that will arise when running your device drivers on Ubuntu.</p>
                <p></p>
                <p>This application will step the user through these tests in a predetermined order and automatically collect both system information as well as test results. It will also prompt the user for input when manual testing is required.</p>
                <p></p>
                <p>The run time for the tests is determined by which tests you decide to execute. The user will have the opportunity to customize the test run to accommodate the driver and the amount of time available for testing.</p>
                <p></p>
                <p>If you have any questions during or after completing your test run, please do not hesitate to contact your Canonical account representative.</p>
                <p></p>
                <p>To begin, simply click the Continue button below and follow the onscreen instructions.</p>
                <p></p>"

                // links below are to test if the urls are working properly.
                //<a href=\"mailto:me@here.there\">me@here.there</a>
                //<p></p>
                //<a href=\"http://www.canonical.com\">Canonical</a>"



            height: units.gu(60)
            width: units.gu(30)
            cursorVisible : true
            readOnly: true
            selectByMouse : true
            textFormat: TextEdit.AutoText
            wrapMode: TextEdit.Wrap
            color: "black"//Theme.palette.normal.foregroundText
            selectedTextColor: Theme.palette.selected.foregroundText
            selectionColor: Theme.palette.selected.foreground
            font.pixelSize: FontUtils.sizeToPixels("medium")

            onLinkActivated:  {
                console.log("onLinkActivated")
                cmdTool.exec("xdg-open", link)
            }


        }
    }




Button {
    id: continueButton
    anchors{
        left: parent.left
        right: parent.right
        bottom: parent.bottom
        margins: units.gu(2)
    }
    // TODO load text from plainbox
    text: i18n.tr("Continue")
    color: UbuntuColors.lightAubergine
    onClicked: {mainView.state = "SUITESELECTION"}
}
}
