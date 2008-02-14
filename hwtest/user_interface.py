import sys
import gettext

from hwtest.contrib.REThread import REThread
from hwtest.iterator import NEXT


class UserInterface(object):
    '''Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract ui_* methods.'''

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
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_pulse(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_intro(self, title, text):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_category(self, title, text, category):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_question(self, question, run_question):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_exchange(self, authentication, message, error):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_final(self, message):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_error(self, title, text):
        raise NotImplementedError, "this function must be overridden by subclasses"
