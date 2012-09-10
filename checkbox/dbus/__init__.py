# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
"""
checkbox.dbus
=============

Utility modules for working with various things accessible over dbus
"""

import logging

from dbus import SystemBus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject


def connect_to_system_bus():
    """
    Connect to the system bus properly.

    Returns a tuple (system_bus, loop) where loop is a GObject.MainLoop
    instance. The loop is there so that you can listen to signals.
    """
    # We'll need an event loop to observe signals. We will need the instance
    # later below so let's keep it. Note that we're not passing it directly
    # below as DBus needs specific API. The DBusGMainLoop class that we
    # instantiate and pass is going to work with this instance transparently.
    #
    # NOTE: DBus tutorial suggests that we should create the loop _before_
    # connecting to the bus.
    logging.debug("Setting up glib-based event loop")
    loop = GObject.MainLoop()
    # Let's get the system bus object. We need that to access UDisks2 object
    logging.debug("Connecting to DBus system bus")
    system_bus = SystemBus(mainloop=DBusGMainLoop())
    return system_bus, loop
