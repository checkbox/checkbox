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
import __builtin__


__all__ = ["ResourceMap"]


class ResourceObject(object):
    __slots__ = ("_list", "_name", "_convert",)

    def __init__(self, list, name, convert=lambda x: x):
        self._list = list
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

    def _try(self, other, function, until=True, default=False):
        found = False
        for item in self._list:
            if self._name in item:
                value = self._convert(item[self._name])
                if function(value, other) == until:
                    # Append item to list of results
                    self._list._map._results.append(item)
                    found = True

        return until if found else default


class ResourceList(list):
    __slots__ = ("_map",)

    def __init__(self, map, *args, **kwargs):
        super(ResourceList, self).__init__(*args, **kwargs)
        self._map = map

    def __getattr__(self, name):
        return ResourceObject(self, name)


class ResourceBuiltin(object):
    __slots__ = ("_function",)

    def __init__(self, function):
        self._function = function

    def __call__(self, object):
        return ResourceObject(object._list, object._name, self._function)


class ResourceGlobals(dict):

    def __init__(self, names, *args, **kwargs):
        super(ResourceGlobals, self).__init__(*args, **kwargs)
        self["__builtins__"] = None

        for name in names:
            function = getattr(__builtin__, name)
            self[name] = ResourceBuiltin(function)


class ResourceMap(dict):
    __slots__ = ("_results",)

    def __getitem__(self, key):
        value = super(ResourceMap, self).__getitem__(key)
        if isinstance(value, (list, tuple)):
            return ResourceList(self, value)

        else:
            return value

    def eval(self, source):
        self._results = []
        resource_globals = ResourceGlobals(["bool", "float", "int", "long", "str"])
        try:
            value = eval(source, resource_globals, self)
            if (isinstance(value, (bool, int)) and value) \
               or (isinstance(value, tuple) and True in value):
                return self._results
        except Exception:
            pass

        return []
