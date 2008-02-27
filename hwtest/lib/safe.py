import os


def safe_make_directory(path, mode=0777):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception, "Path is not a directory: %s" % path

        os.chmod(path, mode)
    else:
        os.makedirs(path, mode)

def safe_remove_directory(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception, "Path is not a directory: %s" % path

        os.removedirs(path)

def safe_remove_file(path):
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise Exception, "Path is not a file: %s" % path

        os.remove(path)
