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

#include "PBJsonUtils.h"

// Key should be a meaningful name, ideally the member name
const QJsonObject PBJsonUtils::QDBusObjectPathArrayToJson(\
        const QString& key, \
        const QList<QDBusObjectPath> opath_list)
{
    QJsonObject object;
    QJsonArray jsonarray;
    if ( opath_list.count() ) {
        for (int i=0; i < opath_list.count();i++) {
            QString path = opath_list.at(i).path();
            jsonarray.append(path);
        }
    }
    QJsonValue value(jsonarray);
    object.insert(key,value);
    return object;
}

// Key should be a meaningful name, ideally the member name
const QList<QDBusObjectPath> PBJsonUtils::JSONToQDBusObjectPathArray(\
        const QString& key, \
        const QJsonObject& object)
{
    QJsonArray jsonarray;
    QJsonValue value;
    value = object.find(key).value();
    jsonarray = value.toArray();
    QList<QDBusObjectPath> opath_list;
    for(int i=0; i<jsonarray.count(); i++) {
        QString path = jsonarray.at(i).toString();
        QDBusObjectPath opath(path);
        opath_list.append(opath);
    }
    return opath_list;
}
