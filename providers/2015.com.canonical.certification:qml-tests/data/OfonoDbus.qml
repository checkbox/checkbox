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
        importModule('telephony_shim', function(success) {
            console.assert(success)
        });
        console.debug("telephony_shim import")
    }

    signal gotModemList(var resultsList)

    function ts_get_modem_list(list) {
        console.debug("ts_get_modems")
        call('telephony_shim.get_modems', [])
    }

    function ts_send_sms(path, number, text) {
        console.debug("ts_send_sms")
        call('telephony_shim.send_sms', [path, number, text])
    }

    onError: {
        console.error("python error: " + traceback);
    }
}