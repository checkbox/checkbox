from hwtest.plugin import Plugin


class GatherPrompt(Plugin):

    priority = -200

    def run(self):
        self._manager.reactor.fire(("interface", "show-gather"))


factory = GatherPrompt
