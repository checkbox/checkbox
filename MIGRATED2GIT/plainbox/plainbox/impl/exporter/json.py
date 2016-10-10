# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
:mod:`plainbox.impl.exporter.json` -- JSON exporter
===================================================

.. warning::
    THIS MODULE DOES NOT HAVE STABLE PUBLIC API
"""

import json

from plainbox.impl.exporter import SessionStateExporterBase


class JSONSessionStateExporter(SessionStateExporterBase):
    """
    Session state exporter creating JSON documents
    """

    OPTION_MACHINE_JSON = 'machine-json'

    SUPPORTED_OPTION_LIST = (
        SessionStateExporterBase.SUPPORTED_OPTION_LIST + (
            OPTION_MACHINE_JSON,))

    def dump(self, data, stream):
        if self.OPTION_MACHINE_JSON in self._option_list:
            encoder = json.JSONEncoder(
                ensure_ascii=False,
                indent=None,
                separators=(',', ':'))
        else:
            encoder = json.JSONEncoder(
                ensure_ascii=False,
                indent=4)
        for chunk in encoder.iterencode(data):
            stream.write(chunk.encode('UTF-8'))
