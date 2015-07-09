#!/usr/bin/python3
# Copyright 2015 Canonical Ltd.
# Written by:
#   Jonathan Cave <jonathan.cave@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

import dbus
import pyotherside

_logger = logging.getLogger('checkbox.touch')


def get_modems():
    """Return a list of modems identified by their path name."""
    paths = []
    bus = dbus.SystemBus()
    try:
        manager = dbus.Interface(bus.get_object('org.ofono', '/'),
                                 'org.ofono.Manager')
    except dbus.exceptions.DBusException as e:
        _logger.error("Service org.ofono not found on DBus: {}".format(e))
        return

    modems = manager.GetModems()

    for path, properties in modems:
        paths.append({'pathName': str(path)})

    pyotherside.send('got-modem-list', paths)
    return


def send_sms(modem_path, recipient, text):
    """Use MessageManager to send a SMS message to a recipient."""
    bus = dbus.SystemBus()
    try:
        mm = dbus.Interface(bus.get_object('org.ofono', modem_path),
                            'org.ofono.MessageManager')
    except dbus.exceptions.DBusException as e:
        _logger.error("Service org.ofono not found on DBus: {}".format(e))
        return

    mm.SetProperty("UseDeliveryReports", dbus.Boolean(1))
    result = mm.SendMessage(recipient, text)

    print(result)

if __name__ == "__main__":
    print(get_modems())
