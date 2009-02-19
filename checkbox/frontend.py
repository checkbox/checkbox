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
import os
import pwd

DBUS_INTERFACE_NAME = "com.ubuntu.checkbox"

DBUS_BUS_NAME = "com.ubuntu.checkbox"


class Frontend(object):

    globals = {}

    def __init__(self, function, method):
        self._function = function
        self._method = method

    def __get__(self, instance, cls=None):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        if self.user == "root":
            return self._function(self._instance, *args, **kwargs)
        else:
            return getattr(self, self._method)(*args, **kwargs)

    @property
    def user(self):
        uid = os.getuid()
        user = pwd.getpwuid(uid)[0]
        return user

    @property
    def client(self):
        import dbus
        import dbus.mainloop.glib

        if "client" in self.globals:
            return self.globals["client"]
        else:
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()
            obj = bus.get_object(DBUS_BUS_NAME, '/checkbox')
            client = dbus.Interface(obj, DBUS_INTERFACE_NAME)

            return self.globals.setdefault("client", client)

    def get_test_result(self, *args, **kwargs):
        from checkbox.test import TestResult

        test = self._instance.test
        if test.user:
            (status, data, duration) = self.client.get_test_result(test.suite, test.name)
            return TestResult(self.test, status, data, float(duration))
        else:
            return self._function(self._instance, *args, **kwargs)

    def get_test_description(self, *args, **kwargs):
        test = self._instance.test
        if test.user:
            return self.client.get_test_description(test.suite, test.name)
        else:
            return self._function(self._instance, *args, **kwargs)

    def get_registry(self, *args, **kwargs):
        if self._instance.user:
            return self.client.get_registry(self._instance.__module__)
        else:
            return self._function(self._instance, *args, **kwargs)


def frontend(method):
    def wrapper(func):
        return Frontend(func, method)
    return wrapper
