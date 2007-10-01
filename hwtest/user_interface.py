import optparse, gettext
from gettext import gettext as _

from hwtest.plugin import Plugin


class UserInterface(object):
    '''Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract ui_* methods.'''

    def __init__(self):
        self.gettext_domain = 'hwtest'
        self.application = None
        self.questions = None

        gettext.textdomain(self.gettext_domain)

    def show_categories(self):
        raise NotImplementedError, 'this function must be overridden by subclasses'

    def show_question(self, question, has_prev, has_next):
        raise NotImplementedError, 'this function must be overridden by subclasses'

    def show_authentication(self, error):
        raise NotImplementedError, 'this function must be overridden by subclasses'


class UserInterfacePlugin(Plugin):

    def __init__(self, user_interface):
        super(UserInterfacePlugin, self).__init__()
        self._user_interface = user_interface

    def register(self, manager):
        super(UserInterfacePlugin, self).register(manager)
        self._manager.reactor.call_on(("interface", "categories"), self.show_categories)
        self._manager.reactor.call_on(("interface", "question"), self.show_question)
        self._manager.reactor.call_on(("interface", "authentication"), self.show_authentication)

    def show_categories(self):
        category = self._user_interface.show_categories()
        self._manager.reactor.fire(("question", "category"), category)

    def show_question(self, question, has_prev, has_next):
        direction = self._user_interface.show_question(question, has_prev,
                                                       has_next)
        self._manager.reactor.fire(("question", "direction"), direction)

    def show_authentication(self):
        error = None
        while True:
            self._manager.report.secure_id = self._user_interface.show_authentication(error)
            self._manager.reactor.fire("authentication")
            error = self._manager.get_error()
            if not error:
                break
