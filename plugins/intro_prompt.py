from hwtest.plugin import Plugin


class IntroPrompt(Plugin):

    def register(self, manager):
        super(IntroPrompt, self).register(manager)
        self._manager.reactor.call_on(("interface", "show-intro"), self.show_intro)

    def show_intro(self, interface):
        intro = interface.show_intro()


factory = IntroPrompt
