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

#ifndef TESTITEMMODEL_H
#define TESTITEMMODEL_H

#include <QObject>
#include "testitem.h"
#include "../gui-engine/gui-engine.h"

// Factory class to create or update a TestItem Model
class TestItemModel : public QObject
{
    Q_OBJECT

public:
    TestItemModel() {};
    ~TestItemModel() {};

public slots:
    ListModel* CreateTestListModel(ListModel* model=NULL);

    // We should obtain a list of desired jobs here
    QList<QDBusObjectPath> GetSelectedRealJobs(ListModel* model=NULL);
};

#endif // TESTITEMMODEL_H
