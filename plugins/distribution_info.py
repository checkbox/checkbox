from hwtest.plugin import Plugin
from hwtest.report_helpers import createElement, createTypedElement


class DistributionInfo(Plugin):

    lsb_release_keys = {"DISTRIB_ID": "distributor-id",
                        "DISTRIB_DESCRIPTION": "description",
                        "DISTRIB_RELEASE": "release",
                        "DISTRIB_CODENAME": "codename"}

    def __init__(self, source_filename="/etc/lsb-release"):
        super(DistributionInfo, self).__init__()
        self._source_filename = source_filename

    def gather(self):
        report = self._manager.report
        if not report.finalised:
            content = self.get_content()

            # Store summary information
            report.info['distribution'] = content['distributor-id']
            report.info['distroseries'] = content['release']

            # Store data in report
            software = getattr(report, 'software', None)
            if software is None:
                software = createElement(report, 'software', report.root)
                report.software = software
            createTypedElement(report, 'lsbrelease', software, None,
                               content, True)

    def get_content(self):
        content = {}
        fd = file(self._source_filename, "r")
        for line in fd.readlines():
            key, value = line.split("=")
            if key in self.lsb_release_keys:
                key = self.lsb_release_keys[key.strip()]
                value = value.strip().strip('"')
                content[key] = value

        return content


factory = DistributionInfo
