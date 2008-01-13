from hwtest.contrib import bpickle
from hwtest.registry import Registry


def install():
    """Install bpickle extensions for Registry types."""
    for type, function in get_registry_types():
        bpickle.dumps_table[type] = function


def uninstall():
    """Uninstall bpickle extensions for Registry types."""
    for type, function in get_registry_types():
        del bpickle.dumps_table[type]


def get_registry_types():
    """
    Generator yields C{(type, bpickle_function)} for available Registry
    types.
    """
    for (type, function) in [(Registry, bpickle.dumps_dict)]:
        yield type, function
