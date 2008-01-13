import re

from hwtest.plugin import Plugin


class ExchangePrompt(Plugin):

    attributes = ["email"]

    def register(self, manager):
        super(ExchangePrompt, self).register(manager)
        self._manager.reactor.call_on(("interface", "show-exchange"),
            self.show_exchange)
 
    def show_exchange(self, interface):
        email_regexp = re.compile(r"^\S+@\S+.\S+$", re.I)
        email = self.config.email

        # Prompt for email the first time unless it is provided.
        if not email:
            email = interface.show_exchange()

        while True:
            if not email_regexp.match(email):
                error = "Email address must be in a proper format."

            else:
                self._manager.reactor.fire(("report", "email"), email)
                interface.do_wait(lambda: self._manager.reactor.fire("exchange"),
                    "Exchanging information with the server...")
                error = self._manager.get_error()
                if not error:
                    break

            # Always prompt for the email subsequent times.
            email = interface.show_exchange(error=error)


factory = ExchangePrompt
