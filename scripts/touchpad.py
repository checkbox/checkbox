#!/usr/bin/python
import argparse
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from gi.repository import Gio


def main(args):
    """
    Open gedit with temporary file created from string
    depending on the command passed
    """
    with tempfile.NamedTemporaryFile() as f:
        str = globals()['get_%s_str' % args.test]()
        f.write(str)
        f.flush()
        with gedit_wrap_none():
            subprocess.call(('gedit', f.name))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run touchpad test cases")
    parser.add_argument("test", choices=["horizontal", "vertical"],
                        help="Test case to execute")
    return parser.parse_args()


@contextmanager
def gedit_wrap_none():
    """
    Make sure that gedit word wrapping is set to None
    """

    gedit_settings = Gio.Settings.new("org.gnome.gedit.preferences.editor")
    current_setting = gedit_settings.get_string("wrap-mode")

    # Set to None
    gedit_settings.set_string("wrap-mode", 'none')

    yield
    gedit_settings.set_string("wrap-mode", current_setting)
   
 
def get_horizontal_str():
    """
    Wide line to force horizontal scrolling
    """
    return 'this is a really wide line, ' * 100


def get_vertical_str():
    """
    Many lines to force vertical scrolling
    """
    return '\n'.join(['this is a single line'] * 1000)


if __name__ == '__main__':
    args = parse_arguments()
    sys.exit(main(args))
