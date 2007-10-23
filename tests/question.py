import unittest

from hwtest.question import QuestionParser


class QuestionParserTest(unittest.TestCase):
    def test_load_path(self):
        parser = QuestionParser()
        parser.load_path("questions/manual.txt")
        self.assertTrue(len(parser.questions) > 0)

    def test_load_string_empty(self):
        parser = QuestionParser()
        parser.load_string("")
        self.assertTrue(parser.questions == [])
        self.assertTrue(len(parser.questions) == 0)

    def test_load_string_one_line(self):
        parser = QuestionParser()
        parser.load_string("""
name: value
""")
        self.assertTrue(parser.questions)
        self.assertTrue(len(parser.questions) == 1)

        question = parser.questions[0]
        self.assertTrue(question.has_key('name'))
        self.assertTrue(question['name'] == 'value')

    def test_load_string_one_line_continued(self):
        parser = QuestionParser()
        parser.load_string("""\
name:
  value
  continued
""")
        self.assertTrue(parser.questions)
        self.assertTrue(len(parser.questions) == 1)

        question = parser.questions[0]
        self.assertTrue(question.has_key('name'))
        self.assertTrue(question['name'] == """\
 value
 continued""")

    def test_parse_string_two_lines(self):
        parser = QuestionParser()
        table = [['name', 'value'], ['foo', 'bar']]
        parser.load_string(
            '\n'.join([': '.join(t) for t in table]))

        self.assertTrue(parser.questions)
        self.assertTrue(len(parser.questions) == 1)

        question = parser.questions[0]
        for key, value in table:
            self.assertTrue(question.has_key(key))
            self.assertTrue(question[key] == value)

    def test_parse_string_two_questions(self):
        parser = QuestionParser()
        table = [['name', 'value1'], ['name', 'value2']]
        parser.load_string(
            '\n\n'.join([': '.join(t) for t in table]))

        self.assertTrue(parser.questions)
        self.assertTrue(len(parser.questions) == 2)

        for i in range(len(table)):
            question = parser.questions[i]
            key, value = table[i]
            self.assertTrue(question.has_key(key))
            self.assertTrue(question[key] == value)
