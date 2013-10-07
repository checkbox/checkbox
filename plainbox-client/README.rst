What?
=====

PlainBox Client is an example client API (based on DBus) for PlainBox.
Currently it doesn't do much, just demonstrates how to use certain features
offered by PlainBox.


Installation
============

You will need 'colorama' to run the demo program. Just pip install it inside a
virtualenv.

Usage
=====

Just run demo.py and observe the flow of messages as you interact with
PlainBox. Note that you don't need to restart demo whenever you restart either
plainbox service or the application using it.


 - GREEN messages are displayed when something is ADDED
 - RED messages are displayed when something is REMOVED
 - YELLOW messages are displayed when something is CHANGED
 - BLUE messages are displayed for PLAINBOX SPECIFIC events
 - MAGENTA messages are displayed when plainbox SERVICE starts or quits
