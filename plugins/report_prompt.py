from hwtest.plugin import Plugin
from hwtest.iterator import PREV


class ReportPrompt(Plugin):

    def register(self, manager):
        super(ReportPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "report"), self.prompt_report)
 
    def prompt_report(self, interface):
        if interface.direction == PREV:
            return

        # This could show a progress bar but it's very fast since most
        # information is available from the gather event type.
        self._manager.reactor.fire("report")


factory = ReportPrompt
