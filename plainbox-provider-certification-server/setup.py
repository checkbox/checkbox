#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
#   Sylvain Pineau <sylvain.pineau@canonical.com>
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

from glob import glob

import DistUtilsExtra.auto

with open("README.rst", encoding="UTF-8") as stream:
    LONG_DESCRIPTION = stream.read()

DATA_FILES = [
    ("/usr/lib/plainbox-providers-1/certification-server/whitelists",
        glob("provider_whitelists/*")),
    ("/usr/share/plainbox-providers-1", ["certification-server.provider"])
]

DistUtilsExtra.auto.setup(
    # To work as expected, the provider content lives in directories starting
    # with provider_ so that DistUtilsExtra auto features avoid putting files
    # in /usr/bin and /usr/share automatically.
    name="plainbox-provider-certification-server",
    version="0.4.dev",
    url="https://launchpad.net/checkbox/",
    author="Sylvain Pineau",
    author_email="sylvain.pineau@canonical.com",
    license="GPLv3+",
    description="Server Certification provider",
    long_description=LONG_DESCRIPTION,
    data_files=DATA_FILES,
    )
