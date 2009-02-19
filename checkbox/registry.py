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
import re

from checkbox.lib.cache import cache

from checkbox.component import ComponentManager
from checkbox.properties import String


class Registry(object):
    """
    Registry base class which should be inherited by each registry
    implementation. This class basically provides methods to represent
    the items in the registry as attributes. If some items cannot
    be represented as attributes, if there are spaces in the name
    for example, this class also provides methods to reprent them as
    dictionary elements.
    """

    _id = 0

    user = String(required=False)

    def __init__(self):
        super(Registry, self).__init__()
        self.id = Registry._id
        Registry._id += 1

    def __str__(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def __getattr__(self, name):
        return self.get(name)

    def split(self, *args, **kwargs):
        return str(self).split(*args, **kwargs)

    def items(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            if default == None:
                from checkbox.registries.none import NoneRegistry
                return NoneRegistry()
            else:
                return default

    def has_key(self, key):
        return key in self.keys()

    def iteritems(self):
        for k, v in self.items():
            yield k, v

    def iterkeys(self):
        from checkbox.registries.link import LinkRegistry

        for k, v in self.items():
            # Prevent returning links in a dict() context
            if not isinstance(v, LinkRegistry):
                yield k

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        from checkbox.registries.link import LinkRegistry

        for k, v in self.items():
            # Prevent returning links in a values() context
            if not isinstance(v, LinkRegistry):
                yield v

    def values(self):
        return list(self.itervalues())

    def clear(self):
        raise Exception, "Cannot call clear on registry."

    def setdefault(self, key, default=None):
        raise Exception, "Cannot call setdefault on registry."

    def __cmp__(self, foreign):
        local = set(self.items())
        foreign = set(foreign.items())
        if local == foreign:
            return 0
        elif local < foreign:
            return -1
        return 1

    def __contains__(self, key):
        return key in self.keys()

    def __len__(self):
        return len(self.keys())

    def __getitem__(self, key):
        for k, v in self.items():
            if k == key:
                return v

        raise KeyError

    def __setitem__(self, key, value):
        raise Exception, "Cannot set setitem on registry."

    def __delitem__(self, key):
        raise Exception, "Cannot call delitem on registry."

    def update(self, foreign):
        raise Exception, "Cannot call update on registry."


class RegistryManager(ComponentManager, Registry):
    """
    Registry manager which is essentially the root of the registry
    tree. The first level in this tree consists of the module names
    which have been loaded from the registries configuration parameter.
    """

    @cache
    def items(self):
        items = []
        registries = self._config.get_defaults().registries
        section_names = re.split(r"\s+", registries)
        for section_name in section_names:
            section = self.load_section(section_name)
            for name in section.get_names():
                module = section.load_module(name)
                items.append((name, module))

        return items


def registry_flatten(registry):
    def get_properties(properties, key, value):
        if isinstance(value, Registry):
            for dict_key, dict_value in value.items():
                get_properties(properties,
                    ".".join([key, dict_key]), dict_value)
        else:
            properties[key] = value

    properties = {}
    for key, value in registry.items():
        get_properties(properties, key, value)

    return properties

def registry_eval(registry, source):
    try:
        return eval(source, {}, registry)
    except Exception:
        return False

def registry_eval_recursive(registry, source, mask=[False]):
    values = []

    value = registry_eval(registry, source)
    if type(value) in (bool, int) and value:
        values.append(registry)
        mask[0] = True
    elif type(value) is tuple and True in value:
        for i in range(len(value)):
            if value[i] is True or i >= len(mask):
                mask[i:i+1] = [value[i]]

        values.append(registry)

    for key, value in registry.items():
        if isinstance(value, Registry):
            values.extend(registry_eval_recursive(value, source, mask))

    return values
