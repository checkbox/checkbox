# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

"""
:mod:`plainbox.impl.commands.list` -- list sub-command
======================================================
"""

import logging

from plainbox.i18n import gettext as _
from plainbox.impl.commands import PlainBoxCommand
from plainbox.impl.highlevel import Explorer


logger = logging.getLogger("plainbox.commands.list")


class ListInvocation:

    def __init__(self, provider_list, ns):
        self.explorer = Explorer(provider_list)
        self.group = ns.group
        self.show_attrs = ns.attrs

    def run(self):
        obj = self.explorer.get_object_tree()
        self._show(obj)

    def _show(self, obj, indent=None):
        if indent is None:
            indent = ""
        # Apply optional filtering
        if self.group is None or obj.group == self.group:
            # Display the object name and group
            print("{}{} {!r}".format(indent, obj.group, obj.name))
            indent += "  "
            # It would be cool if this would draw an ASCI-art tree
            if self.show_attrs:
                for key, value in obj.attrs.items():
                    print("{}{}: {!r}".format(indent, key, value))
        if obj.children:
            if self.group is None:
                print("{}{}".format(indent, _("children")))
                indent += "  "
            for child in obj.children:
                self._show(child, indent)


class ListCommand(PlainBoxCommand):
    """
    Implementation of ``$ plainbox dev list <object>``
    """

    def __init__(self, provider_list):
        self.provider_list = provider_list

    def invoked(self, ns):
        self.autopager()
        return ListInvocation(self.provider_list, ns).run()

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            "list", help=_("list and describe various objects"),
            prog="plainbox dev list")
        parser.add_argument(
            '-a', '--attrs', default=False, action="store_true",
            help=_("show object attributes"))
        parser.add_argument(
            'group', nargs='?',
            help=_("list objects from the specified group"))
        parser.set_defaults(command=self)
