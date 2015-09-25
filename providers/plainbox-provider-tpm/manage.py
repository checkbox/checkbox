#!/usr/bin/env python3
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

"""Management script for the TPM provider."""

from plainbox.provider_manager import setup, N_


setup(
    name='plainbox-provider-tpm',
    namespace='2015.com.canonical.certification.tpm',
    version="0.1",
    description=N_("Plainbox Provider for TPM (trusted platform module)"),
    gettext_domain='plainbox-provider-tpm',
)
