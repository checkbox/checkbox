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

#ifndef WHITELISTMODELFACTORY_H
#define WHITELISTMODELFACTORY_H

#include <QObject>
#include "whitelistitem.h"
#include "../gui-engine/gui-engine.h"

// Factory class to create or update a TestItem Model
class WhiteListModelFactory : public QObject
{
    Q_OBJECT

public:
    WhiteListModelFactory() {};
    ~WhiteListModelFactory() {};

public slots:
    ListModel* CreateWhiteListModel(ListModel* model=NULL);
};

#endif // WHITELISTMODELFACTORY_H
