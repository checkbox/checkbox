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

import telephony_helper
import pyotherside


def get_modems():
    """Return a list of modems identified by their path name."""
    paths = []
    ofonoIf = telephony_helper.OfonoIf()
    modems = ofonoIf.get_modems()
    for path, _ in modems:
        paths.append({'pathName': str(path)})
    pyotherside.send('got-modem-list', paths)
    return


def send_sms(modem_path, recipient, text):
    """Use MessageManager to send a SMS message to a recipient."""
    ofonoIf = telephony_helper.OfonoIf()
    result = ofonoIf.send_sms(modem_path, recipient, text)
    print(result)
    return
