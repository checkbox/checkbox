The Checkbox Touch
==================

This directory contains the implementation of Checkbox Touch. The Ubuntu-SDK
based touch application that initially, will target the phone form factor (but
will work on all the form factors).

It is implemented according to a design document (we need to publish that
document before it can be referenced here) that describes a minimum viable
product for v1.0

The application works well in an x86 and armhf emulator as well as on the
desktop. On a desktop system we recommend to use packaged dependencies
(python3-plainbox and pyotherside). On any of the touch devices you will need
to build a suitable click package (see below for details) or get a copy from
the Ubuntu store, once it gets published.

Building the click package
--------------------------

The click package is built out of the pure QML/JavaScript/Python code contained
in the "py" and "components" directories. In addition to that a few external
libraries (from the Ubuntu repository) are unpacked into the
"lib/$arch\_triplet" directory so that we can import our python dependencies
that are not a part of the SDK. Currently this is totally manual but we should
have a script that automates part of that process soon so it's not going to be
described here in much detail.

Running on a desktop
--------------------

To run on a desktop just install:

1. pyotherside
2. python3-plainbox (from the ppa:checkbox-dev ppa)

Or create a symlink to plainbox from the py/ directory (to
../plainbox/plainbox) if you wish to work from "source"

Then you should be able to run 'qmlscene main.qml' and run the app.
