/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Jonathan Cave <jonathan.cave@canonical.com>
 *
 * Checkbox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3,
 * as published by the Free Software Foundation.
 *
 * Checkbox is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import io.thp.pyotherside 1.2

Python {
    id: ofonoDbus

    Component.onCompleted: {
        setHandler('got-modem-list', gotModemList)

        addImportPath(Qt.resolvedUrl('.'));
        importModule('telephony_helper', function(success) {
            console.assert(success)
        });
        console.debug("telephony_helper import")
    }

    signal gotModemList(var resultsList)

    function th_get_modem_list(list) {
        console.debug("th_get_modems")
        call('telephony_helper.get_modems', [])
    }

    function th_send_sms(path, number, text) {
        console.debug("th_send_sms")
        call('telephony_helper.send_sms', [path, number, text])
    }
}