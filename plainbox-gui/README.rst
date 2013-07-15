Plainbox GUI
============

Plainbox GUI is a Qt/QML GUI running over D-Bus to control Plainbox.

Folder layout/structure

gui-engine/		Contains the D-Bus framework and C++ plugin which represents
				plainbox classes/API
				
gui-ihv/		Contains the QML/Qt "skin" which is used to drive IHV use
				cases. There may be other "skins" created later...

External Documentation Links
============================

How to test and work with gui-ihv code
======================================
To test gui-ihv:  
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
        - sudo apt-get install qt5-creator
        - sudo apt-get install ubuntu-sdk
        - sudo apt-get dist-upgrade

Once the required tools and dependencies are installed:

1. Open QT Creator
2. File->Open Project->plainbox-gui.pro
3. Build->Run
4. Interact with the UI

TBD


