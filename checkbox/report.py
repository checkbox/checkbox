#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
from xml.dom.minidom import Document, Element, parseString


class ReportManager(object):
    """The central point for dumping and loading information.

    This keeps references to all reports which have been added to the
    instance of this manager. These reports will be able to register
    handlers to understand the formats for dumping and loading actions.
    """

    def __init__(self, name, version=None, stylesheet=None):
        self.name = name
        self.version = version
        self.stylesheet = stylesheet
        self.dumps_table = {}
        self.loads_table = {}
        self.document = None

    def handle_dumps(self, type, handler):
        """
        Call back method for reports to register dump handlers.
        """
        if type in self.dumps_table:
            raise Exception, "Dumps type already handled: %s" % type
        self.dumps_table[type] = handler

    def handle_loads(self, type, handler):
        """
        Call back method for reports to register load handlers.
        """
        if type in self.loads_table:
            raise Exception, "Loads type already handled: %s" % type
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
        elif isinstance(node, Element) and node.hasAttribute("type"):
            type = node.getAttribute("type")
            ret = self.loads_table[type](node)
        else:
            ret = self.loads_table["default"](node)
        return ret

    def add(self, report):
        """
        Add a new report to the manager.
        """
        report.register(self)

    def dumps(self, obj):
        """
        Dump the given object which may be a container of any objects
        supported by the reports added to the manager.
        """
        self.document = Document()

        if self.stylesheet: 
            type = "text/xsl"
            href = "file://%s" % self.stylesheet
            style = self.document.createProcessingInstruction("xml-stylesheet",
                "type=\"%s\" href=\"%s\"" % (type, href))
            self.document.appendChild(style)

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
        if hasattr(self, "register_dumps"):
            self.register_dumps()
        if hasattr(self, "register_loads"):
            self.register_loads()
