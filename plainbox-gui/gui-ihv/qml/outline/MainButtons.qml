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



Row {
    id: buttons
    state: "SELECTION"

    signal actionChanged(string actionState)

    width: parent.width - units.gu(20)
    spacing: (parent.width - (140*3))/5  // width - buttons / 5 spaces

    Button {
         id:selectionButton
         text: i18n.tr("selection")
         width:  units.gu(16)
         onClicked: {
             buttons.state = "SELECTION";
             buttons.actionChanged(buttons.state);
         }
    }
    Button {
         id: runButton
         text: i18n.tr("run")
         width:  units.gu(16)
         onClicked:{
             buttons.state = "RUN";
             buttons.actionChanged(buttons.state);
         }

    }
    Button {
        id: resultsButton
        text: i18n.tr("results")
        width: units.gu(16)
        onClicked:{
            buttons.state = "RESULTS"
            buttons.actionChanged(buttons.state);
        }
    }

     states: [
         State {
             name: "SELECTION"
             PropertyChanges { target: selectionButton; color: UbuntuColors.orange}
             PropertyChanges { target: runButton; color: UbuntuColors.warmGrey}
             PropertyChanges { target: resultsButton; color: UbuntuColors.warmGrey}
         },
         State {
             name: "RUN"
             PropertyChanges { target: selectionButton; color: UbuntuColors.warmGrey}
             PropertyChanges { target: runButton; color: UbuntuColors.orange}
             PropertyChanges { target: resultsButton; color: UbuntuColors.warmGrey}

         },
         State {
             name: "RESULTS"
             PropertyChanges { target: selectionButton; color: UbuntuColors.warmGrey}
             PropertyChanges { target: runButton; color: UbuntuColors.warmGrey}
             PropertyChanges { target: resultsButton; color: UbuntuColors.orange}
         }

     ]

}
