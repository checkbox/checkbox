import QtQuick 2.0
import Ubuntu.Components 0.1
import "components"

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
            width: parent.width
            color: "green"
            text: i18n.tr("Start Testing")
            anchors.bottom: parent.bottom
            transformOrigin: Item.Center
        }
    }
}
