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

from io import StringIO

from checkbox.lib.text import split


def raise_none_error(attribute):
    if not attribute:
        raise ValueError("None isn't acceptable as a value")
    else:
        name = attribute.name
        raise ValueError("None isn't acceptable as a value for %s" % name)


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


class Variable:

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
        if self._value is None and self._required is True:
            raise_none_error(self.attribute)

        return self._value

    def set(self, value):
        if value is None:
            if self._required is True:
                raise_none_error(self.attribute)

            new_value = None
        else:
            new_value = self.coerce(value)

        self._value = new_value

    def coerce(self, value):
        return value


class ConstantVariable(Variable):
    __slots__ = ("_item_factory",)

    def __init__(self, item_factory, *args, **kwargs):
        self._item_factory = item_factory
        super(ConstantVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        if self._value is not None and value != self._value:
            raise ValueError("%r != %r" % (value, self._value))
        return self._item_factory(value=value).get()


class BoolVariable(Variable):
    __slots__ = ()

    def coerce(self, value):
        if isinstance(value, str):
            if re.match(r"(yes|true)", value, re.IGNORECASE):
                value = True
            elif re.match(r"(no|false)", value, re.IGNORECASE):
                value = False
            else:
                raise ValueError("%r is not a bool string" % (value,))
        elif not isinstance(value, bool):
            raise ValueError("%r is not a bool" % (value,))

        return value


class BytesVariable(Variable):
    __slots__ = ()

    def coerce(self, value):
        if isinstance(value, str):
            value = value.encode('utf-8')
        elif not isinstance(value, bytes):
            raise ValueError("%r is not bytes" % (value,))

        return value


class StringVariable(Variable):
    __slots__ = ()

    def coerce(self, value):
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        elif not isinstance(value, str):
            raise ValueError("%r is not a str" % (value,))

        return value


class PathVariable(StringVariable):
    __slots__ = ()

    def coerce(self, value):
        path = super(PathVariable, self).coerce(value)
        return posixpath.expanduser(path)


class IntVariable(Variable):
    __slots__ = ()

    def coerce(self, value):
        if isinstance(value, str):
            value = int(value)
        elif not isinstance(value, int):
            raise ValueError("%r is not an int nor long" % (value,))

        return value


class FloatVariable(Variable):
    __slots__ = ()

    def coerce(self, value):
        if isinstance(value, str):
            value = float(value)
        elif not isinstance(value, (int, float)):
            raise ValueError("%r is not a float" % (value,))

        return value


class TimeVariable(FloatVariable):
    __slots__ = ()

    pass


class ListVariable(Variable):
    __slots__ = ("_item_factory", "_separator")

    def __init__(self, item_factory, separator, *args, **kwargs):
        self._item_factory = item_factory
        self._separator = separator
        super(ListVariable, self).__init__(*args, **kwargs)

    def coerce(self, values):
        item_factory = self._item_factory
        if isinstance(values, str):
            values = split(values, self._separator) if values else []
        elif not isinstance(values, (list, tuple)):
            raise ValueError("%r is not a list or tuple" % (values,))

        for i, v in enumerate(values):
            values[i] = item_factory(value=v).get()

        return values


class TupleVariable(ListVariable):

    def coerce(self, values):
        values = super(TupleVariable, self).coerce(list(values))
        return tuple(values)


class AnyVariable(Variable):
    __slots__ = ("_schemas",)

    def __init__(self, schemas, *args, **kwargs):
        self._schemas = schemas
        super(AnyVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        for schema in self._schemas:
            try:
                # Only check that the value can be coerced
                schema(value=value).get()
                return value
            except ValueError:
                pass

        raise ValueError("%r did not match any schema" % value)


class DictVariable(Variable):
    __slots__ = ("_key_schema", "_value_schema")

    def __init__(self, key_schema, value_schema, *args, **kwargs):
        self._key_schema = key_schema
        self._value_schema = value_schema
        super(DictVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        if not isinstance(value, dict):
            raise ValueError("%r is not a dict." % (value,))

        for k, v in value.items():
            value[self._key_schema(value=k).get()] = \
                self._value_schema(value=v).get()
        return value


class MapVariable(Variable):
    __slots__ = ("_schema",)

    def __init__(self, schema, *args, **kwargs):
        self._schema = schema
        super(MapVariable, self).__init__(*args, **kwargs)

    def coerce(self, value):
        if not isinstance(value, dict):
            raise ValueError("%r is not a dict." % (value,))

        for k, v in value.items():
            if k not in self._schema:
                raise ValueError("%r is not a valid key as per %r"
                                   % (k, self._schema))

        for attribute, variable in self._schema.items():
            old_value = value.get(attribute)
            try:
                new_value = variable(value=old_value).get()
            except ValueError as e:
                raise ValueError(
                    "Value of %r key of dict %r could not be converted: %s"
                    % (attribute, value, e))

            if attribute in value:
                value[attribute] = new_value

        return value


class FileVariable(Variable):
    __slots__ = ()

    def coerce(self, value):
        if isinstance(value, str):
            value = StringIO(value)
        elif not hasattr(value, "read"):
            raise ValueError("%r is not a file" % (value,))

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
        for attribute in get_attributes(cls).values():
            variable = attribute.variable_factory(attribute=attribute)
            variables[attribute] = variable

        return obj.__dict__.setdefault("__checkbox_variables__", variables)
