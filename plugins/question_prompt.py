from hwtest.plugin import Plugin
from hwtest.iterator import Iterator
from hwtest.excluder import Excluder
from hwtest.question import QuestionManager


class QuestionPrompt(Plugin):

    run_priority = -300

    def __init__(self, question_manager=None):
        super(QuestionPrompt, self).__init__()
        self.question_manager = question_manager or QuestionManager()
        self.questions = Iterator()
        self.category = None

    def register(self, manager):
        super(QuestionPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "add-question"), self.add_question)
        self._manager.reactor.call_on(("prompt", "set-category"), self.set_category)
        self._manager.reactor.call_on(("prompt", "set-direction"), self.set_direction)

    def run(self):
        self.questions = self.get_questions()
        self.question = self.questions.next()
        while self.question:
            self._manager.reactor.fire(("interface", "show-question"),
                self.question,
                self.questions.has_prev(),
                self.questions.has_next())

    def add_question(self, question):
        self.question_manager.add(question)

    def set_category(self, category):
        self.category = category

    def set_direction(self, direction):
        questions = self.questions
        if direction is 1:
            self.question = questions.has_next() and questions.next() or None
        else:
            self.question = questions.has_prev() and questions.prev() or None

    def get_questions(self):
        questions = self.question_manager.get_iterator()
        if self.category:
            func = lambda q, c=self.category: c not in q.categories
            questions = iter(Excluder(questions, func, func))

        return questions


factory = QuestionPrompt
