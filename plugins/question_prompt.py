from hwtest.plugin import Plugin
from hwtest.iterator import Iterator
from hwtest.excluder import Excluder
from hwtest.question import QuestionManager, QuestionParser


class QuestionPrompt(Plugin):

    priority = -300

    def __init__(self, config, question_manager=None):
        super(QuestionPrompt, self).__init__(config)
        self.question_manager = question_manager or QuestionManager()
        self.questions = Iterator()
        self.category = None

    def register(self, manager):
        super(QuestionPrompt, self).register(manager)
        for (rt, rh) in [("gather", self.gather),
                         (("prompt", "add-question"), self.add_question),
                         (("prompt", "set-category"), self.set_category),
                         (("prompt", "set-direction"), self.set_direction)]:
            self._manager.reactor.call_on(rt, rh)

    def run(self):
        self.questions = self.get_questions()
        self.question = self.questions.next()
        while self.question:
            self._manager.reactor.fire(("interface", "show-question"),
                self.question,
                self.questions.has_prev(),
                self.questions.has_next())

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "question"), message)

    def create_message(self):
        return [q.properties for q in iter(self.questions.iterator)]

    def add_question(self, question):
        self.question_manager.add_question(question)

    def set_category(self, category):
        self.category = category

    def set_direction(self, direction):
        questions = self.questions
        if direction is 1:
            self.question = questions.has_next() and questions.next() or None
        else:
            self.question = questions.has_prev() and questions.prev() or None

    def get_questions(self):
        parser = QuestionParser()
        for directory in self.config.questions_path.split(":"):
            parser.load_directory(directory)

        for question_kwargs in parser.questions:
            type = question_kwargs.pop("type")
            self._manager.reactor.fire((type, "add-question"), **question_kwargs)

        questions = self.question_manager.get_iterator()
        if self.category:
            func = lambda q, c=self.category: c not in q.categories
            questions = iter(Excluder(questions, func, func))

        return questions


factory = QuestionPrompt
