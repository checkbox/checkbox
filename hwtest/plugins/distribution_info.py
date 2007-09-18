from hwtest.plugin import Plugin


class DistributionInfo(Plugin):

    lsb_release_keys = {"DISTRIB_ID": "distributor-id",
                        "DISTRIB_DESCRIPTION": "description",
                        "DISTRIB_RELEASE": "release",
                        "DISTRIB_CODENAME": "codename"}

    def __init__(self, source_filename="/etc/lsb-release"):
        self._source_filename = source_filename
        self._distribution_info = {}

    def register(self, manager):
        self._manager = manager
        self._persist = self._manager.persist.root_at("distribution-info")
        self._manager.reactor.call_on("gather_information", self.gather_information)
        self._manager.reactor.call_on("run", self.run)

    def create_message(self):
        distribution_info = self._distribution_info
        self._distribution_info = {}
        return {"type": "distribution-info", "distribution-info": distribution_info}

    def gather_information(self):
        message = self.create_message()
        if len(message["distribution-info"]):
               self._manager.message_store.add(message)

    def run(self):
        fd = file(self._source_filename, "r")
        for line in fd.readlines():
            key, value = line.split("=")
            if key in self.lsb_release_keys:
                key = self.lsb_release_keys[key.strip()]
                value = value.strip().strip('"')
                self._distribution_info[key] = value
