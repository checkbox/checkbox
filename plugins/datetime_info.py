from datetime import datetime

from hwtest.plugin import Plugin


class DatetimeInfo(Plugin):

    def register(self, manager):
        super(DatetimeInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = str(datetime.utcnow()).split(".")[0]
        self._manager.reactor.fire(("report", "datetime"), message)


factory = DatetimeInfo
