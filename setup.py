#!/usr/bin/env python

from glob import glob
from distutils.core import setup

from hwtest import VERSION


project_name = 'hwtest'

setup(
    name = project_name,
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
        ('share/applications/', ['gtk/hwtest.desktop']),
        ('share/pixmaps/', ['gtk/hwtest.xpm']),
        ('share/hwtest/', ['questions.txt']),
        ('share/hwtest/gtk/', ['gtk/hwtest-gtk.glade'] + glob('gtk/*.png')),
        ('share/hwtest/data/', glob('data/*'))],
    scripts=['gtk/hwtest-gtk'],
    packages=['hwtest', 'hwtest.contrib', 'hwtest.lib', 'hwtest.plugins']
)
