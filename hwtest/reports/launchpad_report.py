import dbus
import logging

from time import strptime
from datetime import datetime

from xml.dom.minidom import Node

from hwtest.registry import Registry
from hwtest.report import Report
from hwtest.reports.xml_report import (XmlReportManager, XmlReport,
    convert_bool)


class LaunchpadReportManager(XmlReportManager):

    def __init__(self, *args, **kwargs):
        super(LaunchpadReportManager, self).__init__(*args, **kwargs)
        self.add(HalReport())
        self.add(ProcessorReport())
        self.add(QuestionReport())
        self.add(SummaryReport())


class HalReport(XmlReport):
    """Report for HAL related data types."""

    def register_dumps(self):
        for (dt, dh) in [(dbus.Boolean, self.dumps_bool),
                         (dbus.Int32, self.dumps_int),
                         (dbus.UInt64, self.dumps_uint64),
                         (dbus.Double, self.dumps_double),
                         (dbus.String, self.dumps_str),
                         (dbus.Array, self.dumps_list),
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
        logging.debug("Dumping hal")
        parent.setAttribute("version", obj["version"])
        for device in obj["devices"].values():
            element = self._create_element("device", parent)
            element.setAttribute("id", str(device.id))
            element.setAttribute("udi", device.info.udi)
            properties = self._create_element("properties", element)
            self.dumps_device(device, properties)

    def dumps_device(self, obj, parent, keys=[]):
        for key, value in obj.items():
            if isinstance(value, Registry):
                self.dumps_device(value, parent, keys + [key])
            else:
                key = ".".join(keys + [key])
                self._manager.call_dumps({key: value}, parent)

    def loads_hal(self, node):
        logging.debug("Loading hal")
        hal = {}
        hal["version"] = node.getAttribute("version")
        hal["devices"] = []
        for device in (d for d in node.childNodes if d.localName == "device"):
            properties = device.getElementsByTagName("properties")[0]
            value = self._manager.call_loads(properties)
            hal["devices"].append(value)
        return hal


class ProcessorReport(Report):
    """Report for processor related data types."""

    def register_dumps(self):
        self._manager.handle_dumps("processors", self.dumps_processors)

    def register_loads(self):
        self._manager.handle_loads("processors", self.loads_processors)

    def dumps_processors(self, obj, parent):
        logging.debug("Dumping processors")
        for name, processor in obj.items():
            element = self._create_element("processor", parent)
            element.setAttribute("id", str(processor.id))
            element.setAttribute("name", str(name))
            self._manager.call_dumps(dict(processor), element)

    def loads_processors(self, node):
        logging.debug("Loading processors")
        processors = {}
        for processor in (p for p in node.childNodes if p.localName == "processor"):
            value = self._manager.call_loads(processor)
            name = processor.getAttribute("name")
            value["processor"] = name
            processors[int(name)] = value

        return processors


class QuestionReport(Report):
    """Report for question related data types."""

    def register_dumps(self):
        for (dt, dh) in [("questions", self.dumps_questions),
                         ("architectures", self.dumps_architectures),
                         ("categories", self.dumps_categories),
                         ("relations", self.dumps_relations),
                         ("depends", self.dumps_depends),
                         ("description", self.dumps_text),
                         ("command", self.dumps_text),
                         ("optional", self.dumps_text),
                         ("data", self.dumps_text),
                         ("status", self.dumps_text),
                         ("suite", self.dumps_text),
                         ("auto", self.dumps_text)]:
            self._manager.handle_dumps(dt, dh)

    def register_loads(self):
        for (lt, lh) in [("questions", self.loads_questions),
                         ("categories", self.loads_list),
                         ("architectures", self.loads_list),
                         ("depends", self.loads_list),
                         ("command", self.loads_data),
                         ("description", self.loads_data),
                         ("optional", self.loads_bool),
                         ("data", self.loads_data),
                         ("status", self.loads_data),
                         ("suite", self.loads_data),
                         ("auto", self.loads_bool)]:
            self._manager.handle_loads(lt, lh)

    def dumps_questions(self, obj, parent):
        logging.debug("Dumping questions")
        for question in [dict(p) for p in obj]:
            element = self._create_element("question", parent)
            name = question.pop("name")
            element.setAttribute("name", str(name))
            self._manager.call_dumps(question, element)

    def dumps_architectures(self, obj, parent):
        for architecture in obj:
            element = self._create_element("architecture", parent)
            self.dumps_text(architecture, element)

    def dumps_categories(self, obj, parent):
        for category in obj:
            element = self._create_element("category", parent)
            self.dumps_text(category, element)

    def dumps_relations(self, obj, parent):
        for relation in obj:
            element = self._create_element("relation", parent)
            self.dumps_text(relation.id, element)

    def dumps_depends(self, obj, parent):
        for depend in obj:
            element = self._create_element("depend", parent)
            self.dumps_text(depend, element)

    def dumps_text(self, obj, parent):
        self._create_text_node(str(obj), parent)

    def loads_questions(self, node):
        logging.debug("Loading questions")
        questions = []
        for question in (q for q in node.childNodes if q.localName == "question"):
            value = self._manager.call_loads(question)
            value["name"] = question.getAttribute("name")
            questions.append(value)
        return questions

    def loads_list(self, node):
        list = []
        for child in (c for c in node.childNodes if c.nodeType != Node.TEXT_NODE):
            value = self.loads_data(child)
            list.append(value)
        return list

    def loads_data(self, node):
        return node.firstChild.data.strip()

    def loads_bool(self, node):
        return convert_bool(self.loads_data(node))


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
        return convert_bool(node.getAttribute("value"))

    def loads_str(self, node):
        return str(node.getAttribute("value"))

    def loads_datetime(self, node):
        value = node.getAttribute("value")
        return datetime(*strptime(value, "%Y-%m-%d %H:%M:%S")[0:7])
