#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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

import logging

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

from checkbox.lib.environ import append_path

from checkbox.properties import Int, String


class PermissionDeniedByPolicy(dbus.DBusException):
    _dbus_error_name = "com.ubuntu.checkbox.PermissionDeniedByPolicy"


class UnknownRegistryException(dbus.DBusException):
    _dbus_error_name = 'com.ubuntu.DeviceDriver.InvalidDriverDBException'

class UnknownTestException(dbus.DBusException):
    _dbus_error_name = 'com.ubuntu.DeviceDriver.InvalidDriverDBException'


class BackendManager(dbus.service.Object):

    DBUS_INTERFACE_NAME = "com.ubuntu.checkbox"

    DBUS_BUS_NAME = "com.ubuntu.checkbox"

    timeout = Int(default=600)
    path = String(default="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")

    def __init__(self):
        self.dbus_info = None
        self.polkit = None
        self.loop = False
        self.tests = {}

    def __repr__(self):
        return "<BackendManager>"

    def register(self, manager):
        import dbus.mainloop.glib
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.dbus_name = dbus.service.BusName(self.DBUS_BUS_NAME, self.bus)

        # Set environment which has been reset by dbus
        for path in self.path.split(":"):
            append_path(path)

        self._manager = manager
        for (rt, rh) in [
             ("test-.*", self.test_all),
             ("run", self.run)]:
            self._manager.reactor.call_on(rt, rh)

    @dbus.service.method(DBUS_INTERFACE_NAME,
        in_signature="s", out_signature="s", sender_keyword="sender",
        connection_keyword="conn")
    def get_registry(self, name, sender=None, conn=None):
        self._check_polkit_privilege(sender, conn, "com.ubuntu.checkbox.info")
        if name not in self._manager.registry:
            raise UnknownRegistryException, "Registry not found: %s" % name

        return str(self._manager.registry[name])

    @dbus.service.method(DBUS_INTERFACE_NAME,
        in_signature="ss", out_signature="as", sender_keyword="sender",
        connection_keyword="conn")
    def get_test_result(self, suite, name, sender=None, conn=None):
        self._check_polkit_privilege(sender, conn, "com.ubuntu.checkbox.test")
        if (suite, name) not in self.tests:
            raise UnknownTestException, \
                "Suite/test not found: %s/%s" % (suite, name)

        test = self.tests[(suite, name)]
        result = test.command()
        return (result.status, result.data, str(result.duration))

    @dbus.service.method(DBUS_INTERFACE_NAME,
        in_signature="ss", out_signature="s", sender_keyword="sender",
        connection_keyword="conn")
    def get_test_description(self, suite, name, sender=None, conn=None):
        self._check_polkit_privilege(sender, conn, "com.ubuntu.checkbox.test")
        if (suite, name) not in self.tests:
            raise UnknownTestException, \
                "Suite/test not found: %s/%s" % (suite, name)

        test = self.tests[(suite, name)]
        return test.description()

    def test_all(self, test):
        self.tests[(test.suite, test.name)] = test

    def run(self):
        self._manager.reactor.fire("gather")

        # Delay instantiating the service after register
        dbus.service.Object.__init__(self, self.bus, "/checkbox")
        main_loop = gobject.MainLoop()
        self.loop = False
        if self.timeout:
            def _t():
                main_loop.quit()
                return True
            gobject.timeout_add(self.timeout * 1000, _t)

        # run until we time out
        while not self.loop:
            if self.timeout:
                self.loop = True
            main_loop.run()

    def _check_polkit_privilege(self, sender, conn, privilege):
        """Verify that sender has a given PolicyKit privilege.

        sender is the sender's (private) D-BUS name, such as ":1:42"
        (sender_keyword in @dbus.service.methods). conn is
        the dbus.Connection object (connection_keyword in
        @dbus.service.methods). privilege is the PolicyKit privilege string.

        This method returns if the caller is privileged, and otherwise throws a
        PermissionDeniedByPolicy exception.
        """
        if sender is None and conn is None:
            # called locally, not through D-BUS
            return

        # get peer PID
        if self.dbus_info is None:
            self.dbus_info = dbus.Interface(conn.get_object("org.freedesktop.DBus",
                "/org/freedesktop/DBus/Bus", False), "org.freedesktop.DBus")
        pid = self.dbus_info.GetConnectionUnixProcessID(sender)

        # query PolicyKit
        if self.polkit is None:
            self.polkit = dbus.Interface(dbus.SystemBus().get_object(
                "org.freedesktop.PolicyKit", "/", False),
                "org.freedesktop.PolicyKit")
        try:
            res = self.polkit.IsProcessAuthorized(privilege, pid, True)
        except dbus.DBusException, e:
            if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                # polkitd timed out, connect again
                self.polkit = None
                return self._check_polkit_privilege(sender, conn, privilege)
            else:
                raise

        if res != "yes":
            logging.debug("_check_polkit_privilege: sender %s "
                "on connection %s pid %i requested %s: %s",
                sender, conn, pid, privilege, res)
            raise PermissionDeniedByPolicy(privilege + " " + res)


factory = BackendManager
