import logging

from xml.dom.minidom import Document, Node, parseString

from hwtest.log import format_object


class ReportManager(object):
    """The central point for dumping and loading information.

    This keeps references to all reports which have been added to the
    instance of this manager. These reports will be able to register
    handlers to understand the formats for dumping and loading actions.
    """

    def __init__(self, name, version=None):
        self.name = name
        self.version = version
        self.dumps_table = {}
        self.loads_table = {}
        self.document = None

    def handle_dumps(self, type, handler):
        """
        Call back method for reports to register dump handlers.
        """
        self.dumps_table[type] = handler

    def handle_loads(self, type, handler):
        """
        Call back method for reports to register load handlers.
        """
        self.loads_table[type] = handler

    def call_dumps(self, obj, node):
        """
        Convenience method for reports to call the dump handler
        corresponding to the type of the given object.
        """
        return self.dumps_table[type(obj)](obj, node)

    def call_loads(self, node):
        """
        Convenience method for reports to call the load handler
        corresponding to the content of the given node.
        """
        if self.loads_table.has_key(node.localName):
            ret = self.loads_table[node.localName](node)
        else:
            ret = self.loads_table["default"](node)
        return ret

    def add(self, report):
        """
        Add a new report to the manager.
        """
        logging.info("Registering report %s.", format_object(report))
        report.register(self)

    def dumps(self, obj):
        """
        Dump the given object which may be a container of any objects
        supported by the reports added to the manager.
        """
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
        """
        Load the given string which may be a container of any nodes
        supported by the reports added to the manager.
        """
        document = parseString(str)
        node = document.childNodes[0]
        assert(node.localName == self.name)

        try:
            ret = self.call_loads(document)
        except KeyError, e:
            raise ValueError, "Unsupported type: %s" % e

        return ret


class Report(object):
    """A convenience for writing reports.

    This provides a register method which will set the manager attribute
    and optionally call the C{register_dumps} and C{register_loads}
    methods.
    """

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
