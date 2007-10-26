import dbus

from hwtest.reports.data import DataReport


class HalReport(DataReport):
    """Report for HAL related data types."""

    def register_dumps(self):
        for (dt, dh) in [(dbus.Boolean, self.dumps_bool),
                         (dbus.Int32, self.dumps_int),
                         (dbus.UInt64, self.dumps_uint64),
                         (dbus.Double, self.dumps_double),
                         (dbus.String, self.dumps_str),
                         (dbus.Array, self.dumps_list),
                         (dbus.Dictionary, self.dumps_dict),
                         ("hal", self.dumps_hal)]:
            self._manager.handle_dumps(dt, dh)

    def register_loads(self):
        for (lt, lh) in [("hal", self.loads_hal),
                         ("uint64", self.loads_int),
                         ("double", self.loads_float)]:
            self._manager.handle_loads(lt, lh)

    def dumps_uint64(self, obj, parent):
        self._dumps_text(str(obj), parent, "uint64")

    def dumps_double(self, obj, parent):
        self._dumps_text(str(obj), parent, "double")

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
        for device in (d for d in node.childNodes if d.localName == "device"):
            properties = device.getElementsByTagName("properties")[0]
            value = self._manager.call_loads(properties)
            hal["devices"].append(value)
        return hal
