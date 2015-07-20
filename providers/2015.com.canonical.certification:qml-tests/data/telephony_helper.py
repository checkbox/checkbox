#!/usr/bin/python3
#
# This file is part of Checkbox.
#
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

import dbus

ROOT_MANAGER = 'org.ofono.Manager'
SIM_MANAGER = 'org.ofono.SimManager'
MESSAGE_MANAGER = 'org.ofono.MessageManager'
REGISTRATION_INFO = 'org.ofono.NetworkRegistration'
RADIO_SETTINGS = 'org.ofono.RadioSettings'


class OfonoIf():
    """Provides an interface to Ofono via DBus."""
    def __init__(self):
        self._bus = dbus.SystemBus()
        # attempt to get the root manager to confirm Ofono is running
        self._get_manager()

    def _get_manager(self):
        """Get the root interface of Ofono."""
        root = self._bus.get_object('org.ofono', '/')
        return dbus.Interface(root, ROOT_MANAGER)

    def _get_sim_manager(self, modem_path):
        """Get ofono interface for SIM operations."""
        modem = self._bus.get_object('org.ofono', modem_path)
        return dbus.Interface(modem, SIM_MANAGER)

    def _get_message_manager(self, modem_path):
        """Get ofono interface for Message operations."""
        modem = self._bus.get_object('org.ofono', modem_path)
        return dbus.Interface(modem, MESSAGE_MANAGER)

    def _get_registration_info(self, modem_path):
        """Get the network registration interface from ofono."""
        modem = self._bus.get_object('org.ofono', modem_path)
        return dbus.Interface(modem, REGISTRATION_INFO)

    def _get_radio_settings(self, modem_path):
        """Get ofono interface for Radio capabilities."""
        modem = self._bus.get_object('org.ofono', modem_path)
        return dbus.Interface(modem, RADIO_SETTINGS)

    def _get_modem_properties(self, modem_path):
        """Get top level properties related to specified modem."""
        manager = self._get_manager()
        modems = manager.GetModems()
        for path, properties in modems:
            if path == modem_path:
                return properties

    def get_modems(self):
        """Return a list of modems identified by their path name."""
        paths = []
        manager = self._get_manager()
        modems = manager.GetModems()
        for path, _ in modems:
            paths.append({'pathName': str(path)})
        return paths

    def get_imei(self, modem_path):
        """Return the IMEI of the specified modem."""
        modem_props = self._get_modem_properties(modem_path)
        return modem_props['Serial']

    def get_imsi(self, modem_path):
        """Return the IMSI of the SIM connected to the specified modem."""
        sim_manager = self._get_sim_manager(modem_path)
        return(sim_manager.GetProperties()['SubscriberIdentity'])

    def send_sms(self, modem_path, recipient, text):
        """Send a SMS message to a recipient on the specified modem."""
        mm = self._get_message_manager(modem_path)
        mm.SetProperty("UseDeliveryReports", dbus.Boolean(1))
        result = mm.SendMessage(recipient, text)
        return result

    def is_pin_locked(self, modem_path):
        """
        Determine if the SIM attached to specified modem has a
        PIN lock enabled.
        """
        sim_manager = self._get_sim_manager(modem_path)
        locked_pins = sim_manager.GetProperties()['LockedPins']
        return 'pin' in locked_pins

    def is_sim_present(self, modem_path):
        """Deterimine if there is a SIM attached to specified modem."""
        sim_manager = self._get_sim_manager(modem_path)
        return bool(sim_manager.GetProperties()['Present'])

    def get_network_name(self, modem_path):
        """
        Get the network that the SIM attached to the specified modem is
        currently registered on.
        """
        net_info = self._get_registration_info(modem_path)
        return net_info.GetProperties()['Name']

    def get_numbers(self, modem_path):
        """Return phone numbers associated with SIM on modem specified."""
        sim_manager = self._get_sim_manager(modem_path)
        return(sim_manager.GetProperties()['SubscriberNumbers'])

    def get_rats(self, modem_path):
        """Return list of RATs supported on specified modem."""
        radio_settings = self._get_radio_settings(modem_path)
        return radio_settings.GetProperties()['ModemTechnologies']
