#!/usr/bin/env python

from glob import glob
from distutils.core import setup

from hwtest import VERSION


setup(
    name = 'hwtest',
    version = VERSION,
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
        ('share/hwtest/plugins/', glob('plugins/*')),
        ('share/hwtest/gtk/', ['gtk/hwtest-gtk.glade'] + glob('gtk/*.png')),
        ('share/hwtest/gtk/plugins/', glob('gtk/plugins/*')),
        ('share/hwtest/cli/plugins/', glob('cli/plugins/*'))],
    scripts=['cli/hwtest-cli', 'gtk/hwtest-gtk'],
    packages=['hwtest', 'hwtest.contrib', 'hwtest.lib']
)
