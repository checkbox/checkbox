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
        Column {
            spacing: units.gu(1)
            id: column1
            anchors {
                margins: units.gu(2)
                fill: parent
            }

            Text {
                id: welcomeText

                text: i18n.tr("Welcome")
                font.pixelSize: units.gu(4)
            }

            Button {
                width: parent.width
                height: gu
                color: "#009E0F"
                text: i18n.tr("Start Testing")
                anchors.verticalCenter: parent.verticalCenter
                transformOrigin: Item.Center
            }

        }
    }
}
