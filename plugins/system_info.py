import md5
import logging

from hwtest.plugin import Plugin


class SystemInfo(Plugin):

    optional_attributes = ["system_id"]

    def register(self, manager):
        super(SystemInfo, self).register(manager)

        # System report should be generated early.
        for (rt, rh, rp) in [
             ("report", self.report, -10)]:
            self._manager.reactor.call_on(rt, rh, rp)

    def report(self):
        system_registry = self._manager.registry.hal.computer.system
        if "hardware" in system_registry:
            system_registry = system_registry.hardware

        system_id = self.config.system_id
        if not system_id:
            fingerprint = md5.new()
            fingerprint.update(system_registry.vendor)
            fingerprint.update(system_registry.product)
            system_id = fingerprint.hexdigest()

        message = system_id
        logging.info("System ID: %s", message)
        self._manager.reactor.fire(("report", "system_id"), message)


factory = SystemInfo
