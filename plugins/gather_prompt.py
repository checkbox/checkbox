import sys

from hwtest.contrib.REThread import REThread

from hwtest.plugin import Plugin


class GatherPrompt(Plugin):

    def register(self, manager):
        super(GatherPrompt, self).register(manager)
        self._manager.reactor.call_on(("interface", "show-gather"),
            self.show_gather)
 
    def do_gather(self):
        self._manager.reactor.fire("gather")

    def show_gather(self, interface):
        interface.show_wait("Please wait while information is being"
            " gathered from your system.")
        thread = REThread(target=self.do_gather, name="do_gather")
        thread.start()
        while thread.isAlive():
            interface.pulse_wait()
            try:
                thread.join(0.1)
            except KeyboardInterrupt:
                sys.exit(1)
        thread.exc_raise()


factory = GatherPrompt
