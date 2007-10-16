from hwtest.report import Report


class HalReport(Report):

    def register_dumps(self):
        self._manager.handle_dumps("hal", self.dumps_hal)

    def register_loads(self):
        self._manager.handle_loads("hal", self.loads_hal)

    def dumps_hal(self, obj, parent):
        parent.setAttribute("version", obj["version"])
        id = 0
        for device in obj["devices"]:
            element = self._create_element("device", parent)
            element.setAttribute("id", str(id)); id += 1
            element.setAttribute("udi", device["info.udi"])
            self._manager.call_dumps({"properties": device}, element)

    def loads_hal(self, node):
        hal = {}
        hal["version"] = node.getAttribute("version")
        hal["devices"] = []
        for device in node.getElementsByTagName("device"):
            properties = device.getElementsByTagName("properties")[0]
            value = self._manager.call_loads(properties)
            hal["devices"].append(value)
        return hal
