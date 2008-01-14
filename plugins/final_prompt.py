from hwtest.plugin import Plugin


class FinalPrompt(Plugin):

    def register(self, manager):
        super(FinalPrompt, self).register(manager)
        for (rt, rh) in [
             (("prompt", "final"), self.prompt_final)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_final(self, interface):
        interface.show_final()


factory = FinalPrompt
