from hwtest.plugin import Plugin


class CategoryPrompt(Plugin):

    optional_attributes = ["category"]

    def register(self, manager):
        super(CategoryPrompt, self).register(manager)
        self._category = self.config.category

        for (rt, rh) in [
             (("prompt", "category"), self.prompt_category)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_category(self, interface):
        registry = self._manager.registry

        # Try to determine category from HAL formfactor
        if not self._category:
            formfactor = registry.hal.computer.system.formfactor
            if formfactor != "unknown":
                self._category = formfactor

        # Try to determine category from dpkg architecture
        if not self._category:
            architecture = registry.dpkg.architecture
            if architecture == "sparc":
                self._category = "server"

        # Try to determine category from kernel version
        if not self._category:
            version = registry.hal.computer.system.kernel.version
            if version.endswith("-server"):
                self._category = "server"

        self._category = interface.show_category(self._category)

        self._manager.reactor.fire(("interface", "category"), self._category)


factory = CategoryPrompt
