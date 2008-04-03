#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
import sys
import gettext

from hwtest.contrib.REThread import REThread
from hwtest.iterator import NEXT


class UserInterface(object):
    """Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract show_* methods."""

    def __init__(self, config):
        self.config = config

        self.direction = NEXT
        self.gettext_domain = "hwtest"
        gettext.textdomain(self.gettext_domain)

    def do_function(self, function):
        thread = REThread(target=function, name="do_function")
        thread.start()

        while thread.isAlive():
            self.show_pulse()
            try:
                thread.join(0.1)
            except KeyboardInterrupt:
                sys.exit(1)
        thread.exc_raise()

    def show_wait(self, message, function):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"

    def show_pulse(self):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"

    def show_intro(self, title, text):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"

    def show_category(self, title, text, category):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"

    def show_test(self, test, run_test):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"

    def show_exchange(self, authentication, message, error):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"

    def show_final(self, message):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"

    def show_error(self, title, text):
        raise NotImplementedError, \
            "this function must be overridden by subclasses"
