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

#ifndef PBJSONUTILS_H
#define PBJSONUTILS_H

#include <QtDBus/QtDBus>
#include <QJsonValue>
#include <QJsonObject>
#include <QJsonDocument>
#include <QJsonArray>

class PBJsonUtils
{
public:
    static const QJsonObject QDBusObjectPathArrayToJson(const QString& key, const QList<QDBusObjectPath> opath_list);
    static const QList<QDBusObjectPath> JSONToQDBusObjectPathArray(const QString& key, const QJsonObject& object);
};

#endif // PBJSONUTILS_H
