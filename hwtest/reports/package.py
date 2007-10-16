from hwtest.report import Report


class PackageReport(Report):

    def register_dumps(self):
        self._manager.handle_dumps("packages", self.dumps_packages)

    def register_loads(self):
        self._manager.handle_loads("packages", self.loads_packages)

    def dumps_packages(self, obj, parent):
        for package in obj:
            element = self._create_element("package", parent)
            name = package.pop("name")
            element.setAttribute("name", str(name))
            self._manager.call_dumps(package, element)

    def loads_packages(self, node):
        packages = []
        for package in node.getElementsByTagName("package"):
            value = self._manager.call_loads(package)
            value["package"] = package.getAttribute("name")
            packages.append(value)
        return packages
