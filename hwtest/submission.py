import md5
from datetime import datetime

from hwtest.system import get_system_id


submission_id = None


def get_submission_id():
    global submission_id
    if not submission_id:
        system_id = get_system_id()

        fingerprint = md5.new()
        fingerprint.update(system_id)
        fingerprint.update(str(datetime.utcnow()))
        submission_id = fingerprint.hexdigest()

    return submission_id
