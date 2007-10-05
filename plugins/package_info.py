from hwtest.plugin import Plugin
from hwtest.package import PackageManager


class PackageInfo(Plugin):

    def __init__(self, config, package_manager=None):
        super(PackageInfo, self).__init__(config)
        self._package_manager = package_manager or PackageManager()

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "set-packages"), message)

    def create_message(self):
        message = []

        for package in self._package_manager.get_packages():
            properties = package.properties
            message.append(properties)

        return message


factory = PackageInfo
