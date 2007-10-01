from hwtest.plugin import Plugin


class CategoryInfo(Plugin):

    def register(self, manager):
        self._manager = manager
        self._manager.reactor.call_on("run", self.run, -300)

    def run(self):
        self._manager.reactor.fire(("interface", "categories"))


factory = CategoryInfo
