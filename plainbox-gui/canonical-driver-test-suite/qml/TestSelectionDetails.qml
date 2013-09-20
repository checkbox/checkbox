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

Rectangle {
    id: rightRect
    anchors.right: parent.right
    anchors.top: parent.top

    height: detailsblock.height
    width: parent.width

    Item{
        id: detailsblock

        height: nameText.height + descriptionText.height + dependsText.height + requiresText.height + commandText.height + units.gu(1)
        width: parent.width

        TestSelectionDetailsItems{
            id: nameText
            labelName: i18n.tr("name")
            anchors.top: parent.top
            text: currentTestItem.testname
        }

        TestSelectionDetailsItems{
            id: descriptionText
            labelName: i18n.tr("description")
            anchors.top: nameText.bottom
            text: currentTestItem.description
        }

        TestSelectionDetailsItems{
            id: dependsText
            labelName: i18n.tr("depends")
            anchors.top: descriptionText.bottom
            text: currentTestItem.depends
        }

        TestSelectionDetailsItems{
            id: requiresText
            labelName: i18n.tr("requires")
            anchors.top: dependsText.bottom
            text:currentTestItem.requires
        }

        TestSelectionDetailsItems{
            id: commandText
            labelName: i18n.tr("command")
            anchors.top: requiresText.bottom
            text: currentTestItem.command
        }
    }
}
