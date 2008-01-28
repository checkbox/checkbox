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

        self.application = None
        self.questions = None
        self.direction = NEXT

        self.gettext_domain = "hwtest"
        gettext.textdomain(self.gettext_domain)

    def do_wait(self, message, function):
        self.show_wait_begin(message)
        thread = REThread(target=function, name="do_wait")
        thread.start()
        while thread.isAlive():
            self.show_pulse()
            try:
                thread.join(0.1)
            except KeyboardInterrupt:
                sys.exit(1)
        thread.exc_raise()
        self.show_wait_end()

    def do_question(self, message, question):
        if str(question.command):
            self.show_question_begin(message)
            thread = REThread(target=question.command, name="do_question")
            thread.start()
            while thread.isAlive():
                self.show_pulse()
                try:
                    thread.join(0.1)
                except KeyboardInterrupt:
                    sys.exit(1)
            thread.exc_raise()

        question.description()
        self.show_question_end(question)

    def show_wait_begin(self, message):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_wait_end(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_pulse(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_intro(self, title, text):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_category(self, title, text, category):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_question_begin(self, message):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_question_end(self, question):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_exchange(self, authentication, message, error):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_final(self, message):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_error(self, title, text):
        raise NotImplementedError, "this function must be overridden by subclasses"
