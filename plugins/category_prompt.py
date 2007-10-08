from hwtest.plugin import Plugin


class CategoryPrompt(Plugin):

    priority = -400

    def run(self):
        self._manager.reactor.fire(("interface", "show-categories"))


factory = CategoryPrompt
