/*
 * This file is part of Checkbox
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

#include "WhiteListModelFactory.h"

ListModel* WhiteListModelFactory::CreateWhiteListModel(ListModel *model)
{
    qDebug("WhiteListModelFactory::CreateWhiteListModel()");

    // We can create OR update the model
    if (model==NULL) {
        qDebug("Creating fresh WhiteListItem");
        model = new ListModel(new WhiteListItem, qApp);
        if (model == NULL) {
            qDebug("Cannot allocate memory to our testitemmodel");
        }

    } else {
        qDebug("Recreating TestItemModel");
        model->clear();
    }

    const QString engname("");

    GuiEngine* myengine = qApp->findChild<GuiEngine*>(engname);
    if(myengine == NULL) {
        qDebug("Cant find guiengine object");

        // NB: Model will be empty at this point
        return model;
    }

    QMap<QDBusObjectPath,QString> paths_and_names = \
            myengine->GetWhiteListPathsAndNames();

    QMap<QDBusObjectPath,QString>::const_iterator iter = paths_and_names.begin();

    while(iter != paths_and_names.end() ) {

        qDebug() << iter.key().path();

        qDebug() << " Name: " << iter.value();

        model->appendRow(new WhiteListItem(iter.value(), \
                                           iter.key().path(), \
                                           model));
        iter++;
    }

    qDebug("WhiteListModelFactory::CreateWhiteListModel() - Done");

    return model;
}
