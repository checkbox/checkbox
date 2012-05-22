#!/usr/bin/python
import sys
import subprocess
import tempfile
from contextlib import contextmanager
import gconf
import argparse


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
    client = gconf.Client()
    wrap_mode = client.get_string('/apps/gedit-2/preferences/editor'
                                  '/wrap_mode/wrap_mode')
    client.set_string('/apps/gedit-2/preferences/editor/wrap_mode/wrap_mode',
                      'GTK_WRAP_NONE')
    yield
    client.set_string('/apps/gedit-2/preferences/editor/wrap_mode/wrap_mode',
                      wrap_mode)


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
