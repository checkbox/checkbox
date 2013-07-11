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
To test gui-ihv:  
	Software Needed:
		QT Creator (2.7.0 or greater)  
		Ubuntu.Components 0.1 - This is part of the Ubunutu distribution 
			and gets updated

1. Open QT Creator
2. File->Open Project->plainbox-gui.pro
3. Build->Run
4. Interact with the UI

TBD


