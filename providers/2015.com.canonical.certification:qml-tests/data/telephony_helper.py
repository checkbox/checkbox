#!/usr/bin/python3

import logging

import dbus
import pyotherside

_logger = logging.getLogger('checkbox.touch')


def get_modems():
    """Return a list of modems identified by their path name"""
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
    """Use MessageManager to send a SMS message to a recipient"""
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
