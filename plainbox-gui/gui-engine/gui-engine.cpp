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
 
#include "gui-engine.h"
#include <QtDBus/QtDBus>
#include <QDebug>

void GuiEnginePlugin::registerTypes(const char *uri)
{
    // register our classes
    qmlRegisterType<GuiEngine>(uri,1,0,"GuiEngine");
}

GuiEngine::GuiEngine( QObject*parent ) : QObject(parent)
{

}

// Dummy_CallPlainbox_Exit is for prototyping purposes and will eventually be removed
void GuiEngine::Dummy_CallPlainbox_Exit()
{
    // Connect to Dbus Session Bus
    if (!QDBusConnection::sessionBus().isConnected()) {
        fprintf(stderr, "Cannot connect to the D-Bus session bus.\n");
        return;
    }

    // Hard-coded names for Plainbox session, service and function
    QDBusInterface iface("com.canonical.certification.PlainBox", \
    	"/plainbox/service", "com.canonical.certification.PlainBox", \
    	QDBusConnection::sessionBus());
    if (iface.isValid()) {
        QDBusReply<QString> reply = iface.call("Exit");
        if (reply.isValid()) {
            printf("Reply was: %s\n", qPrintable(reply.value()));
            return;
        } else {
            fprintf(stderr,"Invalid reply, but not important for now. \
	            This code shows where to collect results from DBus calls");
        }
        return;
    }

    fprintf(stderr, "%s\n", \
    	qPrintable(QDBusConnection::sessionBus().lastError().message()));
}

// End of file - gui-engine.cpp



