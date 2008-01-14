from hwtest.plugin import Plugin


class IntroPrompt(Plugin):

    def register(self, manager):
        super(IntroPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "intro"), self.prompt_intro)

    def prompt_intro(self, interface):
        interface.show_intro()


factory = IntroPrompt
