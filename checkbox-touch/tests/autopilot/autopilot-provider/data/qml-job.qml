import QtQuick 2.0
import Ubuntu.Components 0.1
import QtQuick.Layouts 1.1

import Plainbox 0.1

QmlJob {
    id: root

    Component.onCompleted: testingShell.pageStack.push(testPage)

    Page {
        id: testPage
        objectName: "qmlTestPage"
        ColumnLayout {
            spacing: units.gu(10)
            anchors {
                margins: units.gu(5)
                fill: parent
            }

            Button {
                objectName: "passButton"
                Layout.fillWidth: true; Layout.fillHeight: true
                text: i18n.tr("Pass")
                color: "#38B44A"
                onClicked: {
                    testDone({'outcome': 'pass'});
                }
            }

            Button {
                objectName: "failButton"
                Layout.fillWidth: true; Layout.fillHeight: true
                text: i18n.tr("Fail")
                color: "#DF382C"
                onClicked: {
                    testDone({"outcome": "fail"});
                }
            }
        }
    }
}
