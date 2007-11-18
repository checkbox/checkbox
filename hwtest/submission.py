import md5
from datetime import datetime


submission_id = None


def get_submission_id(registry):
    global submission_id
    if not submission_id:
        system_id = registry.system.id

        fingerprint = md5.new()
        fingerprint.update(system_id)
        fingerprint.update(str(datetime.utcnow()))
        submission_id = fingerprint.hexdigest()

    return submission_id
