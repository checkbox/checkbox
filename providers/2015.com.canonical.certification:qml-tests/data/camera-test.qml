import QtQuick 2.0
import Ubuntu.Components 1.1
import QtMultimedia 5.0
import QtQuick.Layouts 1.1
Page {
    signal testDone(var test)
    property var testingShell
    title: i18n.tr("Camera test")

    ColumnLayout {
        spacing: units.gu(5)
        anchors.fill: parent
        anchors.margins: units.gu(3)
        Label {
            fontSize: "large"
            Layout.fillWidth: true
            wrapMode: Text.WrapAtWordBoundaryOrAnywhere
            text: i18n.tr("On the next screen you'll see video feed from your \
camera. Decide whether camera is working correctly, and tap corresponding \
button.")
            font.bold: true
        }
        Button {
            text: i18n.tr("Start the test")
            Layout.fillWidth: true
            onClicked: {
                testingShell.pageStack.push(subpage);
            }
        }
    }

    Page {
        id: subpage
        title: i18n.tr("Camera test")
        VideoOutput {
            id: viewfinder
            source: cam
            anchors.fill: parent
            orientation: 270
        }

        Camera {
            id: cam
        }

        ColumnLayout {
            spacing: units.gu(1)
            anchors {
                fill: parent
            }
            Button {
                width: units.gu(10)
                height: units.gu(5)
                Layout.alignment: Qt.AlignHCenter
                text: i18n.tr("Camera works")
                color: UbuntuColors.green
                onClicked: {
                    testDone({'outcome': 'pass'});
                }
            }
            Button {
                width: units.gu(10)
                height: units.gu(5)
                Layout.alignment: Qt.AlignHCenter
                text: i18n.tr("Camera doesn't work")
                color: UbuntuColors.red
                onClicked: {
                    testDone({'outcome': 'fail'});
                }
            }
        }

    }
}
