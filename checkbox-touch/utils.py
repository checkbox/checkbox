#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2016 Canonical Ltd.
# Written by:
#   Maciej Kisielewski <maciej.kisielewski@canonical.com>
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
Common functions used by build-me and get-libs.
"""

import apt
import apt_pkg
import collections
import os
import shutil
import subprocess
import tempfile
import urllib.request


def rsync_tree(src, dest, preserve_symlinks=False):
    """
    copy files from src to dest using rsync
    """
    links_option = "-l" if preserve_symlinks else "-L"
    parent_dir = os.path.split(os.path.abspath(dest))[0]
    # adding trailing slash if it's not already there
    src = os.path.join(src, '')
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    subprocess.check_call(["rsync", "-a", links_option, src, dest])


def prepare_uris(packages):
    """Prepare cache and generate URIs for all packages."""
    uris = dict()
    Source = collections.namedtuple('Source', ['uri', 'repositories'])
    sources = [Source('http://ports.ubuntu.com/ubuntu-ports',
                      'main restricted universe'),
               Source('http://ppa.launchpad.net/checkbox-dev/ppa/ubuntu',
                      'main')]
    with tempfile.TemporaryDirectory() as tmp:
        new_etc_apt = os.path.join(tmp, 'etc', 'apt')
        os.makedirs(new_etc_apt)
        # copy over trusted.gpg
        shutil.copyfile('/etc/apt/trusted.gpg',
                        os.path.join(new_etc_apt, 'trusted.gpg'))
        # copy over additional keyrings
        if os.path.exists('/etc/apt/trusted.gpg.d'):
            shutil.copytree('/etc/apt/trusted.gpg.d',
                            os.path.join(new_etc_apt, 'trusted.gpg.d'))
        sources_list = open(os.path.join(new_etc_apt, 'sources.list'), "w")
        for source in sources:
            sources_list.write(
                "deb [arch=armhf] {uri} wily {repositories}\n".format(
                    uri=source.uri, repositories=source.repositories))
        sources_list.close()
        apt_pkg.config["Apt::Architecture"] = 'armhf'
        cache = apt.Cache(rootdir=tmp)
        cache.update()
        cache.open(None)
        for pkg in packages:
            if pkg not in cache or len(cache[pkg].versions) < 1:
                # package not found
                raise Exception('Package {0} not found!'.format(pkg))
            # use first uri available
            uris[pkg] = cache[pkg].versions[0].uri
    # return filled dictionary
    return uris


def get_package_from_url_and_extract(url, target_dir):
    filename = os.path.join(target_dir, url.split('/')[-1])
    print('retrieving {0}'.format(url))
    urllib.request.urlretrieve(url, filename)
    subprocess.check_call(["dpkg", "-x", filename, target_dir])
