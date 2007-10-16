from time import strptime
from datetime import datetime

from hwtest.report import Report


class SummaryReport(Report):

    def register_dumps(self):
        self._manager.handle_dumps("live_cd", self.dumps_value)
        self._manager.handle_dumps("system_id", self.dumps_value)
        self._manager.handle_dumps("distribution", self.dumps_value)
        self._manager.handle_dumps("distroseries", self.dumps_value)
        self._manager.handle_dumps("architecture", self.dumps_value)
        self._manager.handle_dumps("private", self.dumps_value)
        self._manager.handle_dumps("contactable", self.dumps_value)
        self._manager.handle_dumps("date_created", self.dumps_datetime)

    def register_loads(self):
        self._manager.handle_loads("live_cd", self.loads_bool)
        self._manager.handle_loads("system_id", self.loads_str)
        self._manager.handle_loads("distribution", self.loads_str)
        self._manager.handle_loads("distroseries", self.loads_str)
        self._manager.handle_loads("architecture", self.loads_str)
        self._manager.handle_loads("private", self.loads_bool)
        self._manager.handle_loads("contactable", self.loads_bool)
        self._manager.handle_loads("date_created", self.loads_datetime)

    def dumps_value(self, obj, parent):
        parent.setAttribute("value", str(obj))

    def dumps_datetime(self, obj, parent):
        parent.setAttribute("value", str(obj).split(".")[0])

    def loads_bool(self, node):
        return bool(node.getAttribute("value"))

    def loads_str(self, node):
        return str(node.getAttribute("value"))

    def loads_datetime(self, node):
        value = node.getAttribute("value")
        return datetime(*strptime(value, "%Y-%m-%d %H:%M:%S")[0:7])
