import md5
import logging

from hwtest.plugin import Plugin


class SystemKeyInfo(Plugin):

    def register(self, manager):
        super(SystemKeyInfo, self).register(manager)

        # System report should be generated early.
        for (rt, rh, rp) in [
             ("report", self.report, -10)]:
            self._manager.reactor.call_on(rt, rh, rp)

    def report(self):
        system_registry = self._manager.registry.hal.computer.system
        if "hardware" in system_registry:
            system_registry = system_registry.hardware

        fingerprint = md5.new()
        fingerprint.update(system_registry.vendor)
        fingerprint.update(system_registry.product)

        message = fingerprint.hexdigest()
        logging.info("System key: %s", message)
        self._manager.reactor.fire(("report", "system_key"), message)


factory = SystemKeyInfo
