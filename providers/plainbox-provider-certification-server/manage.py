#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2012, 2013, 2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

from plainbox.provider_manager import SourceDistributionCommand
from plainbox.provider_manager import manage_py_extension
from plainbox.provider_manager import setup, N_


@manage_py_extension
class SourceDistributionCommandExt(SourceDistributionCommand):
    # Overridden version of SourceDistributionCommand that handles COPYING
    __doc__ = SourceDistributionCommand.__doc__
    _INCLUDED_ITEMS = SourceDistributionCommand._INCLUDED_ITEMS + ['COPYING']


setup(
    name='2013.com.canonical.certification:certification-server',
    version="1.0",
    description=N_("Server Certification provider"),
    gettext_domain="2013_com_canonical_certification_certification-server",
)
