import re

from hwtest.plugin import Plugin
from hwtest.iterator import NEXT, PREV


class ExchangePrompt(Plugin):

    attributes = ["email"]

    def register(self, manager):
        super(ExchangePrompt, self).register(manager)
        self._email = self.config.email
        self._email_regexp = re.compile(r"^\S+@\S+.\S+$", re.I)

        for (rt, rh) in [
             (("prompt", "exchange"), self.prompt_exchange)]:
            self._manager.reactor.call_on(rt, rh)
 
    def prompt_exchange(self, interface):
        # Prompt for email the first time unless it is provided.
        self._email = interface.show_exchange(self._email or "")

        error = None
        while True:
            if not self._email or interface.direction == PREV:
                break
            elif not self._email_regexp.match(self._email):
                error = "Email address must be in a proper format."
            elif interface.direction == NEXT:
                self._manager.reactor.fire(("report", "email"), self._email)
                interface.do_wait(lambda: self._manager.reactor.fire("exchange"),
                    "Exchanging information with the server...")
                error = self._manager.get_error()
                if not error:
                    break

            # Always prompt for the email subsequent times.
            self._email = interface.show_exchange(self._email, error=error)


factory = ExchangePrompt
