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
from checkbox.attribute import Attribute
from checkbox.variables import (ConstantVariable, BoolVariable, BytesVariable,
    StringVariable, PathVariable, IntVariable, FloatVariable, TimeVariable,
    ListVariable, TupleVariable, AnyVariable, DictVariable, MapVariable,
    FileVariable, VariableFactory, Variable, get_variable)


class Property:

    def __init__(self, variable_class=Variable, variable_kwargs={}):
        self._variable_class = variable_class
        self._variable_kwargs = variable_kwargs

    def __get__(self, obj, cls=None):
        if obj is None:
            return self._get_attribute(cls)
        if cls is None:
            cls = type(obj)
        attribute = self._get_attribute(cls)
        variable = get_variable(obj, attribute)
        return variable.get()

    def __set__(self, obj, value):
        cls = type(obj)
        attribute = self._get_attribute(cls)
        variable = get_variable(obj, attribute)
        variable.set(value)

    def _detect_name(self, used_cls):
        self_id = id(self)
        for cls in used_cls.__mro__:
            for attr, prop in cls.__dict__.items():
                if id(prop) == self_id:
                    return attr
        raise RuntimeError("Property used in an unknown class")

    def _get_attribute(self, cls):
        try:
            attribute = cls.__dict__["_checkbox_attributes"].get(self)
        except KeyError:
            cls._checkbox_attributes = {}
            attribute = None

        if attribute is None:
            name = self._detect_name(cls)
            attribute = PropertyAttribute(self, cls, name,
                self._variable_class, self._variable_kwargs)
            cls._checkbox_attributes[self] = attribute

        return attribute

    def coerce(self, value):
        return self._variable_class(**self._variable_kwargs).coerce(value)


class PropertyAttribute(Attribute):

    def __init__(self, prop, cls, name, variable_class, variable_kwargs):
        super(PropertyAttribute, self).__init__(name, cls,
            VariableFactory(variable_class, attribute=self, **variable_kwargs))

        self.cls = cls # Used by references

        # Copy attributes from the property to avoid one additional
        # function call on each access.
        for attr in ["__get__", "__set__"]:
            setattr(self, attr, getattr(prop, attr))


class PropertyType(Property):

    def __init__(self, **kwargs):
        kwargs["value"] = kwargs.pop("default", None)
        kwargs["value_factory"] = kwargs.pop("default_factory", None)
        super(PropertyType, self).__init__(self.variable_class, kwargs)


class PropertyFactory(PropertyType):

    def __init__(self, type=None, **kwargs):
        if "default" in kwargs:
            raise ValueError("'default' not allowed for factories. "
                             "Use 'default_factory' instead.")
        if type is None:
            type = Property()
        kwargs["item_factory"] = VariableFactory(type._variable_class,
            **type._variable_kwargs)
        super(PropertyFactory, self).__init__(**kwargs)


class Constant(PropertyFactory):

    variable_class = ConstantVariable


class Bool(PropertyType):

    variable_class = BoolVariable


class Bytes(PropertyType):

    variable_class = BytesVariable


class String(PropertyType):

    variable_class = StringVariable


class Path(PropertyType):

    variable_class = PathVariable


class Int(PropertyType):

    variable_class = IntVariable


class Float(PropertyType):

    variable_class = FloatVariable


class Time(PropertyType):

    variable_class = TimeVariable


class List(PropertyFactory):

    variable_class = ListVariable

    def __init__(self, *args, **kwargs):
        kwargs["separator"] = kwargs.pop("separator", r"\s")
        super(List, self).__init__(*args, **kwargs)


class Tuple(PropertyFactory):

    variable_class = TupleVariable


class Any(PropertyType):

    variable_class = AnyVariable

    def __init__(self, schemas=[], **kwargs):
        kwargs["schemas"] = [VariableFactory(schema._variable_class,
            **schema._variable_kwargs) for schema in schemas]
        self.schemas = schemas
        super(Any, self).__init__(**kwargs)


class Dict(PropertyType):

    variable_class = DictVariable

    def __init__(self, key, value, **kwargs):
        kwargs["key_schema"] = VariableFactory(key._variable_class,
            **key._variable_kwargs)
        kwargs["value_schema"] = VariableFactory(value._variable_class,
            **value._variable_kwargs)
        super(Dict, self).__init__(**kwargs)


class Map(PropertyType):

    variable_class = MapVariable

    def __init__(self, schema={}, **kwargs):
        for key, type in schema.items():
            schema[key] = VariableFactory(type._variable_class,
                **type._variable_kwargs)

        kwargs["schema"] = schema
        super(Map, self).__init__(**kwargs)


class File(PropertyType):

    variable_class = FileVariable


class Message(Map):

    def __init__(self, type, schema={}, **kwargs):
        self.type = type
        schema["type"] = Constant(default_factory=lambda: type, type=String())
        super(Message, self).__init__(schema, **kwargs)
