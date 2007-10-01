from hwtest.plugin import Plugin


class AuthenticationInfo(Plugin):

    def register(self, manager):
        self._manager = manager
        self._manager.reactor.call_on("run", self.run, -100)

    def run(self):
        self._manager.reactor.fire(("interface", "authentication"))


factory = AuthenticationInfo
