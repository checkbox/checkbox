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
import inspect


def format_class(cls):
    return "%s.%s" % (cls.__module__, cls.__name__)

def format_object(object):
    """
    Returns a fully-qualified name for the specified object, such as
    'checkbox.log.format_object()'.
    """
    if inspect.ismethod(object):
        # FIXME If the method is implemented on a base class of
        # object's class, the module name and function name will be
        # from the base class and the method's class name will be from
        # object's class.
        name = repr(object).split(" ")[2]
        return "%s.%s()" % (object.__module__, name)
    elif inspect.isfunction(object):
        name = repr(object).split(" ")[1]
        return "%s.%s()" % (object.__module__, name)
    return format_class(object.__class__)

def format_delta(seconds):
    if not seconds:
        seconds = 0.0
    return "%.02fs" % float(seconds)
