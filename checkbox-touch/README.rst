The (Converging) Checkbox
=========================

This directory contains the implementation of Checkbox. The Ubuntu-SDK based
touch application that initially, will target the phone form factor (but will
work on all the form factors).

It is implemented according to a design document (http://goo.gl/2agB51),
that describes a minimum viable product for v1.0

The application works well in an x86 and armhf emulator as well as on the
desktop. On a desktop system we recommend to use packaged dependencies
(python3-plainbox and pyotherside). On any of the touch devices you will need
to build a suitable click package (see below for details) or get a copy from
the Ubuntu store, once it gets published.

TL;DR
-----

Run:

.. code-block:: bash

    $ ./get-libs
    $ ./build-me --provider \
    ../providers/plainbox-provider-certification-touch/ --install

To start testing on the device!

Getting dependencies
--------------------

The click package is built from QML/JavaScript/Python code contained in the
`py` and `components` directories. It also has `lib` directory that contains
all necessary libraries needed to run checkbox.

Before building click package make sure you run `./get-libs` to initialize and
populate `./lib` directory. Use --get-local-plainbox to embed plainbox code
that's available in the ../plainbox directory.

Building and installing the click package
-----------------------------------------

To build Checkbox-Touch click package run:

.. code-block:: bash

    $ ./build-me

to build and install the package run:

.. code-block:: bash

    $ ./build-me --install

Running Checkbox-Touch on a desktop
-----------------------------------

To run on a desktop run `qmlscene checkbox-touch.qml`
Note: Make sure you've ran `./get-libs` first.


Choosing the default test-plan
------------------------------

If you wish to run one particular test plan, you may do so, by providing
./build-me script with --testplan option. E.g.:

.. code-block:: bash

    $ ./build-me --testplan="2013.com.canonical.plainbox::stub"


Embedding providers into click package
--------------------------------------

If you wish to bundle providers into click package use `--provider` option in
build-me script. E.g.:

.. code-block:: bash

    $ ./build-me --provider ../providers/plainbox-provider-certification-touch


Default Checkbox-Touch settings
-------------------------------
During execution of `./build-me` script, `settings.json` file is generated.
It contains values that Checkbox-Touch will use as its default ones.
Altough not required, you may edit this file to suit your needs.

Further assistance
------------------

For further assistance on packaging Checkbox, run:

.. code-block:: bash

    $ ./build-me --help


The Release Process
===================

The release process is quite simple. It's also informal as we only did it once or twice

- Tag the tree using the $PRODUCT-v$VERSION scheme (checkbox-touch-v0.1).
- Build a new click package as outlined above.
- Test it on some devices to ensure that's it's not horribly broken.
- Create a release on an appropriate Launchpad milestone on the checkbox-touch
  project (https://launchpad.net/checkbox-touch). Write a changelog and upload
  the click package. The changelog should contain link to the version milestone
  on Launchpad, e.g. https://launchpad.net/checkbox-touch/+milestone/1.1.2
- Join ``#ubuntu-app-devel`` on freenode and figure out who can upload core-dev
  applications. Ask them to upload the new version. Popey declared to do the
  uploads, so start by asking him.
  that do this but it seems to be informal at this stage.
- Do some post-release changes (bump the version in the sources). Commit that
  and propose a merge (along with the released tag) back to ``lp:checkbox``.
