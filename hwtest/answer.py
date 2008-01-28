NO = "no"
YES = "yes"
SKIP = "skip"
ALL_STATUS = [YES, NO, SKIP]


class Answer(object):

    required_fields = ["status", "data"]

    def __init__(self, status=SKIP, data=""):
        self.attributes = self._validate({
            "status": status,
            "data": data})

    def _validate(self, attributes):
        # Unknown fields
        for field in attributes.keys():
            if field not in self.required_fields:
                raise Exception, \
                    "Answer attributes contains unknown field: %s" % field

        # Required fields
        for field in self.required_fields:
            if not attributes.has_key(field):
                raise Exception, \
                    "Answer attributes does not contain a '%s': %s" \
                    % (field, attributes)

        # Status field
        if attributes["status"] not in ALL_STATUS:
            raise Exception, \
                "Unknown status: %s" % attributes["status"]

        return attributes

    def __getattr__(self, name):
        if name in self.attributes:
            return self.attributes[name]

        raise AttributeError, name
