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
def merge_function_metadata(original, new):
    """Overwrite C{new}'s docstring and instance dictionary from C{original}.

    This also sets an C{original_function} attribute on the new
    function to C{original}. This is to allow code
    introspect various things about the original function.
    """
    new.__doc__ = original.__doc__
    new.__dict__.update(original.__dict__)
    new.original_function = original
