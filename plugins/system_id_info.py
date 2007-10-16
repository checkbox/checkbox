from hwtest.system import get_system_id
from hwtest.plugin import Plugin


class SystemIdInfo(Plugin):

    def register(self, manager):
        super(SystemIdInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = get_system_id()
        self._manager.reactor.fire(("report", "system_id"), message)


factory = SystemIdInfo
