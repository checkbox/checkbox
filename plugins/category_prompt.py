from hwtest.plugin import Plugin


class CategoryPrompt(Plugin):

    attributes = ["category"]

    def register(self, manager):
        super(CategoryPrompt, self).register(manager)
        self._manager.reactor.call_on(("interface", "show-category"), self.show_category)

    def show_category(self, interface):
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
            version = registry.hal.computer.system.kernel.version
            if version.endswith("-server"):
                category = "server"

        if not category:
            category = interface.show_category()

        self._manager.reactor.fire(("prompt", "set-category"),
            category)


factory = CategoryPrompt
