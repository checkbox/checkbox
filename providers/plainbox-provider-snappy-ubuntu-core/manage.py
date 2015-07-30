#!/usr/bin/env python3
from plainbox.provider_manager import setup, N_

# This file is part of Checkbox.
#
# Copyright 2015 Canonical Ltd.
# Written by:
#   Jonathan Cave <jonathan.cave@canonical.com>
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

setup(
    name='plainbox-provider-snappy-ubuntu-core',
    namespace='2013.com.canonical.certification',
    version="1.0",
    description=N_("Canonical certification provider for Snappy Ubuntu Core"),
    gettext_domain='plainbox-provider-snappy-ubuntu-core',
)
