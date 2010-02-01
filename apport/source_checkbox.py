'''apport package hook for checkbox

(c) 2009 Canonical Ltd.
Author: David Murphy <schwuk@ubuntu.com>
'''

from apport.hookutils import *
from os import path
from xdg.BaseDirectory import xdg_cache_home


def add_info(report):
    USER_LOG = path.join(xdg_cache_home, 'checkbox', 'checkbox.log')
    apport.hookutils.attach_file_if_exists(report, USER_LOG)
    apport.hookutils.attach_file_if_exists(report, '/var/log/checkbox.log')

    SUBMISSION = path.join(xdg_cache_home, 'checkbox', 'submission.xml')
    apport.hookutils.attach_file_if_exists(report, SUBMISSION)
