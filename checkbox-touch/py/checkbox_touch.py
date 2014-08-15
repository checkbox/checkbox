# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
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
:mod:`checkbox_touch` -- touch specific APIs
============================================

This module contains APIs specific to the implementation of checkbox-touch.
"""

from gettext import gettext as _

try:
    import pyotherside
except ImportError:
    raise SystemExit(
        ("Please don't try to import or this module directly,"
         " it only works when imported from QML"))


def get_welcome_text():
    """
    Get the replacement for the "Welcome text" message
    """
    return _("Welcome text (python loaded)")


# NOTE: this is just an example, it's not really needed for anything
pyotherside.send("python-core-loaded")
