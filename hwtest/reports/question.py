from hwtest.report import Report


class QuestionReport(Report):
    """Report for question related data types."""

    def register_dumps(self):
        self._manager.handle_dumps("questions", self.dumps_questions)
        self._manager.handle_dumps("architectures", self.dumps_architectures)
        self._manager.handle_dumps("categories", self.dumps_categories)
        self._manager.handle_dumps("depends", self.dumps_depends)
        self._manager.handle_dumps("description", self.dumps_text)
        self._manager.handle_dumps("command", self.dumps_text)
        self._manager.handle_dumps("optional", self.dumps_text)

    def register_loads(self):
        self._manager.handle_loads("questions", self.loads_questions)

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
        for question in node.getElementsByTagName("question"):
            value = self._manager.call_loads(question)
            value["question"] = question.getAttribute("name")
            questions.append(value)
        return questions
