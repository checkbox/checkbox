/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
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
import Ubuntu.Components.Popups 1.3

/*! \brief Comment addition dialog.
    \inherits Item

    This component is a prompt for user comments regarding test.
*/

Item {
    id: commentsDialog
    /*!
      `dialog` alias shortens the code that launches this dialog
     */
    property alias dialog: component

    /*!
      Use this property to populate the textArea that the user will write in.
      It's useful when the comment is only updated - you can use the previous
      input.
     */
    property var commentDefaultText: ""

    /*!
      Gets signalled when user taps 'done'
     */
    signal commentAdded(string comment)

    Component {
        id: component
        Dialog {
            id: dialog
            title: i18n.tr("Add comment")

            modal: true

            TextArea {
                id: commentText
                objectName: "commentText"
            }

            Button {
                id: doneButton
                objectName: "doneButton"
                text: i18n.tr("Done")
                color: UbuntuColors.green
                onClicked: {
                    PopupUtils.close(dialog);
                    commentAdded(commentText.text);
                    commentText.text = "";
                }
            }

            Component.onCompleted: {
                commentText.text = commentDefaultText
                commentText.cursorPosition = commentText.text.length;
                commentText.forceActiveFocus();
            }
        }
    }
}

