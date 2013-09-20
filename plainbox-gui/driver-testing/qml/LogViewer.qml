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


Popover {
    id: logview

    property alias logText: logtext.text
    property alias logHeight: flick.height

    property string jobName: "Not Set"
    property string jobPath: "Not Set"
    contentWidth: parent.width - units.gu(30)

    Column {
        Row {
            Label {
                text: jobName
                fontSize: "large"
            }
        }
        Row {
            Flickable {
                id: flick
                width: logview.width;
                height: units.gu(50)

                contentWidth: logtext.paintedWidth
                contentHeight: logtext.paintedHeight
                clip: true

                TextArea {
                    id: logtext
                    text: "Load this up with text\nhere's a url: <a href=\"http://www.ubuntu.com\">Visit Ubuntu</a>
                           even more even more \n even more even more \n even more even more \n
                           even more even more \n even more even more \n even more even more \n"

                    height: parent.height
                    width: parent.width
                    cursorVisible : true
                    readOnly: true
                    selectByMouse : true
                    textFormat: TextEdit.RichText
                    wrapMode: TextEdit.NoWrap
                    focus: true
                    font.pixelSize: FontUtils.sizeToPixels("medium")
                    color: "white"
                    style: Rectangle { color: "black" }

                    Component.onCompleted: {
                        // get the log info from guiengine
                        text = "<code>" + guiEngine.GetIOLog(jobPath) + "</code>";
                    }
                }
            }
        }
    }
}
