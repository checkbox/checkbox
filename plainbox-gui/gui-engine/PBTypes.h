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

#ifndef PB_TYPES_H
#define PB_TYPES_H

/* Decoding for the org.freedesktop.Dbus.ObjectManager
 *
 * Structs useful to the GUI for extraction and display purposes
 *
 * Ultimately we must decode this DBus Signature
 * "a{oa{sa{sv}}}
 *
 * So, starting with the inner most, we can say that:
 *   a{sv} = QString, QDBusVariant = om_smalldict
 *
 * Then, we will have
 *
 * a{sa{sv}} = QMap<QString,QVariantMap> = om_innerdict
 *
 * Finally, we want this:
 *
 * a{oa{sa{sv}}} = QMap<QString,innerdict> = outerdict
 */
typedef QMap<QString,QDBusVariant> om_smalldict;
typedef QMap<QString,om_smalldict> om_innerdict;
typedef QMap<QDBusObjectPath,om_innerdict> om_outerdict;

// now register these metatypes
Q_DECLARE_METATYPE(om_smalldict);
Q_DECLARE_METATYPE(om_innerdict);
Q_DECLARE_METATYPE(om_outerdict);

/* We need a new metatype for passing to plainbox CreateSession()
 *
 * Basically, an array of DBus Object Paths
 */
typedef QList<QDBusObjectPath> opath_array_t;

Q_DECLARE_METATYPE(opath_array_t);

/* We would like a metatype to represent returned job_state_map dictionary */
typedef QMap<QString,QDBusObjectPath> jsm_t;

Q_DECLARE_METATYPE(jsm_t);

#endif // PB_TYPES_H
