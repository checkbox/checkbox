import md5
from datetime import datetime


def get_submission_key(registry):
    system_key = registry.system.key

    fingerprint = md5.new()
    fingerprint.update(system_key)
    fingerprint.update(str(datetime.utcnow()))
    return fingerprint.hexdigest()
