
import QtQuick 2.2

Item {
    id: smsTest

    anchors.fill: parent


    property var testingShell
    signal testDone(var test)
    
    GenericSmsTest {
        id: testPages

        Component.onCompleted: {
            testPages.setTestActionText("Send an SMS containing a URL and"
                + " confirm it is displayed correctly...")
            
            testPages.setPredefinedContent("The message contains both text"
                + " & a URL www.ubuntu.com Does it look good?")
        }
    }
}



