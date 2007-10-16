from hwtest.plugin import Plugin
from hwtest.package import PackageManager


class PackageInfo(Plugin):

    def __init__(self, config, package_manager=None):
        super(PackageInfo, self).__init__(config)
        self._package_manager = package_manager or PackageManager()

    def register(self, manager):
        super(PackageInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "package"), message)

    def create_message(self):
        return [p.properties for p in self._package_manager.get_packages()]


factory = PackageInfo
