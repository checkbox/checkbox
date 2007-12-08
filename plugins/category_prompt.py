from hwtest.plugin import Plugin


class CategoryPrompt(Plugin):

    priority = -400

    def run(self):
        category = self.config.category
        registry = self._manager.registry

        # Try to determine category from HAL formfactor
        if not category:
            formfactor = registry.hal.computer.system.formfactor
            if formfactor != "unknown":
                category = formfactor

        # Try to determine category from dpkg architecture
        if not category:
            architecture = registry.dpkg.architecture
            if architecture == "sparc":
                category = "server"

        # Try to determine category from kernel version
        if not category:
            version = registry.hal.system.kernel.version
            if version.endswith("-server"):
                category = "server"

        self._manager.reactor.fire(("interface", "show-category"),
            category=category)


factory = CategoryPrompt
