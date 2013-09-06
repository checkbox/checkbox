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


Dialog {
    id: dialog

    title: i18n.tr("Log Viewer")
    text: i18n.tr("")

    property alias logText: logtext.text
//    property alias showTroubleShootingLink: troubleButton.visible
    property alias logHeight: flick.height

    property string jobPath: "Not Set"

    // Re-insert this for other/future versions of the GUI
//    property alias showTroubleShootingLink: troubleButton.visible
//
//    Button {
//        id: troubleButton
//        text: i18n.tr("Trouble Shooting")
//        color: UbuntuColors.orange
//        onClicked: {
//            // TODO put in real url!!
//            cmdTool.exec("xdg-open", "https://wiki.ubuntu.com/Testing/Automation/Checkbox/");
//        }
//    }

    Flickable {
        id: flick

        width: logtext.width;
        height: units.gu(50)
        contentWidth: logtext.paintedWidth
        contentHeight: logtext.paintedHeight
        clip: true

        function ensureVisible(r)
        {
            if (contentX >= r.x)
                contentX = r.x;
            else if (contentX+width <= r.x+r.width)
                contentX = r.x+r.width-width;
            if (contentY >= r.y)
                contentY = r.y;
            else if (contentY+height <= r.y+r.height)
                contentY = r.y+r.height-height;
        }

        TextEdit{
            id: logtext
            text: "Load this up with text\nhere's a url: <a href=\"http://www.ubuntu.com\">Visit Ubuntu</a>
                even more even more \n even more even more \n even more even more \n
                even more even more \n even more even more \n even more even more \n"

            //height: units.gu(60)
            width: units.gu(30)
            cursorVisible : true
            readOnly: true
            selectByMouse : true
            textFormat: TextEdit.RichText
            wrapMode: TextEdit.Wrap
            focus: true
            color: Theme.palette.normal.foregroundText
            selectedTextColor: Theme.palette.selected.foregroundText
            selectionColor: Theme.palette.selected.foreground
            font.pixelSize: FontUtils.sizeToPixels("medium")

            onCursorRectangleChanged: flick.ensureVisible(cursorRectangle)

            Component.onCompleted: {
               // text = io_log;

                // get the log info from guiengine
                text = guiEngine.GetIOLog(jobPath);
            }

            onLinkActivated: {
                cmdTool.exec("xdg-open", link)
            }
        }
    }

    Button {
        id: doneButton
        text: i18n.tr("Done")
        color: UbuntuColors.warmGrey
        onClicked: PopupUtils.close(dialog)
    }

}
