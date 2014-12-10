.import Ubuntu.Components.Popups 1.0 as Popups

function showDialog(caller, message, buttons) {
    var p = Qt.createComponent(Qt.resolvedUrl("CbtDialog.qml")).createObject(caller);
    p.buttons = buttons || [{ "text": i18n.tr("OK"), "color": "UbuntuColors.green"}];
    p.label = message;
    Popups.PopupUtils.open(p.dialog);
}
