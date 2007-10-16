from xml.dom.minidom import Document, Node, parseString


class ReportManager(object):
    def __init__(self, name, version=None):
        self.name = name
        self.version = version
        self.dumps_table = {}
        self.loads_table = {}
        self.document = None

    def handle_dumps(self, type, handler):
        self.dumps_table[type] = handler

    def handle_loads(self, type, handler):
        self.loads_table[type] = handler

    def call_dumps(self, obj, node):
        return self.dumps_table[type(obj)](obj, node)

    def call_loads(self, node):
        if self.loads_table.has_key(node.localName):
            ret = self.loads_table[node.localName](node)
        else:
            ret = self.loads_table["default"](node)
        return ret

    def add(self, report):
        #logging.info("Registering report %s.", format_object(report))
        report.register(self)

    def dumps(self, obj):
        self.document = Document()
        node = self.document.createElement(self.name)
        self.document.appendChild(node)

        if self.version:
            node.setAttribute("version", self.version)

        try:
            self.call_dumps(obj, node)
        except KeyError, e:
            raise ValueError, "Unsupported type: %s" % e

        document = self.document
        self.document = None
        return document

    def loads(self, str):
        document = parseString(str)
        node = document.childNodes[0]
        assert(node.localName == self.name)

        try:
            ret = self.call_loads(document)
        except KeyError, e:
            raise ValueError, "Unsupported type: %s" % e

        return ret


class Report(object):

    def _create_element(self, name, parent):
        element = self._manager.document.createElement(name)
        parent.appendChild(element)
        return element

    def _create_text_node(self, text, parent):
        text_node = self._manager.document.createTextNode(text)
        parent.appendChild(text_node)
        return text_node

    def register(self, manager):
        self._manager = manager
        self._manager.handle_loads("default", self.loads_default)
        if hasattr(self, "register_dumps"):
            self.register_dumps()
        if hasattr(self, "register_loads"):
            self.register_loads()

    def loads_default(self, node):
        default = {}
        for child in node.childNodes:
            if child.nodeType != Node.TEXT_NODE:
                if child.hasAttribute("name"):
                    name = child.getAttribute("name")
                else:
                    name = child.localName
                default[name] = self._manager.call_loads(child)
        return default
