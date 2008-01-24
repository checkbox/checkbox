NO = "no"
YES = "yes"
SKIP = "skip"
ALL_STATUS = [YES, NO, SKIP]


class Answer(object):

    required_fields = ["status", "data"]

    def __init__(self, status=SKIP, data=""):
        self.attributes = self._validate(**{
            "status": status,
            "data": data})

    def _validate(self, **kwargs):
        # Unknown fields
        for field in kwargs.keys():
            if field not in self.required_fields:
                raise Exception, \
                    "Answer attributes contains unknown field: %s" % field

        # Required fields
        for field in self.required_fields:
            if not kwargs.has_key(field):
                raise Exception, \
                    "Answer attributes does not contain a '%s': %s" \
                    % (field, kwargs)

        # Status field
        if kwargs["status"] not in ALL_STATUS:
            raise Exception, \
                "Unknown status: %s" % kwargs["status"]

        return kwargs

    def __getattr__(self, name):
        if name in self.attributes:
            return self.attributes[name]

        raise AttributeError, name
