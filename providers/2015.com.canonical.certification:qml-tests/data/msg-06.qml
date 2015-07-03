
import QtQuick 2.2

Item {
    id: smsTest

    anchors.fill: parent


    property var testingShell
    signal testDone(var test)
    
    GenericSmsTest {
        id: testPages

        Component.onCompleted: {
            testPages.setTestActionText("Send an SMS Message to a contact"
                + " containing special characters...")
            
            testPages.setPredefinedContent("!\"£$%😆^&*()😁")
        }
    }
}



