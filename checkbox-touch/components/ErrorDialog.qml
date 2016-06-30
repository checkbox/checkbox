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
import QtQuick 2.0
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 0.1

/*! \brief Error message popup.
    \inherits Item

    This component is an error reporting dialog.
    To use this component call showError() from ErrorLogic.js
    Typical usage is:
        import "components/ErrorLogic.js" as ErrorLogic
        (...)
        ErrorLogic.showError(mainView, "There was something wrong", Qt.quit)
*/

Item {
    id: errorDialog
    /*!
        Gets signalled when user taps on the button
     */
    signal done()

    property string buttonLabel: i18n.tr("Um, OK")

    /*!
      `dialog` alias helps use the component containing dialog
    */
    property alias dialog: dialogComponent

    /*!
      Text to display in the error dialog
    */
    property string errorMessage: i18n.tr("Error encountered")


    Component {
        id: dialogComponent

        Dialog {
            id: dlg
            title: i18n.tr("Error encountered")

            Label {
                text: errorMessage
                width: parent.width
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            }

            Button {
                id: button
                text: errorDialog.buttonLabel
                color: UbuntuColors.red
                onClicked: {
                    done();
                    PopupUtils.close(dlg);
                }
            }
        }
    }
}
