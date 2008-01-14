import os

from hwtest.plugin import Plugin


class PermissionPrompt(Plugin):

    def register(self, manager):
        super(PermissionPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "permission"),
            self.prompt_permission)

    def prompt_permission(self, interface):
        if os.getuid() != 0:
            self._manager.reactor.fire(("prompt", "error"), interface,
                "Invalid permission", "Application must be run as root")
            self._manager.reactor.stop()


factory = PermissionPrompt
