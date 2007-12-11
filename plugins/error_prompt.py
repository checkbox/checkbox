from hwtest.plugin import Plugin


class ErrorPrompt(Plugin):

    def register(self, manager):
        super(ErrorPrompt, self).register(manager)
        self._manager.reactor.call_on(("interface", "show-error"),
            self.show_error)

    def show_error(self, interface, title, text):
        interface.show_error_message(title, text)


factory = ErrorPrompt
