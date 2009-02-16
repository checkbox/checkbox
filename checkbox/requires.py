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
from checkbox.lib.cache import cache

from checkbox.registry import registry_eval_recursive


class Requires(object):

    def __init__(self, registry, source):
        self._registry = registry
        self._source = source
        self._mask = [False]

    def __str__(self):
        return self.get_source() or ""

    @cache
    def get_values(self):
        if self._source is None:
            self._mask = [True]
            return []

        return registry_eval_recursive(self._registry,
            self._source, self._mask)

    def get_packages(self):
        packages = []
        values = self.get_values()
        for value in values:
            if value.__class__.__name__ == "PackageRegistry":
                packages.append(value)

        return packages

    def get_devices(self):
        devices = []
        values = self.get_values()
        for value in values:
            if value.__class__.__name__ == "DeviceRegistry":
                devices.append(value)

        return devices

    def get_source(self):
        return self._source

    def get_mask(self):
        self.get_values()
        return self._mask
