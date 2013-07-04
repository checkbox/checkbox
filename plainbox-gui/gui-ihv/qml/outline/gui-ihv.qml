/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Andrew Haigh <andrew.haigh@cellsoftware.co.uk>
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
import GuiEngine 1.0
  
Rectangle {
    id: gui_ihv
    color: "light green"
    width: 640; height: 120

    Text{
        id: gui_ihv_title
        anchors.centerIn: parent
        text: "Plainbox IHV - prototype interface. Click here to exit Plainbox service"
    }

    GuiEngine {
        id: guiengineobj
    }

    MouseArea {
        id: gui_ihv_mouse_area
        anchors.fill: parent
        onClicked: {
            // Just call a simple Plainbox function to exit (proof of concept)
            guiengineobj.Dummy_CallPlainbox_Exit();
        }
    }
}

