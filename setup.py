#!/usr/bin/env python

from glob import glob
from distutils.core import setup

from hwtest.config import Config


config = Config("examples/hwtest.conf")


setup(
    name = 'hwtest',
    version = config.get_defaults().version,
    author = 'Marc Tardif',
    author_email = 'marc.tardif@canonical.com',
    license = 'GPL',
    description = 'Hardware Test',
    long_description = '''
This project provides an interfaces for gathering hardware details
and prompting the user for tests. This information can then be sent
to Launchpad.
''',
    data_files=[
        ('share/applications/', ['gtk/hwtest-gtk.desktop']),
        ('share/pixmaps/', ['gtk/hwtest-gtk.xpm']),
        ('share/hwtest/data/', glob('data/*')),
        ('share/hwtest/install/', glob('install/*')),
        ('share/hwtest/plugins/', glob('plugins/*.py')),
        ('share/hwtest/registries/', glob('registries/*.py')),
        ('share/hwtest/questions/', glob('questions/*')),
        ('share/hwtest/scripts/', glob('scripts/*')),
        ('share/hwtest-gtk/', ['gtk/hwtest-gtk.glade'] + glob('gtk/*.png'))],
    scripts=['bin/hwtest'],
    packages=['hwtest', 'hwtest.contrib', 'hwtest.lib', 'hwtest.reports',
        'hwtest_cli', 'hwtest_gtk']
)
