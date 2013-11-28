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
import inspect
import logging

from logging import StreamHandler, FileHandler, Formatter


def format_class(cls):
    return "%s.%s" % (cls.__module__, cls.__name__)

def format_object(object, *args, **kwargs):
    """
    Returns a fully-qualified name for the specified object, such as
    'checkbox.log.format_object()'.
    """
    args_string = ""
    if args:
        args_string += ", ".join(str(a) for a in args)
        if kwargs:
            args_string += ", "
    if kwargs:
        args_string += ", ".join(["%s=%s" % (k, v) for k, v in kwargs.items()])

    module = object.__module__ if object.__module__ else inspect.getfile(object)
    if inspect.ismethod(object):
        # FIXME If the method is implemented on a base class of
        # object's class, the module name and function name will be
        # from the base class and the method's class name will be from
        # object's class.
        name = repr(object).split(" ")[2]
        return "%s %s(%s)" % (module, name, args_string)
    elif inspect.isfunction(object):
        name = repr(object).split(" ")[1]
        return "%s %s(%s)" % (module, name, args_string)
    return format_class(object.__class__)

def format_delta(seconds):
    if not seconds:
        seconds = 0.0
    return "%.02fs" % float(seconds)

def set_logging(level, log=None):
    log_level = logging.getLevelName(level.upper())
    log_handlers = []
    if log:
        log_filename = log
        log_handlers.append(FileHandler(log_filename))
    else:
        log_handlers.append(StreamHandler())

    # Log setup
    format = ("%(asctime)s %(levelname)-8s %(message)s")
    if log_handlers:
        for handler in log_handlers:
            handler.setFormatter(Formatter(format))
            logging.getLogger().addHandler(handler)
        if log_level:
            logging.getLogger().setLevel(log_level)
    elif not logging.getLogger().handlers:
        logging.disable(logging.CRITICAL)
