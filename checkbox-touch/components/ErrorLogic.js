.import Ubuntu.Components.Popups 1.0 as Popups

function showError(caller, errorMessage, continuation, finalLabel) {
    // stackDepth keeps track of how many popups are stacked on the screen
    // we need this so continuation is called only if the last (the bottom one) popup
    // is closed
    showError.stackDepth = ++showError.stackDepth || 1;
    var popup = Qt.createComponent(Qt.resolvedUrl("ErrorDialog.qml")).createObject(caller);
    popup.errorMessage = errorMessage;
    if (showError.stackDepth > 1) {
        popup.buttonLabel = i18n.tr("Continue")
    } else {
        popup.buttonLabel = finalLabel || i18n.tr("Quit")
        popup.done.connect(function() {
            continuation();
        });
    }
    Popups.PopupUtils.open(popup.dialog);
}
