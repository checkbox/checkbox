from xml.dom.minidom import Node

from hwtest.report import Report
from hwtest.reports.data import convert_bool


class QuestionReport(Report):
    """Report for question related data types."""

    def register_dumps(self):
        for (dt, dh) in [("questions", self.dumps_questions),
                         ("architectures", self.dumps_architectures),
                         ("categories", self.dumps_categories),
                         ("depends", self.dumps_depends),
                         ("description", self.dumps_text),
                         ("command", self.dumps_text),
                         ("optional", self.dumps_text),
                         ("data", self.dumps_text),
                         ("status", self.dumps_text),
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
                         ("auto", self.loads_bool)]:
            self._manager.handle_loads(lt, lh)

    def dumps_questions(self, obj, parent):
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

    def dumps_depends(self, obj, parent):
        for depend in obj:
            element = self._create_element("depend", parent)
            self.dumps_text(depend, element)

    def dumps_text(self, obj, parent):
        self._create_text_node(str(obj), parent)

    def loads_questions(self, node):
        questions = []
        for question in (q for q in node.childNodes if q.localName == "question"):
            value = self._manager.call_loads(question)
            value["question"] = question.getAttribute("name")
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
