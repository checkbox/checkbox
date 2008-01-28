import re

from gettext import gettext as _

from hwtest.plugin import Plugin
from hwtest.iterator import PREV


class ExchangePrompt(Plugin):

    optional_attributes = ["email"]

    def register(self, manager):
        super(ExchangePrompt, self).register(manager)
        self._email = self.config.email
        self._email_regexp = re.compile(r"^\S+@\S+.\S+$", re.I)

        for (rt, rh) in [
             (("prompt", "exchange"), self.prompt_exchange)]:
            self._manager.reactor.call_on(rt, rh)
 
    def prompt_exchange(self, interface):
        error = None
        while True:
            self._email = interface.show_exchange(self._email, error=error)

            if interface.direction == PREV:
                break
            elif not self._email_regexp.match(self._email):
                error = _("Email address must be in a proper format.")
            else:
                self._manager.reactor.fire(("report", "email"), self._email)
                interface.do_wait(
                    _("Exchanging information with the server..."),
                    lambda: self._manager.reactor.fire("exchange"))
                error = self._manager.get_error()
                if not error:
                    break


factory = ExchangePrompt
