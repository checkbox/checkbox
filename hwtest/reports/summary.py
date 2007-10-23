from time import strptime
from datetime import datetime

from hwtest.report import Report


class SummaryReport(Report):
    """Report for summary related data types."""

    def register_dumps(self):
        for (dt, dh) in [("live_cd", self.dumps_value),
                         ("system_id", self.dumps_value),
                         ("distribution", self.dumps_value),
                         ("distroseries", self.dumps_value),
                         ("architecture", self.dumps_value),
                         ("private", self.dumps_value),
                         ("contactable", self.dumps_value),
                         ("date_created", self.dumps_datetime)]:
            self._manager.handle_dumps(dt, dh)

    def register_loads(self):
        for (lt, lh) in [("live_cd", self.loads_bool),
                         ("system_id", self.loads_str),
                         ("distribution", self.loads_str),
                         ("distroseries", self.loads_str),
                         ("architecture", self.loads_str),
                         ("private", self.loads_bool),
                         ("contactable", self.loads_bool),
                         ("date_created", self.loads_datetime)]:
            self._manager.handle_loads(lt, lh)

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
