import QtQuick 2.0
import Ubuntu.Components 0.1

Item {


        Rectangle {
            anchors.fill: parent
            color: Theme.palette.normal.overlay
            border.color: "black"
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "Test details"
            }

            Rectangle {
                anchors.right: parent.right
                height: parent.height
                width: parent.width - units.gu(40)
                color: Theme.palette.normal.overlay
                border.color: "black"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "Test details"
                }
            }

        }
    }

