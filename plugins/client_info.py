import os

from hwtest.plugin import Plugin


class ClientInfo(Plugin):

    def register(self, manager):
        super(ClientInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = {}
        message["name"] = os.path.basename(self.config.parent.path)
        message["version"] = self.config.parent.get_defaults().version
        self._manager.reactor.fire(("report", "client"), message)


factory = ClientInfo
