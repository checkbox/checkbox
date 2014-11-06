# This file is part of Checkbox.
#
# Copyright 2012, 2013, 2014 Canonical Ltd.
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
:mod:`plainbox.impl.providers.special` -- various special providers
===================================================================

.. warning::

    THIS MODULE DOES NOT HAVE STABLE PUBLIC API
"""

from importlib.machinery import SourceFileLoader
import logging
import os

from plainbox.i18n import gettext_noop as N_
from plainbox.impl import get_plainbox_dir
from plainbox.impl.secure.config import Unset
from plainbox.impl.secure.providers.v1 import Provider1
from plainbox.impl.secure.providers.v1 import Provider1Definition


logger = logging.getLogger("plainbox.providers.special")


def get_stubbox_def():
    """
    Get a Provider1Definition for stubbox
    """
    stubbox_def = Provider1Definition()
    stubbox_def.name = "2013.com.canonical.plainbox:stubbox"
    stubbox_def.version = "1.0"
    stubbox_def.description = N_("StubBox (dummy data for development)")
    stubbox_def.secure = False
    stubbox_def.gettext_domain = "stubbox"
    stubbox_def.location = os.path.join(
        get_plainbox_dir(), "impl/providers/stubbox")
    return stubbox_def


def get_stubbox():
    return Provider1.from_definition(get_stubbox_def(), secure=False)


def get_categories_def():
    """
    Get a Provider1Definition for the provider that knows all the categories
    """
    categories_def = Provider1Definition()
    categories_def.name = "2013.com.canonical.plainbox:categories"
    categories_def.version = "1.0"
    categories_def.description = N_("Common test category definitions")
    categories_def.secure = False
    categories_def.gettext_domain = "2013_com_canonical_plainbox_categories"
    categories_def.location = os.path.join(
        get_plainbox_dir(), "impl/providers/categories")
    return categories_def


def get_categories():
    return Provider1.from_definition(get_categories_def(), secure=False)


def get_embedded_providers_defs(path):
    """
    Get a list of Proivder1Definition of all providers present in `path`
    """
    providers_defs = []

    # assumption: we don't go recursive in path
    entries = os.listdir(path)
    for entry in entries:
        if os.path.isdir(os.path.join(path, entry)):
            manage_py = os.path.join(path, entry, 'manage.py')
            if os.path.exists(manage_py):
                providers_defs.append(load_provider_from_manage_py(manage_py))

    return providers_defs


def get_embedded_providers(path):
    return [Provider1.from_definition(definition, secure=False)
            for definition in get_embedded_providers_defs(path)]


def load_provider_from_manage_py(manage_py):
    # override provider_manager.setup() to capture setup's parameters
    setup_kwargs = []

    def fake_setup(**kwargs):
        setup_kwargs.append(kwargs)

    from plainbox import provider_manager
    provider_manager.setup = fake_setup

    loader = SourceFileLoader('manage', manage_py)
    loader.load_module()
    location = os.path.dirname(os.path.abspath(manage_py))
    setup_kwargs = setup_kwargs.pop()
    definition = Provider1Definition()
    definition.location = location
    definition.name = setup_kwargs.get('name', None)
    definition.version = setup_kwargs.get('version', None)
    definition.description = setup_kwargs.get('description', None)
    definition.gettext_domain = setup_kwargs.get('gettext_domain', Unset)
    return definition
