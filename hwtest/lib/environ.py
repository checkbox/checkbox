from os import environ


def get_variable(name):
    """Get the value of an environment variable name.

    Keyword arguments:
    name -- name of the environment variable
    """

    if name in environ:
        value = environ[name]
    else:
        value = ''

    return value

def add_variable(name, value):
    """Add or change the value of an environment variable name.

    Keyword arguments:
    name -- name of the environment variable
    value -- value given to the environment variable
    """

    environ[name] = value

def remove_variable(name):
    """Remove an environment variable name.

    Keyword arguments:
    name -- name of the environment variable
    """

    if name in environ:
        del environ[name]

def add_path(path):
    """Add a path to the PATH environment variable if it doesn't exist
    already.

    Keyword arguments:
    path -- path to add
    """

    environ_path = get_variable('PATH').split(':')
    if path not in environ_path:
        environ_path.insert(0, path)
        environ['PATH'] = ':'.join(environ_path)

def remove_path(path):
    """Remove a path from the PATH environment variable if it exists
    already.

    Keyword arguments:
    path -- path to remove
    """

    environ_path = get_variable('PATH').split(':')
    if path in environ_path:
        environ_path.remove(path)
        environ['PATH'] = ':'.join(environ_path)
