import gettext


class UserInterface(object):
    '''Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract ui_* methods.'''

    title = "Hardware Testing"

    def __init__(self, config):
        self.config = config

        self.application = None
        self.questions = None

        self.gettext_domain = "hwtest"
        gettext.textdomain(self.gettext_domain)

    def show_category(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_question(self, question, has_prev, has_next):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_exchange(self, error):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_error_message(self, error):
        raise NotImplementedError, "this function must be overridden by subclasses"
