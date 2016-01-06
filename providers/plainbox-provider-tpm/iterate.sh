#!/bin/sh
# This file is part of Checkbox.
#
# Copyright 2015 Canonical Ltd.
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

# This simple script was used for development.
# Please do not put it into binary packages.
set -x
set -e
test_plan=2015.com.canonical.certification.tpm::smoke-tests
./manage.py validate
plainbox dev analyze --print-run-list -T $test_plan
plainbox run -T $test_plan --dont-suppress-output -f json -p with-resource-map,with-attachments
