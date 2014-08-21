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

The click package is built from QML/JavaScript/Python code contained in the
`py` and `components` directories. It also has `lib` directory that contains
all necessary libraries needed to run checkbox-touch.

Before building click package make sure you run `./get-libs` to initialize and
populate `./lib` directory.
To build the click package run `$ click build path_to_checkbox-touch`.

Deploying on the device
-----------------------

To run install package on the device/emulator run :

`$ adb push com.canonical.certification.checkbox-touch_0.2_armhf.click`
`/home/phablet/`

`$ phablet-shell`

`phablet@ubuntu-phablet:$ pkcon install-local`
`com.canonical.certification.checkbox-touch_0.2_armhf.click`

`phablet@ubuntu-phablet:$ exit`


Running on a desktop
--------------------

To run on a desktop run `qmlscene main.qml`
Note: Make sure you've ran `./get-libs` first.


