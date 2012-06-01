#
# This file is part of Checkbox.
#
# Copyright 2011 Canonical Ltd.
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
__all__ = [
    "EnumException", "Enum", "enum_name_to_value", "enum_value_to_name"]


class EnumException(Exception):

    pass


class Enum:

    def __init__(self, *names):
        value = 0
        unique_names = set()
        for name in names:
            if isinstance(name, (list, tuple)):
                name, value = name

            if not isinstance(name, str):
                raise EnumException(
                    "enum name is not a string: %s" % name)

            if isinstance(value, str):
                if value not in unique_names:
                    raise EnumException(
                        "enum value does not define: %s" % value)
                value = getattr(self, value)

            if not isinstance(value, int):
                raise EnumException(
                    "enum value is not an integer: %s" % value)

            if name in unique_names:
                raise EnumException(
                    "enum name is not unique: %s" % name)

            unique_names.add(name)
            setattr(self, name, value)
            value += 1


def enum_name_to_value(enum, name):
    if not hasattr(enum, name):
        raise EnumException("enum name unknown: %s" % name)

    return getattr(enum, name)


def enum_value_to_name(enum, value):
    for k, v in enum.__dict__.items():
        if v == value:
            return k

    raise EnumException("enum value unknown: %s" % value)
