from hwtest.report import Report


class ProcessorReport(Report):

    def register_dumps(self):
        self._manager.handle_dumps("processors", self.dumps_processors)

    def register_loads(self):
        self._manager.handle_loads("processors", self.loads_processors)

    def dumps_processors(self, obj, parent):
        for processor in obj:
            element = self._create_element("processor", parent)
            name = processor.pop("processor")
            element.setAttribute("name", str(name))
            self._manager.call_dumps(processor, element)

    def loads_processors(self, node):
        processors = []
        for processor in node.getElementsByTagName("processor"):
            value = self._manager.call_loads(processor)
            value["processor"] = processor.getAttribute("name")
            processors.append(value)
        return processors
