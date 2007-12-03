import os

from hwtest.plugin import Plugin


class PermissionPrompt(Plugin):

    priority = -500

    def run(self):
        if os.getuid() != 0:
            self._manager.reactor.fire(("interface", "show-error-message"),
                "Invalid permission", "Application must be run as root")
            self._manager.reactor.stop()


factory = PermissionPrompt
