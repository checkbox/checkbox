#
# This file is part of Checkbox.
#
# Copyright 2011 Canonical Ltd.
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


def implement_from_dict(class_name, methods=[], superclass=object):
    """Return a class that implements empty methods.

    :param superclass: The superclass of the class to be generated.
    :param methods: A list of method names to implement as empty.
    """
    def empty(*args, **kwargs):
        pass

    class_dict = {}
    for method in methods:
        class_dict[method] = empty

    if not isinstance(superclass, tuple):
        superclass = (superclass,)
    return type(class_name, superclass, class_dict)
