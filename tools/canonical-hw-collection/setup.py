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

from setuptools import setup

setup(
    name="canonical-hw-collection",
    version="1.2",
    url="https://launchpad.net/checkbox/",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@canonical.com",
    license="GPLv3",
    platforms=["POSIX"],
    description=(
        "Tool for collecting hardware information and sending it to"
        " Canonical."),
    long_description="""
This tool collects various information about the hardware it is running on
and sends it to a server operated by Canonical. The tool can operate in two
modes that differ just on the destination of the data. See below for
details.

Note that unless you are a Canonical employee, or you've been asked to use
this tool by a Canonical employee, you will not have much use of the tool.
None of the data is not publicly available.""",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    install_requires=[
        'plainbox >= 0.23.dev0',
        'guacamole >= 0.9',
    ],
    scripts=[
        'canonical-hw-collection',
    ],
    include_package_data=True)
