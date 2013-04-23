#
# This file is part of Checkbox.
#
# Copyright 2008-2012 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import gettext
import logging
import os
import pwd
import re
import subprocess
import webbrowser

from checkbox.contrib.REThread import REThread
from checkbox.lib.environ import (
    add_variable,
    get_variable,
    remove_variable,
    )
from checkbox.job import (
    FAIL,
    PASS,
    UNINITIATED,
    UNRESOLVED,
    UNSUPPORTED,
    UNTESTED,
    )
from checkbox.reactor import StopAllException


NEXT = 1
PREV = -1

YES_ANSWER = "yes"
NO_ANSWER = "no"
SKIP_ANSWER = "skip"
ALL_ANSWERS = [YES_ANSWER, NO_ANSWER, SKIP_ANSWER]

ANSWER_TO_STATUS = {
    NO_ANSWER: FAIL,
    YES_ANSWER: PASS,
    SKIP_ANSWER: UNTESTED}

STATUS_TO_ANSWER = {
    FAIL: NO_ANSWER,
    PASS: YES_ANSWER,
    UNINITIATED: SKIP_ANSWER,
    UNRESOLVED: NO_ANSWER,
    UNSUPPORTED: SKIP_ANSWER,
    UNTESTED: SKIP_ANSWER}

CONTINUE_ANSWER = 'Continue'
RERUN_ANSWER = 'Rerun'
RESTART_ANSWER = 'Restart'


class UserInterface:
    """Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract show_* methods."""

    def __init__(self, title, data_path=None):
        self.title = title
        self.data_path = data_path
        self.progress = None
        self.ui_flags = {}

        self.report_url = None
        self.direction = NEXT
        self.gettext_domain = "checkbox"
        gettext.textdomain(self.gettext_domain)

    def show_info(self, text, options=[], default=None):
        logging.info(text)
        return default

    def show_error(
        self, primary_text, secondary_text=None, detailed_text=None):
        text = filter(None, [primary_text, secondary_text, detailed_text])
        text = '\n'.join(text)
        logging.error(text)
        raise StopAllException("Error: %s" % text)

    def show_warning(
        self, primary_text, secondary_text=None, detailed_text=None):
        try:
            self.show_error(primary_text, secondary_text, detailed_text)
        except StopAllException:
            # The only difference with show_error for now is that warnings
            # don't stop the reactor.
            pass

    def show_progress(self, message, function, *args, **kwargs):
        self.show_progress_start(message)

        thread = REThread(target=function, name="progress",
            args=args, kwargs=kwargs)
        thread.start()

        while thread.isAlive():
            self.show_progress_pulse()
            thread.join(0.1)
        thread.exc_raise()

        self.show_progress_stop()
        return thread.return_value()

    def show_progress_start(self, message):
        return

    def show_progress_stop(self):
        return

    def show_progress_pulse(self):
        return

    def show_text(self, text, previous=None, next=None):
        return

    def show_entry(self, text, value, label=None, submitToHexr=False, previous=None, next=None):
        return value

    def show_check(self, text, options=[], default=[]):
        return default

    def show_radio(self, text, options=[], default=None):
        return default

    def show_tree(self, text, options={}, default={}, deselect_warning=""):
        return default

    def show_test(self, test, runner):
        test["status"] = UNTESTED
        test["data"] = "Manual test run non interactively."

    def show_url(self, url):
        """Open the given URL in a new browser window.

        Display an error dialog if everything fails."""

        # If we are called through sudo, determine the real user id and
        # run the browser with it to get the user's web browser settings.
        try:
            uid = int(get_variable("SUDO_UID"))
            gid = int(get_variable("SUDO_GID"))
            sudo_prefix = ["sudo", "-H", "-u", "#%s" % uid]
        except (TypeError):
            uid = os.getuid()
            gid = None
            sudo_prefix = []

        # if ksmserver is running, try kfmclient
        try:
            if (os.getenv("DISPLAY") and
                    subprocess.call(
                        ["pgrep", "-x", "-u", str(uid), "ksmserver"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0):
                subprocess.Popen(sudo_prefix + ["kfmclient", "openURL", url])
                return
        except OSError:
            pass

        # if gnome-session is running, try gnome-open; special-case
        # firefox (and more generally, mozilla browsers) and epiphany
        # to open a new window with respectively -new-window and
        # --new-window; special-case chromium-browser to allow file://
        # URLs as needed by the checkbox report.
        try:
            if (os.getenv("DISPLAY") and
                subprocess.call(
                    ["pgrep", "-x", "-u", str(uid), "gnome-panel|gconfd-2"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0):
                from gi.repository import Gio

                preferred_xml_app = Gio.app_info_get_default_for_type(
                    "application/xml", False)
                if preferred_xml_app:
                    preferred_browser = preferred_xml_app.get_executable()
                    browser = re.match(
                        "((firefox|seamonkey|flock)[^\s]*)",
                        preferred_browser)
                    if browser:
                        subprocess.Popen(
                            sudo_prefix +
                            [browser.group(0), "-new-window", url])
                        return

                    browser = re.match("(epiphany[^\s]*)", preferred_browser)
                    if browser:
                        subprocess.Popen(
                            sudo_prefix +
                            [browser.group(0), "--new-window", url])
                        return

                    browser = re.match(
                        "(chromium-browser[^\s]*)", preferred_browser)
                    if browser:
                        subprocess.Popen(
                            sudo_prefix +
                            [browser.group(0),
                                "--allow-file-access-from-files", url])
                        return

                    subprocess.Popen(
                        sudo_prefix +
                        [preferred_browser % url], shell=True)
                    return

                subprocess.Popen(sudo_prefix + ["gnome-open", url])
                return
        except OSError:
            pass

        # fall back to webbrowser
        if uid and gid:
            os.setgroups([gid])
            os.setgid(gid)
            os.setuid(uid)
            remove_variable("SUDO_USER")
            add_variable("HOME", pwd.getpwuid(uid).pw_dir)

        webbrowser.open(url, new=True, autoraise=True)
        return

    def show_report(self, text, results):
        """
        Display a report of all test case results
        and make it possible to modify them
        """
        raise NotImplementedError

    def update_status(self, job):
        """
        If implemented, it will be called after each job finishes.
        The passed Job object can be used to update in-UI status
        about each job.
        """
        pass
