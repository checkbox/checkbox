NO = 'no'
YES = 'yes'
SKIP = 'skip'
ALL_STATUS = [YES, NO, SKIP]


class Answer:

    def __init__(self, status, data, auto):
        self.status = status
        self.data = data
        self.auto = auto

    def get_properties(self):
        return dict((p, getattr(self, p)) for p in ("status", "data", "auto"))
