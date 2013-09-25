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
    property alias textFormat: nameText.textFormat

    Label {
        id: nameLabel
        text: ""
        color: Qt.rgba(1, 1, 1, 0.9)
        width: units.gu(10)
        anchors {
            left: parent.left
            leftMargin: units.gu(1)
            verticalCenter: nameRect.verticalCenter
        }
    }

    Rectangle {
        id: nameRect
        height: nameText.height + units.gu(1)
        width: parent.width - nameLabel.width - units.gu(3)
        color: Theme.palette.normal.background
        antialiasing: true
        radius: 6
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

    TextEdit {
        id: nameText
        width: parent.width - nameLabel.width - units.gu(4)
        wrapMode: Text.Wrap
        anchors {
            left: nameLabel.right
            leftMargin: units.gu(2)
            verticalCenter: nameRect.verticalCenter
        }
        selectionColor: Theme.palette.selected.foreground
        selectedTextColor: Theme.palette.selected.background
        text:""
        selectByMouse: true
        readOnly: true
    }
}
