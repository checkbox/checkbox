from hwtest.plugin import Plugin

from hwtest.report_helpers import createTypedElement


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

    def gather_information(self):
        report = self._manager.report
        content = self._distribution_info 

        # Store summary information
        report.info['distribution'] = content['distributor-id']
        report.info['distroseries'] = content['release']

        # Store data in report
        createTypedElement(report, 'distribution', report.root, None,
                           content, True)

    def run(self):
        fd = file(self._source_filename, "r")
        for line in fd.readlines():
            key, value = line.split("=")
            if key in self.lsb_release_keys:
                key = self.lsb_release_keys[key.strip()]
                value = value.strip().strip('"')
                self._distribution_info[key] = value


factory = DistributionInfo
