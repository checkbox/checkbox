'''apport general hook for checkbox

(c) 2009 Canonical Ltd.
Author: David Murphy <schwuk@ubuntu.com>
'''

from apport.hookutils import *
from os import path
from xdg.BaseDirectory import xdg_cache_home

def add_info(report):
    SYSTEM = path.join(xdg_cache_home, 'checkbox', 'system')
    SUBMISSION = path.join(xdg_cache_home, 'checkbox', 'submission')

    try:
        report['CheckboxSystem'] = open(SYSTEM).read()
    except IOError:
        pass

    try:
        report['CheckboxSubmission'] = open(SUBMISSION).read()
    except IOError:
        pass
