import optparse, gettext
from gettext import gettext as _

from hwtest.plugin import Plugin
from hwtest.contrib.REThread import REThread


class UserInterface(object):
    '''Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract ui_* methods.'''

    title = "Hardware Testing"

    def __init__(self):
        self.gettext_domain = "hwtest"
        self.application = None
        self.questions = None

        gettext.textdomain(self.gettext_domain)

    def show_category(self):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_question(self, question, has_prev, has_next):
        raise NotImplementedError, "this function must be overridden by subclasses"

    def show_exchange(self, error):
        raise NotImplementedError, "this function must be overridden by subclasses"


class UserInterfacePlugin(Plugin):

    def __init__(self, config, user_interface):
        super(UserInterfacePlugin, self).__init__(config)
        self._user_interface = user_interface

    def register(self, manager):
        super(UserInterfacePlugin, self).register(manager)
        self._manager.reactor.call_on(("interface", "show-category"), self.show_category)
        self._manager.reactor.call_on(("interface", "show-question"), self.show_question)
        self._manager.reactor.call_on(("interface", "show-gather"), self.show_gather)
        self._manager.reactor.call_on(("interface", "show-exchange"), self.show_exchange)

    def show_category(self, category=None):
        if not category:
            category = self._user_interface.show_category()
        self._manager.reactor.fire(("prompt", "set-category"), category)

    def show_question(self, question, has_prev, has_next):
        direction = self._user_interface.show_question(question, has_prev,
                                                       has_next)
        self._manager.reactor.fire(("prompt", "set-direction"), direction)

    def do_gather(self):
        self._manager.reactor.fire("gather")

    def show_gather(self):
        self._user_interface.show_gather()
        thread = REThread(target=self.do_gather, name="do_gather")
        thread.start()
        while thread.isAlive():
            self._user_interface.pulse_gather()
            try:
                thread.join(0.1)
            except KeyboardInterrupt:
                sys.exit(1)
        thread.exc_raise()

    def show_exchange(self, email=None):
        # Prompt for email the first time unless it is provided.
        if not email:
            email = self._user_interface.show_exchange()
        while True:
            self._manager.reactor.fire(("report", "email"), email)
            self._manager.reactor.fire("exchange")
            error = self._manager.get_error()
            if not error:
                break
            # Always prompt for the email subsequent times.
            email = self._user_interface.show_exchange(error)
