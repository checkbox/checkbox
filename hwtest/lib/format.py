def format_bytes(bytes):
    """Convert a bytes integer value to a human-readable string."""
    if bytes >= 1024 * 1024 * 1024 * 1024:
        return "%.2fTB" % (bytes/1024/1024/1024/1024.)
    if bytes >= 1024 * 1024 * 1024:
        return "%.2fGB" % (bytes/1024/1024/1024.)
    if bytes >= 1024 * 1024:
        return "%.2fMB" % (bytes/1024/1024.)
    elif bytes >= 1024:
        return "%.2fKB" % (bytes/1024.)
    else:
        return "%dB" % (bytes)

