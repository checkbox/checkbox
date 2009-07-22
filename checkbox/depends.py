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
from checkbox.lib.iterator import (IteratorContain, IteratorExclude,
    IteratorPreRepeat)
from checkbox.lib.resolver import Resolver


class DependsIterator(IteratorContain):

    def __init__(self, elements=[], compare=None):
        from checkbox.job import UNINITIATED

        self._dependent_next = []
        self._dependent_prev = []
        self._dependent_status = UNINITIATED

        if compare is None:
            compare = lambda a, b: cmp(a["name"], b["name"])

        # Resolve dependencies
        resolver = Resolver(compare=compare, key=lambda e: e["name"])
        element_dict = dict((e["name"], e) for e in elements)
        for element in elements:
            depends = element.get("depends", "").split()
            depends = [element_dict[d] for d in depends]
            resolver.add(element, *depends)

        elements = resolver.get_dependents()
        iterator = IteratorExclude(elements,
            self._dependent_exclude_func,
            self._dependent_exclude_func)
        iterator = IteratorPreRepeat(iterator,
            lambda element, resolver=resolver: \
                   self._dependent_prerepeat_next_func(element, resolver))

        super(DependsIterator, self).__init__(iterator)

    def _dependent_exclude_func(self, element):
        return element.get("auto", False)

    def _dependent_prerepeat_next_func(self, element, resolver):
        from checkbox.job import PASS, UNINITIATED, UNTESTED

        status = element.get("status", UNINITIATED)
        if status != UNINITIATED:
            if status != PASS:
                for dependent in resolver.get_dependents(element):
                    dependent["status"] = UNTESTED
                    dependent["auto"] = True
            else:
                for dependent in resolver.get_dependents(element):
                    dependent["status"] = UNINITIATED
                    del dependent["auto"]
