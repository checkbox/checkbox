
import QtQuick 2.2

Item {
    id: smsTest

    anchors.fill: parent


    property var testingShell
    signal testDone(var test)
    
    GenericSmsTest {
        id: testPages

        Component.onCompleted: {
            testPages.setTestActionText("Send an SMS message to a"
                                        + " single contact...")
            
            testPages.setPredefinedContent("The aim of art is to represent not"
                    + " the outward appearance of things, but their inward"
                    + " significance. Aristotle")
        }
    }
}



