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
import posixpath


# Implementation of partial function in Python 2.5+
def VariableFactory(cls, **old_kwargs):
    def variable_factory(**new_kwargs):
        kwargs = old_kwargs.copy()
        kwargs.update(new_kwargs)
        return cls(**kwargs)

    return variable_factory

try:
    from functools import partial as VariableFactory
except ImportError:
    pass


class Variable(object):

    _value = None
    _required = True

    attribute = None

    def __init__(self, attribute=None, value=None, value_factory=None,
                 required=True):
        self.attribute = attribute
        self._required = required
        if value is not None:
            self.set(value)
        if value_factory is not None:
            self.set(value_factory())

    def get(self, default=None):
        value = self._value
        if value is None:
            return default
        else:
            return self.parse_get(value)

    def set(self, value):
        if value is None:
            if self._required is True:
                raise Exception, "None isn't an acceptable value"
            new_value = None
        else:
            new_value = self.parse_set(value)

        self._value = new_value

    def parse_get(self, value):
        return value

    def parse_set(self, value):
        return str(value)


class BoolVariable(Variable):

    def parse_get(self, value):
        if re.match(r"(yes|true)", value, re.IGNORECASE):
            return True
        elif re.match(r"(no|false)", value, re.IGNORECASE):
            return False
        else:
            return bool(int(value))


class StringVariable(Variable):

    def parse_get(self, value):
        return str(value)


class PathVariable(StringVariable):

    def parse_get(self, value):
        path = super(PathVariable, self).parse_get(value)
        return posixpath.expanduser(path)


class IntVariable(Variable):

    def parse_get(self, value):
        return int(value)


class FloatVariable(Variable):

    def parse_get(self, value):
        return float(value)


class ListVariable(Variable):

    def __init__(self, item_factory, *args, **kwargs):
        super(ListVariable, self).__init__(*args, **kwargs)
        self._item_factory = item_factory

    def parse_get(self, value):
        item_factory = self._item_factory
        if not len(value):
            values = []
        else:
            values = re.split(r"\s*,?\s+", value)

        return [item_factory(value=v).get() for v in values]

    def parse_set(self, value):
        if isinstance(value, list):
            return ", ".join(value)
        else:
            return value


def get_variable(obj, attribute):
    return get_variables(obj)[attribute]

def get_variables(obj):
    from checkbox.attribute import get_attributes

    if "__checkbox_variables__" in obj.__dict__:
        return obj.__dict__["__checkbox_variables__"]
    else:
        variables = {}
        cls = type(obj)
        for attribute in get_attributes(cls).itervalues():
            variable = attribute.variable_factory(attribute=attribute)
            variables[attribute] = variable

        return obj.__dict__.setdefault("__checkbox_variables__", variables)
