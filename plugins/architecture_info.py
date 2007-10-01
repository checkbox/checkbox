import os.path

from commands import getoutput

from hwtest.plugin import Plugin
from hwtest.report_helpers import createTypedElement


class ArchitectureInfo(Plugin):

    dpkg_path = "/usr/bin/dpkg"
    dpkg_command = "%s --print-architecture" % dpkg_path

    def __init__(self):
        super(ArchitectureInfo, self).__init__()
        self._architecture_info = ''
        
    def gather(self):
        report = self._manager.report
        if not report.finalised:
            report.info['architecture'] = self._architecture_info

    def run(self):
        self._architecture_info = 'Unknown'

        # Debian and derivatives
        if os.path.exists(self.dpkg_path):
            self._architecture_info = getoutput(self.dpkg_command)


factory = ArchitectureInfo
