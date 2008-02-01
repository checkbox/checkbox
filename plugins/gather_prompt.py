from gettext import gettext as _

from hwtest.plugin import Plugin


class GatherPrompt(Plugin):

    def register(self, manager):
        super(GatherPrompt, self).register(manager)
        self._done = False

        self._manager.reactor.call_on(("prompt", "gather"), self.prompt_gather)
 
    def prompt_gather(self, interface):
        if not self._done:
            interface.show_wait(_("Gathering information from your system..."),
                lambda: self._manager.reactor.fire("gather"))
            self._done = True


factory = GatherPrompt
