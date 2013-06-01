#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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
import builtins


__all__ = ["ResourceMap"]


class ResourceObject:
    __slots__ = ("_iterator", "_name", "_convert",)

    def __init__(self, iterator, name, convert=lambda x: x):
        self._iterator = iterator
        self._name = name
        self._convert = convert

    def __cmp__(self, other):
        return self._try(other, cmp, 0, 1)

    def __lt__(self, other):
        return self._try(other, lambda a, b: a < b)

    def __le__(self, other):
        return self._try(other, lambda a, b: a <= b)

    def __gt__(self, other):
        return self._try(other, lambda a, b: a > b)

    def __ge__(self, other):
        return self._try(other, lambda a, b: a >= b)

    def __eq__(self, other):
        return self._try(other, lambda a, b: a == b)

    def __ne__(self, other):
        return self._try(other, lambda a, b: a != b)

    def __contains__(self, other):
        return self._try(other, lambda a, b: b in a)

    def _try(self, other, function, until=True, default=False):
        found = False
        for item in self._iterator:
            if self._name in item:
                value = self._convert(item[self._name])
                if function(value, other) == until:
                    # Append item to results
                    self._iterator._map._results.append(item)
                    found = True

        return until if found else default


class ResourceIterator:
    __slots__ = ("_map", "_values",)

    def __init__(self, map, values):
        self._map = map
        self._values = values

    def __contains__(self, elt):
        found = False
        for value in self._values:
            if elt in value:
                self._map._results.append(value)
                found = True

        return found

    def __iter__(self):
        for value in self._values:
            yield value

    def __getattr__(self, name):
        return ResourceObject(self, name)


class ResourceBuiltin:
    __slots__ = ("_function",)

    def __init__(self, function):
        self._function = function

    def __call__(self, object):
        return ResourceObject(object._iterator, object._name, self._function)


class ResourceGlobals(dict):

    def __init__(self, names, *args, **kwargs):
        super(ResourceGlobals, self).__init__(*args, **kwargs)

        for name in names:
            function = getattr(builtins, name)
            self[name] = ResourceBuiltin(function)


class ResourceMap(dict):
    __slots__ = ("_results",)

    def __getitem__(self, key):
        value = super(ResourceMap, self).__getitem__(key)
        if isinstance(value, (list, tuple)):
            return ResourceIterator(self, value)

        elif isinstance(value, dict):
            return ResourceIterator(self, [value])

        else:
            return value

    def eval(self, source):
        self._results = []
        resource_globals = ResourceGlobals(["bool", "float", "int", "str"])
        try:
            value = eval(source, resource_globals, self)
            if (isinstance(value, (bool, int)) and value) \
               or (isinstance(value, tuple) and True in value):
                return self._results
        except Exception:
            pass

        return None
