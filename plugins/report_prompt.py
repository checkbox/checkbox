from gettext import gettext as _

from hwtest.plugin import Plugin
from hwtest.iterator import PREV


class ReportPrompt(Plugin):

    def register(self, manager):
        super(ReportPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "report"), self.prompt_report)
 
    def prompt_report(self, interface):
        if interface.direction != PREV:
            interface.show_wait(_("Building report..."),
                lambda: self._manager.reactor.fire("report"))


factory = ReportPrompt
