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

    def get(self):
        return self._value

    def set(self, value):
        if value is None:
            if self._required is True:
                raise Exception, "None isn't an acceptable value"
            new_value = None
        else:
            new_value = self.coerce(value)

        self._value = new_value

    def coerce(self, value):
        return value


class ConstantVariable(Variable):

    def __init__(self, item_factory, *args, **kwargs):
        self._item_factory = item_factory
        super(ConstantVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        if self._value is not None and value != self._value:
            raise TypeError("%r != %r" % (value, self._value))
        return self._item_factory(value=value).get()


class BoolVariable(Variable):

    def coerce(self, value):
        if isinstance(value, bool):
            return value
        elif re.match(r"(yes|true)", value, re.IGNORECASE):
            return True
        elif re.match(r"(no|false)", value, re.IGNORECASE):
            return False
        else:
            return bool(int(value))


class StringVariable(Variable):

    def coerce(self, value):
        return str(value)


class PathVariable(StringVariable):

    def coerce(self, value):
        path = super(PathVariable, self).coerce(value)
        return posixpath.expanduser(path)


class UnicodeVariable(Variable):

    def coerce(self, value):
        return unicode(value)


class IntVariable(Variable):

    def coerce(self, value):
        return int(value)


class FloatVariable(Variable):

    def coerce(self, value):
        return float(value)


class ListVariable(Variable):

    def __init__(self, item_factory, *args, **kwargs):
        self._item_factory = item_factory
        super(ListVariable, self).__init__(*args, **kwargs)

    def coerce(self, values):
        item_factory = self._item_factory
        if not len(values):
            values = []
        elif not isinstance(values, (list, tuple,)):
            values = re.split(r"\s*,?\s+", values)

        return [item_factory(value=v).get() for v in values]


class TupleVariable(ListVariable):

    def coerce(self, values):
        values = super(TupleVariable, self).coerce(values)
        return tuple(values)


class AnyVariable(Variable):

    def __init__(self, schemas, *args, **kwargs):
        self._schemas = schemas
        super(AnyVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        for schema in self._schemas:
            try:
                # Only check that the value can be coerced
                dummy = schema(value=value).get()
                return value
            except TypeError:
                pass

        raise TypeError("%r did not match any schema" % value)


class DictVariable(Variable):

    def __init__(self, key_schema, value_schema, *args, **kwargs):
        self._key_schema = key_schema
        self._value_schema = value_schema
        super(DictVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        if not isinstance(value, dict):
            raise TypeError("%r is not a dict." % (value,))
        new_dict = {}
        for k, v in value.items():
            new_dict[self._key_schema(value=k).get()] = \
                self._value_schema(value=v).get()
        return new_dict


class MapVariable(Variable):

    def __init__(self, schema, optional, *args, **kwargs):
        self._schema = schema
        self._optional = set(optional)
        super(MapVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        new_dict = {}
        if not isinstance(value, dict):
            raise TypeError("%r is not a dict." % (value,))
        for k, v in value.iteritems():
            if k not in self._schema:
                raise TypeError("%r is not a valid key as per %r"
                                   % (k, self._schema))
            try:
                new_dict[k] = self._schema[k](value=v).get()
            except TypeError, e:
                raise TypeError(
                    "Value of %r key of dict %r could not be converted: %s"
                    % (k, value, e))
        new_keys = set(new_dict.keys())
        required_keys = set(self._schema.keys()) - self._optional
        missing = required_keys - new_keys
        if missing:
            raise TypeError("Missing keys %s" % (missing,))
        return new_dict


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
