#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
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
setup.py multiplexer
====================

This `setup.py` is really a multiplexer to various setup.py files (for
plainbox, checkbox-ng, etc). It was implemented because readthedocs.org cannot
handle many projects in one repository correctly.
"""
import glob
import os
import subprocess
import sys

delegate_to = ['plainbox', 'checkbox-ng', 'checkbox-old']
delegate_to.extend(glob.glob('plainbox-provider*'))
try:
    base = os.path.dirname(__file__)
    for target_dir in delegate_to:
        # NOTE: use sys.executable because 'python' and 'python3' resolve to
        # non-virtualenv (!) versions of python when building on
        # readthedocs.org
        cmd = [sys.executable, 'setup.py'] + sys.argv[1:]
        cwd = os.path.join(base, target_dir)
        subprocess.check_call(cmd, cwd=cwd)
except subprocess.CalledProcessError as exc:
    raise SystemExit(str(exc))
