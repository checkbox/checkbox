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

            // FYI, in QT 5, here's how to do it
            //                  import QtQuick 2.1
            //                  import QtQuick.Controls 1.0
            // fileDialog.open()
            // ..... path is returned in fileDialog.fileUrls

            onClicked: PopupUtils.close(file_dialog)
        }
    }


    Button {
        id: cancel
        text: i18n.tr("Cancel")
        color: UbuntuColors.warmGrey
        onClicked: PopupUtils.close(file_dialog)
    }

    // FYI in QT 5, this is how to use a save as dialog
    //
    //FileDialog {
    //    id: fileDialog
    //    title: "Please select a folder to save to:"
    //    selectFolder : true
    //    onAccepted: {
    //        console.log("You chose: " + fileDialog.fileUrls)
    //    }
     //   onRejected: {
     //       console.log("Canceled")
     //   }

}
