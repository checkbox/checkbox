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


ListModel {
    id: suiteModel
    ListElement { name: "Orange"; type: "Fruit"}
    ListElement { name: "Apple"; type: "Fruit" }
    ListElement { name: "Tomato"; type: "Fruit" }
    ListElement { name: "Carrot"; type: "Vegetable" }
    ListElement { name: "Potato"; type: "Vegetable" }
}
