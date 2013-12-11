Checkbox GUI
============

Checkbox GUI is a Qt/QML GUI running over D-Bus to control Plainbox.

Folder layout/structure

gui-engine/		Contains the D-Bus framework and C++ plugin which represents
				plainbox classes/API
				
checkbox-gui/   Contains the QML/Qt "skin" which is used to drive testing.
                There may be other "skins" created later...

External Documentation Links
============================

How to test and work with checkbox-gui code
======================================
To test checkbox-gui:  
	Software Needed:
		QT Creator (2.7.0 or greater)  
		Ubuntu.Components 0.1 - This is part of the Ubunutu distribution 
			and gets updated
    How to install:
        Run the mk-venv script on the top level directory, this will add the
        required PPAs and install the needed packages.
        Optionally, to install manually:
        - sudo apt-add-repository ppa:ubuntu-sdk-team/ppa
        - sudo apt-add-repository ppa:canonical-qt5-edgers/qt5-proper
        - sudo apt-get update
        - sudo apt-get install qtcreator
        - sudo apt-get install ubuntu-sdk
        - sudo apt-get dist-upgrade

*NEW*. Since the UI is now getting live data through dbus, a plainbox service is required:

- Open a new terminal
- Change to the branch's top directory and run:
  $ mk-venv /tmp/plainbox-venv
- Activate the venv:
  $ . /tmp/plainbox-venv/bin/activate #Note the dot is significant
- Run plainbox in service mode:
  $ plainbox service


Once the required tools and dependencies are installed:

1. Open QT Creator
2. File->Open Project->checkbox-gui.pro
3. Build->Run
4. Interact with the UI

There seems to be a visual glitch when starting the UI (step 3). You may notice
that a "ghost" window opens, this looks like qt creator but it's a "mirror" or
bitmap of that window. This is the actual application window. To make it react,
simply try to move it around, or close it and restart it (the ghost window,
not qt creator itself). This bug has been reported and is being looked at.

TBD


