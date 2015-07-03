
import QtQuick 2.2

Item {
    id: smsTest

    anchors.fill: parent


    property var testingShell
    signal testDone(var test)
    
    GenericSmsTest {
        id: testPages

        Component.onCompleted: {
            testPages.setTestActionText("Send an SMS message containing a"
                + " & to a contact and confirm it is displayed correctly")
            
            testPages.setPredefinedContent("I like sending SMSs & getting"
                + " replies! Especially if they are about kittens & puppies.")
        }
    }
}



