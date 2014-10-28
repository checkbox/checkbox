.import Ubuntu.Components.Popups 1.0 as Popups

function confirmRequest(caller, options, continuation) {
    // if the question was answered before and user selected to
    // remember their selection - 'returning' true
    if (mainView.appSettings[options.question]) {
        continuation(true);
        return;
    }
    var popup = Qt.createComponent(Qt.resolvedUrl("ConfirmationDialog.qml")).createObject(caller);
    popup.withRemember = options.remember;
    popup.question = options.question;
    popup.answer.connect(function(result, remember) {
        mainView.appSettings[options.question] = remember;
        continuation(result);
    });
    Popups.PopupUtils.open(popup.dialog);
}
