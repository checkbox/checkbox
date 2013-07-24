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

    TextArea{
        id: logtext
        text: "Load this up with text"
        Text { font.pointSize: 12; }
        //color: "green"
        height: units.gu(40)
    }


    Button {
        id: doneButton
        text: i18n.tr("Done")
        color: UbuntuColors.warmGrey
        onClicked: {
            PopupUtils.close(dialog)
        }
    }
}








