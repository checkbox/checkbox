import sys
import gettext

from hwtest.contrib.REThread import REThread


class UserInterface(object):
    '''Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract ui_* methods.'''

    def __init__(self, config):
        self.config = config

        self.application = None
        self.questions = None

        self.gettext_domain = "hwtest"
        gettext.textdomain(self.gettext_domain)

    def do_wait(self, function, message):
        self.show_wait(message)
        thread = REThread(target=function, name="do_wait")
        thread.start()
        while thread.isAlive():
            self.show_pulse()
            try:
                thread.join(0.1)
            except KeyboardInterrupt:
                sys.exit(1)
        thread.exc_raise()

    def show_wait(self, message):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_pulse(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_category(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_question(self, question, has_prev, has_next):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_exchange(self, message, error):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_final(self, message):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_error_message(self, title, text):
        raise NotImplementedError, "this function must be overridden by subclasses"
