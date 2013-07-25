import QtQuick 2.0
import Ubuntu.Components 0.1
import Ubuntu.Components.Popups 0.1


Dialog {
    id: file_dialog
    title: i18n.tr("Save Report")
    text: i18n.tr("Please choose a directory to save the report.")




    Button {
        id: save
        text: i18n.tr("OK")
        onClicked: {

            // TODO this is where to call the SaveAs Dialog
            //directory.fileContent = "abc"
            //directory.filename = "test.txt"
            //directory.saveFile()
            //PopupUtils.close(file_dialog)
        }
    }


    Button {
        id: cancel
        text: i18n.tr("Cancel")
        color: UbuntuColors.warmGrey
        onClicked: PopupUtils.close(file_dialog)
    }

}
