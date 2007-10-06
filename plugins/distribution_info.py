from hwtest.plugin import Plugin


class DistributionInfo(Plugin):

    lsb_source = "/etc/lsb-release"
    lsb_release_keys = {"DISTRIB_ID": "distributor-id",
                        "DISTRIB_DESCRIPTION": "description",
                        "DISTRIB_RELEASE": "release",
                        "DISTRIB_CODENAME": "codename"}

    def register(self, manager):
        super(DistributionInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "set-distribution"), message)

    def create_message(self):
        message = {}
        fd = file(self.lsb_source, "r")
        for line in fd.readlines():
            key, value = line.split("=")
            if key in self.lsb_release_keys:
                key = self.lsb_release_keys[key.strip()]
                value = value.strip().strip('"')
                message[key] = value

        return message


factory = DistributionInfo
