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
import "."





Page {
    title: i18n.tr("Run Manager")

    Item {
        id: filler
        height: units.gu(0)
    }



    RunManagerListView {
        id: testsuitelist

        width: parent.width - units.gu(4)

        anchors{
            horizontalCenter: parent.horizontalCenter
            top: filler.bottom
            bottom: runbuttons.top
            margins: units.gu(2)
        }
    }


    RunManagerButtons {
        id: runbuttons

        anchors{
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
            margins: units.gu(2)
        }

        onCancel:{
            console.log("On Cancel")
        }

        onPauseTest: {
            console.log("Pause")
        }
    }

}
