import QtQuick 2.0
import Ubuntu.Components 0.1
import QtQuick.Layouts 1.1

Page {

    signal testDone(var test);

    property var testingShell;
    onTestingShellChanged: {
        title: 'dadsads'
       //title: testingShell.getTest().id
    }
    ColumnLayout {
        spacing: units.gu(10)
        anchors {
            margins: units.gu(5)
            fill: parent
        }

        Button {
            Layout.fillWidth: true; Layout.fillHeight: true
            text: i18n.tr("Pass")
            color: "#38B44A"
            onClicked: {
                testDone({'outcome': 'pass'});
            }
        }

        Button {
            Layout.fillWidth: true; Layout.fillHeight: true
            text: i18n.tr("Fail")
            color: "#DF382C"
            onClicked: {
                testDone({"outcome": "fail"});
            }
        }
    }
}
