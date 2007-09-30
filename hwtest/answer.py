NO = 'no'
YES = 'yes'
SKIP = 'skip'
ALL_STATUS = [YES, NO, SKIP]


class Answer:

    def __init__(self, test, status, data, auto):
        self.test = test
        self.status = status
        self.data = data
        self.auto = auto

    def __str__(self):
        return self.test.name
