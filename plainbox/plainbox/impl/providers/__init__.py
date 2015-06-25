# This file is part of Checkbox.
#
# Copyright 2013-2015 Canonical Ltd.
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
APIs for working with providers.

:mod:`plainbox.impl.providers` -- providers package
===================================================

Providers are a mechanism by which PlainBox can enumerate jobs and whitelists.
Currently there are only v1 (as in version one) providers that basically have
to behave as CheckBox itself (mini CheckBox forks for example)

There is ongoing work and discussion on V2 providers that would have a
lower-level interface and would be able to define new job types, new whitelist
types and generally all the next-gen semantics.

PlainBox does not come with any real provider by default. PlainBox sometimes
creates special dummy providers that have particular data in them for testing.


V1 providers
------------

The first (current) version of PlainBox providers has the following properties,
this is also described by :class:`IProvider1`::

    * there is a directory with '.txt' or '.txt.in' files with RFC822-encoded
      job definitions. The definitions need a particular set of keys to work.

    * there is a directory with '.whitelist' files that contain a list (one per
      line) of job definitions to execute.

    * there is a directory with additional executables (added to PATH)

    * there is a directory with an additional python3 libraries (added to
      PYTHONPATH)
"""


class ProviderNotFound(LookupError):

    """ Exception used to report that a provider cannot be located. """


def get_providers(*, only_secure: bool=False) -> 'List[Provider1]':
    """
    Find and load all providers that are available.

    :param only_secure:
        (keyword only) Return only providers that are deemed secure.
    :returns:
        A list of Provider1 objects, created in no particular order.

    This function can be used to get a list of all available providers. Most
    applications will just want the default, regular list of providers, without
    bothering to restrict themselves to the secure subset.

    Those are the providers that can run jobs as root using the
    ``plainbox-trusted-launcher-1`` mechanism. Depending on the *policykit*
    Policy, those might start without prompting the user for the password. If
    you want to load only them, use the `only_secure` option.
    """
    if only_secure:
        from plainbox.impl.secure.providers.v1 import all_providers
    else:
        from plainbox.impl.providers.v1 import all_providers
    from plainbox.impl.providers import special
    all_providers.load()
    return [
        special.get_manifest(),
        special.get_exporters(),
        special.get_categories(),
    ] + all_providers.get_all_plugin_objects()
