from hwtest.plugin import Plugin


class ErrorPrompt(Plugin):

    def register(self, manager):
        super(ErrorPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "error"),
            self.prompt_error)

    def prompt_error(self, interface, title, text):
        interface.show_error(title, text)


factory = ErrorPrompt
