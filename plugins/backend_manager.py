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
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

from checkbox.lib.environ import add_variable, append_path

from checkbox.job import Job, PASS
from checkbox.properties import Int, String
from checkbox.user_interface import UserInterface


class PermissionDeniedByPolicy(dbus.DBusException):
    _dbus_error_name = "com.ubuntu.checkbox.PermissionDeniedByPolicy"


class UnknownJobException(dbus.DBusException):
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
        self.jobs = []

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
             ("report-suite", self.report_suite),
             ("report-test", self.report_test),
             ("run", self.run)]:
            self._manager.reactor.call_on(rt, rh)

    @dbus.service.method(DBUS_INTERFACE_NAME,
        in_signature="ss", out_signature="as", sender_keyword="sender",
        connection_keyword="conn")
    def get_job_result(self, command, user, sender=None, conn=None):
        self.loop = False
        for job in self.jobs:
            if job.get("command") == command:
                break
        else:
            raise UnknownJobException, \
                "Job not found for command: %s" % command

        add_variable("SUDO_USER", user)
        job = Job(job["command"], job.get("environ"),
            job.get("timeout"), job.get("user"))
        (status, data, duration) = job.execute()
        if status == PASS:
            self._manager.reactor.fire("message-string", data)

        return (status, data, str(duration))

    def report_suite(self, suite):
        self.jobs.append(suite)

    def report_test(self, test):
        self.jobs.append(test)

    def run(self):
        interface = UserInterface("System Testing Backend")
        self._manager.reactor.fire("prompt-gather", interface)
        self._manager.reactor.fire("prompt-suites", interface)

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


factory = BackendManager
