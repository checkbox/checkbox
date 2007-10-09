from hwtest.plugin import Plugin


class ExchangePrompt(Plugin):

    priority = -100

    def run(self):
        self._manager.reactor.fire(("interface", "show-exchange"))


factory = ExchangePrompt
