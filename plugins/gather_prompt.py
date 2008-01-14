from hwtest.plugin import Plugin


class GatherPrompt(Plugin):

    def register(self, manager):
        super(GatherPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "gather"), self.prompt_gather)
 
    def prompt_gather(self, interface):
        interface.do_wait(lambda: self._manager.reactor.fire("gather"),
            "Gathering information from your system...")


factory = GatherPrompt
