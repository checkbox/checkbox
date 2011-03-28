'''apport general hook for checkbox

(c) 2009 Canonical Ltd.
Author: David Murphy <schwuk@ubuntu.com>
'''
import os


def add_info(report):
    HOME = os.environ.get('HOME', '/')
    CACHE_HOME = os.environ.get('XDG_CACHE_HOME',
        os.path.join(HOME, '.cache'))
    SYSTEM = os.path.join(CACHE_HOME, 'checkbox', 'system')
    SUBMISSION = os.path.join(CACHE_HOME, 'checkbox', 'submission')

    try:
        report['CheckboxSystem'] = open(SYSTEM).read()
    except IOError:
        pass

    try:
        report['CheckboxSubmission'] = open(SUBMISSION).read()
    except IOError:
        pass
