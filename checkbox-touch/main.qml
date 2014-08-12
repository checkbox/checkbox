import QtQuick 2.0
import Ubuntu.Components 0.1
import "components"
import io.thp.pyotherside 1.2


/*!
    \brief MainView with a Label and Button elements.
*/

MainView {
    // objectName for functional testing purposes (autopilot-qt5)
    objectName: "mainView"

    // Note! applicationName needs to match the "name" field of the click manifest
    applicationName: "com.canonical.certification.checkbox-touch"

    /*
     This property enables the application to change orientation
     when the device is rotated. The default is false.
    */
    //automaticOrientation: true

    width: units.gu(100)
    height: units.gu(75)

    Python {
        id: python
        Component.onCompleted: {
            console.log("Using pyotherside " + python.pluginVersion());
            console.log("Using python " + python.pythonVersion());
            welcomeText.text = i18n.tr("Welcome text (python loaded)");
        }
        onError: {
            console.error("python error: " + traceback)
        }
    }

    Page {
        id: welcomePage
        title: i18n.tr("System Testing")
        anchors.bottomMargin: units.gu(1)
        Column {
            anchors.margins: units.gu(1)
            spacing: units.gu(1)
            id: column1
            anchors {
                fill: parent
            }
            Text {
                id: welcomeText
                text: i18n.tr("Welcome text")
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: units.gu(4)
            }
        }
        Button {
            color: "green"
            text: i18n.tr("Start Testing")
            anchors.right: parent.right
            anchors.rightMargin: units.gu(2)
            anchors.left: parent.left
            anchors.leftMargin: units.gu(2)
            anchors.bottom: parent.bottom
            anchors.bottomMargin: units.gu(1)
            transformOrigin: Item.Center
        }

        Component.onCompleted: {
            console.log("welcome page ready");
        }
    }
}
