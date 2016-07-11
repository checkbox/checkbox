.import Ubuntu.Components.Popups 1.0 as Popups

.import QtQuick 2.0 as QtQuick

function confirmRequest(caller, options, continuation) {
    // if the question was answered before and user selected to
    // remember their selection - 'returning' true
    if (mainView.appSettings[options.question]) {
        continuation(true);
        return;
    }
    var component = Qt.createComponent(Qt.resolvedUrl("ConfirmationDialog.qml"));
    if (component.status == QtQuick.Component.Error) {
        var msg = i18n.tr("could not create ConfirmationDialog component\n'") + component.errorString();
        console.error(msg);
        ErrorLogic.showError(mainView, msg, Qt.quit, i18n.tr("Quit"));
    }
    var popup = component.createObject(caller);

    popup.withRemember = options.remember;
    popup.question = options.question;
    popup.answer.connect(function(result, remember) {
        mainView.appSettings[options.question] = remember;
        continuation(result);
    });
    Popups.PopupUtils.open(popup.dialog);
}
