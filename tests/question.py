import unittest

from hwtest.question import (parse_file, parse_string)


class QuestionTest(unittest.TestCase):
    def test_parse_file(self):
        questions = parse_file("questions.txt")
        self.assertTrue(len(questions) > 0)

    def test_parse_string_empty(self):
        questions = parse_string("")
        self.assertTrue(questions == [])
        self.assertTrue(len(questions) == 0)

    def test_parse_string_one_line(self):
        questions = parse_string("""
key: value
""")
        self.assertTrue(questions)
        self.assertTrue(len(questions) == 1)

        question = questions[0]
        self.assertTrue(question.has_key('key'))
        self.assertTrue(question['key'] == 'value')

        questions = parse_string("""
key: value
  continued
""")
        self.assertTrue(questions)
        self.assertTrue(len(questions) == 1)

        question = questions[0]
        self.assertTrue(question.has_key('key'))
        self.assertTrue(question['key'] == 'value continued')

    def test_parse_string_two_lines(self):
        table = [['key1', 'value1'], ['key2', 'value2']]
        questions = parse_string(
            '\n'.join([': '.join(t) for t in table]))

        self.assertTrue(questions)
        self.assertTrue(len(questions) == 1)

        question = questions[0]
        for key, value in table:
            self.assertTrue(question.has_key(key))
            self.assertTrue(question[key] == value)

    def test_parse_string_two_questions(self):
        table = [['question1', 'value1'], ['question2', 'value2']]
        questions = parse_string(
            '\n\n'.join([': '.join(t) for t in table]))

        self.assertTrue(questions)
        self.assertTrue(len(questions) == 2)

        for i in range(len(table)):
            question = questions[i]
            key, value = table[i]
            self.assertTrue(question.has_key(key))
            self.assertTrue(question[key] == value)
