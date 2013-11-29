#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
from checkbox.variables import Variable


class Attribute:

    def __init__(self, name, cls, variable_factory=None):
        self.name = name
        self.cls = cls
        self.variable_factory = variable_factory or Variable


def get_attributes(cls):
    if "__checkbox_attributes__" in cls.__dict__:
        return cls.__dict__["__checkbox_attributes__"]
    else:
        attributes = {}
        for name in dir(cls):
            attribute = getattr(cls, name, None)
            if isinstance(attribute, Attribute):
                attributes[name] = attribute

        cls.__checkbox_attributes__ = attributes
        return cls.__checkbox_attributes__
