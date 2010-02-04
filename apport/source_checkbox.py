'''apport package hook for checkbox

(c) 2009 Canonical Ltd.
Author: David Murphy <schwuk@ubuntu.com>
'''
import os

from apport.hookutils import attach_file_if_exists


def add_info(report):
    HOME = os.environ.get('HOME', '/')
    CACHE_HOME = os.environ.get('XDG_CACHE_HOME',
        os.path.join(HOME, '.cache'))

    USER_LOG = os.path.join(CACHE_HOME, 'checkbox', 'checkbox.log')
    attach_file_if_exists(report, USER_LOG)
    attach_file_if_exists(report, '/var/log/checkbox.log')

    SUBMISSION = os.path.join(CACHE_HOME, 'checkbox', 'submission.xml')
    attach_file_if_exists(report, SUBMISSION)
