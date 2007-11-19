import re
import dbus

from hwtest.lib.cache import cache
from hwtest.lib.update import recursiveupdate

from command import CommandRegistry
from data import DataRegistry
from map import MapRegistry


class DeviceRegistry(DataRegistry):
    """Registry for HAL device information.

    Each item contained in this registry consists of the properties of
    the corresponding HAL device.
    """

    @cache
    def items(self):
        all = {}
        current = None
        for line in self.split("\n"):
            match = re.match(r"  (.*) = (.*) \((.*?)\)", line)
            if match:
                keys = match.group(1).split(".")
                value = match.group(2).strip()
                type_name = match.group(3)
                if type_name == "bool":
                    value = dbus.Boolean(value == "true")
                elif type_name == "double":
                    value = dbus.Double(float(value.split()[0]))
                elif type_name == "int":
                    value = dbus.Int32(int(value.split()[0]))
                elif type_name == "string":
                    value = dbus.String(value.strip("'"))
                elif type_name == "string list":
                    value = dbus.Array([v.strip("'")
                            for v in value.strip("{}").split(", ")])
                elif type_name == "uint64":
                    value = dbus.UInt64(int(value.split()[0]))
                else:
                    raise Exception, "Unknown type: %s" % type_name

                for key in reversed(keys):
                    value = {key: value}

                recursiveupdate(all, value)

        items = []
        for key, value in all.items():
            value = MapRegistry(self.config, value)
            items.append((key, value))

        return items


class HalRegistry(CommandRegistry):
    """Registry for HAL information.

    Each item contained in this registry consists of the udi as key and
    the corresponding device registry as value.
    """

    default_command = "lshal"

    @cache
    def items(self):
        items = []
        for block in self.split("\n\n"):
            lines = block.split("\n")
            while lines:
                line = lines.pop(0)
                match = re.match(r"udi = '(.*)'", line)
                if match:
                    udi = match.group(1)
                    key = udi.split("/")[-1]
                    break

            if lines:
                value = DeviceRegistry(self.config, "\n".join(lines))
                items.append((key, value))

        return items


factory = HalRegistry
