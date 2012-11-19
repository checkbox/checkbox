PlainBox
========

PlainBox is a plain replacement for CheckBox

Hacking
=======

To start hacking use virtualenv with python3

    $ sudo apt-get install python-virtualenv python3-dev
    $ virtualenv -p python3 /path/to/venv
    $ . /path/to/venv/bin/activate

On Ubuntu you'll need to update the version of distribute that is installed
inside the virtualenv to install coverage.

    (venv) $ easy_install -U distribute
    (venv) $ easy_install -U coverage

Then 'develop' the package, this will setup proper path imports and create stub
executables for you. All imports will now use your directory (no need to set
PYTHONPATH to anything)

    (venv) $ python3 setup.py develop

You will be now able to run plainbox:

    (venv) $ plainbox --help

Testing
=======

When hacking, run tests with code coverage (peek at .coveragerc):

    (venv) $ coverage run setup.py test

You can also use the standard 'discover' command from python3 unittest module:

    (venv) $ coverage run -m unittest discover

...then look at test report coverage in the console:

    (venv) $ coverage report

...or in your browser:

    (venv) $ coverage html
    (venv) $ xdg-open htmlcov/index.html

Using the checkbox submodule
============================

This git tree uses the submodule system to put the entire checkbox source code
repository in the checkbox directory. To use it, after you get the plainbox
tree run the following commands:

    $ git submodule init
    $ git submodule update

You only need to run init once, and update each time the chcekbox submodule is
updated to point to new commit in the checkbox tree. If you use this all of
plainbox tests and actual code will run using the embedded copy of checkbox. If
you don't do this you need to install checkbox globally using a system package.
