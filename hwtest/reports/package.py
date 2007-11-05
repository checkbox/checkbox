from hwtest.report import Report


class PackageReport(Report):
    """Report for package related data types."""

    def register_dumps(self):
        self._manager.handle_dumps("packages", self.dumps_packages)

    def register_loads(self):
        self._manager.handle_loads("packages", self.loads_packages)

    def dumps_packages(self, obj, parent):
        for package in [dict(p) for p in obj]:
            element = self._create_element("package", parent)
            name = package.pop("name")
            element.setAttribute("name", str(name))
            self._manager.call_dumps(package, element)

    def loads_packages(self, node):
        packages = []
        for package in (p for p in node.childNodes if p.localName == "package"):
            value = self._manager.call_loads(package)
            value["package"] = package.getAttribute("name")
            packages.append(value)
        return packages
