import os
import shutil


def safe_remove_directory(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception, "Path is not a directory: %s" % path

        shutil.rmtree(path)

def safe_remove_file(path):
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise Exception, "Path is not a file: %s" % path

        os.remove(path)
