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
from inspect import getargspec

from checkbox.lib.decorator import merge_function_metadata


class ArgumentReplacer:
    """A decorator helper that filters arguments to be passed to a function.

    Create one with the original function and a function to replace
    the arguments, and then call replace_arguments for each call to
    the function.
    """
    def __init__(self, original_function, argument_replacer):
        """
        @param original_function: The function which will be called
            soon. The function must *not* define any * or ** parameters.
        @param argument_replacer: A function which will be called for
            every argument. It will be passed a parameter name and the
            associated argument. It should return the new value.
        """
        self.original_function = original_function
        self.argument_replacer = argument_replacer

        spec = getargspec(original_function)
        self.all_arguments = spec[0]
        if getattr(original_function, 'im_self', None) is not None:
            # If it's bound, ignore the bound arguments.
            self.all_arguments = self.all_arguments[1:]

    def replace_arguments(self, args, kwargs):
        """Filter some arguments destined to be passed to a function.

        @param args: Original positional arguments.
        @param kwargs: Original keyword arguments.

        @return: new arguments and kwarguments.
        """
        args = list(args)
        kwargs = kwargs.copy()

        for name_index, name in enumerate(self.all_arguments):
            # Ok, we've got the name of the argument. Let's find the value
            # of the argument in our original arguments and replace it
            # whether it's a positional or a keyword argument.
            if name_index < len(args):
                # Must be a positional argument
                value = args[name_index]
                args[name_index] = self.argument_replacer(name, value)
            else:
                # Must be a keyword argument
                if name not in kwargs:
                    # Oh, but it wasn't passed in. Ignore it.
                    continue
                value = kwargs[name]
                kwargs[name] = self.argument_replacer(name, value)
        return args, kwargs


def coerce_arguments(**schemas):
    """
    A decorator factory which returns a decorator which coerces arguments.
    """
    def replacer(name, value):
        if name in schemas:
            return schemas[name].coerce(value)
        return value

    def decorator(original):
        argument_replacer = ArgumentReplacer(original, replacer)
        def replacement(*args, **kwargs):
            new_args, new_kwargs = argument_replacer.replace_arguments(args,
                                                                       kwargs)
            return original(*new_args, **new_kwargs)
        merge_function_metadata(original, replacement)
        return replacement

    return decorator
