import os

from gettext import gettext as _

from hwtest.plugin import Plugin


class PermissionPrompt(Plugin):

    def register(self, manager):
        super(PermissionPrompt, self).register(manager)
        for (rt, rh) in [
             (("prompt", "permission"), self.prompt_permission)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_permission(self, interface):
        if os.getuid() != 0:
            self._manager.reactor.fire(("prompt", "error"), interface,
                _("Administrator Access Needed"),
                _("You need to be an administrator to use this application."))
            self._manager.reactor.stop_all()


factory = PermissionPrompt
