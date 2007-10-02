from hwtest.plugin import Plugin


class GatherPrompt(Plugin):

    run_priority = -200

    def run(self):
        self._manager.reactor.fire(("interface", "show-gather"))


factory = GatherPrompt
