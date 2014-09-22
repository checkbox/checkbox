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
from plainbox.impl.clitools import ToolBase
import plainbox

from checkbox_stack import PlainboxApplication


__version__ = (0, 2, 0, 'dev', 0)


class CheckboxTouchApplication(PlainboxApplication):
    """
    Class implementing the whole checkbox-touch application logic.

    This class exposes methods that can be called by the javascript embedded
    into many of the QML views. Each method implements a request / response
    semantics where the request is the set of data passed to python from
    javascript and the response is the python dictionary returned and processed
    back on the javascript side.

    This model follows the similar web development mechanics where the browser
    can issue asynchronous requests in reaction to user interactions and uses
    response data to alter the user interface.
    """

    def get_version_pair(self) -> (str, str):
        return {
            'plainbox_version': ToolBase.format_version_tuple(
                plainbox.__version__),
            'application_version': ToolBase.format_version_tuple(__version__)
        }


create_app_object = CheckboxTouchApplication.create_and_get_handle
