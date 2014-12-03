#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
# Written by:
#   Sylvain Pineau <sylvain.pineau@canonical.com>
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

from plainbox.provider_manager import setup, N_

setup(
    name='2014.com.ubuntu:ubuntu-touch',
    version="1.1",
    description=N_("The Ubuntu Touch for Plainbox"),
    gettext_domain="plainbox-provider-ubuntu-touch",
    strict=False,
)
