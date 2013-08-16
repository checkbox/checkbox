import QtQuick 2.0
import Ubuntu.Components 0.1

Item {
    id: details_items
    height: nameRect.height + units.gu(1)

    anchors {
        right: parent.right
        left: parent.left
    }

    property alias labelName: nameLabel.text
    property alias text: nameText.text

    Label {
        id: nameLabel
        text: ""
        horizontalAlignment: Text.AlignRight
        width: units.gu(10)
        anchors {
            left: parent.left
            top: parent.top
            topMargin: units.gu(1)
            leftMargin: units.gu(1)
        }
    }

    Text {
        id: nameText
        width: parent.width - nameLabel.width - units.gu(4)
        wrapMode: Text.Wrap
        anchors {
            left: nameLabel.right
            leftMargin: units.gu(2)
            verticalCenter: nameRect.verticalCenter
        }
        text:""
    }

    Rectangle {
        id: nameRect
        height: nameText.height + units.gu(1)
        width: parent.width - nameLabel.width - units.gu(3)
        color: "transparent"
        border{
            color: UbuntuColors.warmGrey
            width: 1
        }
        anchors {
            left: nameLabel.right
            leftMargin: units.gu(1)
            top: parent.top
            topMargin: units.gu(1)
        }
    }
}
