import os.path

from commands import getoutput

from hwtest.plugin import Plugin


class ArchitectureInfo(Plugin):

    dpkg_path = "/usr/bin/dpkg"
    dpkg_command = "%s --print-architecture" % dpkg_path

    def register(self, manager):
        super(ArchitectureInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "set-architecture"), message)

    def create_message(self):
        message = 'Unknown'

        # Debian and derivatives
        if os.path.exists(self.dpkg_path):
            message = getoutput(self.dpkg_command)

        return message


factory = ArchitectureInfo
