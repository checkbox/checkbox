import os.path

from commands import getoutput

from hwtest.plugin import Plugin
from hwtest.report_helpers import createTypedElement


class ArchitectureInfo(Plugin):

    dpkg_path = "/usr/bin/dpkg"
    dpkg_command = "%s --print-architecture" % dpkg_path

    def gather(self):
        report = self._manager.report
        if not report.finalised:
            content = self.get_content()
            report.info['architecture'] = content

    def get_content(self):
        content = 'Unknown'

        # Debian and derivatives
        if os.path.exists(self.dpkg_path):
            content = getoutput(self.dpkg_command)

        return content

factory = ArchitectureInfo
