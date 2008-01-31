NO = "no"
YES = "yes"
SKIP = "skip"
ALL_STATUS = [YES, NO, SKIP]


class Answer(object):

    required_fields = ["status", "data"]
    optional_fields = {
        "start_time": None,
        "end_time": None}

    def __init__(self, status=SKIP, data="", start_time=None, end_time=None):
        self.attributes = self._validate({
            "status": status,
            "data": data,
            "start_time": start_time,
            "end_time": end_time})

    def _validate(self, attributes):
        # Unknown fields
        for field in attributes.keys():
            if field not in self.required_fields + self.optional_fields.keys():
                raise Exception, \
                    "Answer attributes contains unknown field: %s" % field

        # Required fields
        for field in self.required_fields:
            if not attributes.has_key(field):
                raise Exception, \
                    "Answer attributes does not contain a '%s': %s" \
                    % (field, attributes)

        # Optional fields
        for field in self.optional_fields.keys():
            if not attributes.has_key(field):
                attributes[field] = self.optional_fields[field]

        # Status field
        if attributes["status"] not in ALL_STATUS:
            raise Exception, \
                "Unknown status: %s" % attributes["status"]

        return attributes

    def __getattr__(self, name):
        if name in self.attributes:
            return self.attributes[name]

        raise AttributeError, name
