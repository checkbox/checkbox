from hwtest.plugin import Plugin
from hwtest.package import PackageManager


class PackageInfo(Plugin):

    def __init__(self, package_manager=None):
        super(PackageInfo, self).__init__()
        self._package_manager = package_manager or PackageManager()

    def register(self, manager):
        self._manager = manager
        self._manager.reactor.call_on("gather_information", self.gather_information)
        self._manager.reactor.call_on("run", self.run)

    def create_message(self):
        package_info = self._package_info
        self._package_info = []
        return {"type": "package-info", "package-info": package_info}

    def gather_information(self):
        message = self.create_message()
        if len(message["package-info"]):
               self._manager.message_store.add(message)

    def run(self):
        self._package_info = []

        for package in self._package_manager.get_packages():
            properties = package.properties
            self._package_info.append(properties)


factory = PackageInfo
