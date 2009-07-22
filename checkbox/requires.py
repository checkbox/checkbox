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
from checkbox.lib.iterator import IteratorContain, IteratorExclude

from checkbox.registry import registry_eval_recursive


class RequiresIterator(IteratorContain):

    def __init__(self, elements=[], registry=None):
        self._registry = registry
        self._requires_mask = {}

        iterator = IteratorExclude(elements,
            self._requires_exclude_func,
            self._requires_exclude_func)

        super(RequiresIterator, self).__init__(iterator)

    def _requires_exclude_func(self, element):
        """IteratorExclude function which removes element when the
           requires field contains a False value."""
        from checkbox.job import UNSUPPORTED

        if self._registry:
            mask = []
            for require in element.get("requires", []):
                result = registry_eval_recursive(self._registry, require)
                mask.append(bool(result))

            if False in mask:
                element["status"] = UNSUPPORTED
                element["data"] = "Test requirements not met."
                return True

        return False
