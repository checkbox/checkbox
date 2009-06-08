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
import os
import re

from checkbox.lib.cache import Cache

from checkbox.properties import Path, String
from checkbox.plugin import Plugin


class GraphInfo(Plugin):

    # Filename where the dot file is stored
    input = Path(default="%(checkbox_data)s/graph.dot")

    # Filename where the png file is stored
    output = Path(default="%(checkbox_data)s/graph.png")

    # Command to create a png from the given dot file
    command = String(default="dot -Tpng -o@output@ @input@")

    def register(self, manager):
        super(GraphInfo, self).register(manager)

        self._nodes = {}
        self._edges = {}
        self._manager.reactor.call_on(".*", self.event_all, -1000)
        self._manager.reactor.call_on("stop", self.stop, 1000)

    def event_all(self, *args, **kwargs):
        event_type = self._manager.reactor._event_stack[-1]
        handlers = []
        for key, value in self._manager.reactor._event_handlers.items():
            for v in value:
                info = get_handler_info(v[0])
                self._nodes.setdefault(info.cls, set())
                self._nodes[info.cls].add(info.func)
            if re.match("^%s$" % key, event_type):
                handlers.extend(value)

        if len(self._manager.reactor._handler_stack) > 1:
            parent_handler = self._manager.reactor._handler_stack[-2]
            self._edges.setdefault(parent_handler, set())
            for handler in handlers:
                self._edges[parent_handler].add(handler[0])

    def stop(self):
        file = open(self.input, "w")

        # Header
        file.write("""
digraph g {
graph [
rankdir = "LR"
concentrate = "true"
];
node [
fontsize = "12"
shape = "ellipse"
];
edge [
];
""")

        # Nodes
        for cls, funcs in self._nodes.items():
            funcs_string = "|".join(["<%s>%s" % (f, f) for f in funcs])
            if cls != "GraphInfo":
                file.write("""\
"%s" [
label = "%s|%s"
shape = "record"
];
""" % (cls, cls, funcs_string))
 
        # Edges
        for parent, children in self._edges.items():
            parent_info = get_handler_info(parent)
            for child in children:
                child_info = get_handler_info(child)
                if child_info.cls != "GraphInfo":
                    file.write("""\
"%s":"%s" -> "%s":"%s";
""" % (parent_info.cls, parent_info.func, child_info.cls, child_info.func))

        # Footer
        file.write("}\n")
        file.close()

        command = self.command.replace("@output@", self.output). \
            replace("@input@", self.input)
        os.system(command)


class HandlerInfo(object):

    def __init__(self, cls, func):
        self.cls = cls
        self.func = func


def get_handler_info(handler):
    if isinstance(handler, Cache):
        cls = handler._instance.__class__.__name__
        func = handler._function.__name__
    else:
        cls = handler.im_class.__name__
        func = handler.im_func.__name__

    return HandlerInfo(cls, func)


factory = GraphInfo
