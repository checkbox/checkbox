from hwtest.report import Report


class ProcessorReport(Report):
    """Report for processor related data types."""

    def register_dumps(self):
        self._manager.handle_dumps("processors", self.dumps_processors)

    def register_loads(self):
        self._manager.handle_loads("processors", self.loads_processors)

    def dumps_processors(self, obj, parent):
        for processor in [dict(p) for p in obj]:
            element = self._create_element("processor", parent)
            name = processor.pop("processor")
            element.setAttribute("name", str(name))
            self._manager.call_dumps(processor, element)

    def loads_processors(self, node):
        processors = []
        for processor in (p for p in node.childNodes if p.localName == "processor"):
            value = self._manager.call_loads(processor)
            value["processor"] = processor.getAttribute("name")
            processors.append(value)
        return processors
