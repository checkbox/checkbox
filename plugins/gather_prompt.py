from hwtest.plugin import Plugin


class GatherPrompt(Plugin):

    def register(self, manager):
        super(GatherPrompt, self).register(manager)
        self._done = False

        self._manager.reactor.call_on(("prompt", "gather"), self.prompt_gather)
 
    def prompt_gather(self, interface):
        if not self._done:
            interface.do_wait(lambda: self._manager.reactor.fire("gather"),
                "Gathering information from your system...")
            self._done = True


factory = GatherPrompt
