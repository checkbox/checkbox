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
        system_id = self.config.system_id
        if not system_id:
            system = self._manager.registry.hal.computer.system
            if not system:
                return

            # Old versions of HAL didn't have the hardware namespace
            if "hardware" in system:
                hardware = system.hardware
            else:
                hardware = system

            fingerprint = md5.new()
            for field in [
                    system.info.product,
                    system.info.subsystem,
                    system.product,
                    system.vendor,
                    system.formfactor,
                    hardware.vendor,
                    hardware.produdct]:
                fingerprint.update(str(field))

            system_id = fingerprint.hexdigest()

        message = system_id
        logging.info("System ID: %s", message)
        self._manager.reactor.fire(("report", "system_id"), message)


factory = SystemInfo
