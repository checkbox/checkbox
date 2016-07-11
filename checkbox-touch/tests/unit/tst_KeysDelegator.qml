/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
 *
 * Authors:
 * - Maciej Kisielewski <maciej.kisielewski@canonical.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import QtTest 1.0
import Ubuntu.Test 1.0
import "../../components"

Item {
    KeysDelegator {
        id: kd
    }
    UbuntuTestCase {
        name: "KeysDelegatorTestCase"
        when: windowShown

        function cleanup() {
            kd.unsetAllHandlers();
        }

        function test_normalizeKeyStroke_LowerCaseKeyOnly() {
            var result = kd._normalizeKeystroke('a');
            compare(result, 'a');
        }

        function test_normalizeKeystroke_UpperCaseKeyOnly() {
            var result = kd._normalizeKeystroke('A');
            compare(result, 'a');
        }

        function test_normalize_UnorderedModifiers() {
            var result = kd._normalizeKeystroke('shift+alt+ctrl+X');
            compare(result, 'alt+ctrl+shift+x');
        }

        function test_normalizeKeystroke_ctrlOnly() {
            var result = kd._normalizeKeystroke('ctrl+5');
            compare(result, 'ctrl+5');
        }

        function test_normalizeKeystroke_modifierRepeated() {
            var result = kd._normalizeKeystroke('ctrl+alt+alt+ctrl+q');
            compare(result, 'alt+ctrl+q');
        }

        function test_normalizeKeystroke_throws_noKey() {
            try {
                var result = kd._normalizeKeystroke('ctrl+');
                fail("Didn't fail with missing key");
            } catch (e) {
                verify(e.message.match(/Missing key in the keystroke.*/), '"Missing key" error message matches');
            }

        }

        function test_normalizeKeystroke_throws_unknownModifier() {
            try {
                var result = kd._normalizeKeystroke('select+X');
                fail("Didn't fail with unknown modifier");
            } catch (e) {
                verify(e.message.match(/Unknown modifier key.*/), '"Unknown modifier key" error message matches');
            }
        }

        function test_normalizeKeystroke_thows_badKey() {
            try {
                var result = kd._normalizeKeystroke('ctrl+[');
                fail("Didn't fail with '[' as the key");
            } catch (e) {
                verify(e.message.match(/Picked key "\[" is not an alphanumeric.*/), '"Picked key is not an alphanumeric" error message matches');
            }
        }

        function test_normalizeKeystroke_thows_reverseOrder() {
            try {
                var result = kd._normalizeKeystroke('b+ctrl');
                fail("Didn't fail with 'ctrl' as the key");
            } catch (e) {
                verify(e.message.match(/Picked key "ctrl" is not an alphanumeric.*/), '"Picked key is not an alphanumeric" error message matches');
            }
        }

        function test_endToEnd_smoke() {
            var result = 0;
            var handler = function() {
                result++;
            }
            kd.setHandler('alt+r', 'mock', handler)
            var altR = {"objectName":"","key":82,"text":"r","modifiers":134217728,"isAutoRepeat":false,"count":1,"nativeScanCode":27,"accepted":false}
            kd.activeStack.push('mock');
            kd.keyPress(altR);
            kd.activeStack.pop();
            compare(result, 1);
        }

        function test_endToEnd_unsetting() {
            var result = 0;
            var handler = function() {
                result++;
            }
            kd.setHandler('alt+e', 'mock', handler)
            kd.unsetHandler('alt+e', 'mock')
            var altE = {"objectName":"","key":69,"text":"e","modifiers":134217728,"isAutoRepeat":false,"count":1,"nativeScanCode":26,"accepted":false}
            kd.activeStack.push('mock');
            kd.keyPress(altE);
            kd.activeStack.pop();
            compare(result, 0);
        }
        function test_unsetHandler_nonExisting() {
            kd.unsetHandler('shift+m');
        }

        function test_endToEnd_overwriteHandler() {
            var result = '';
            var handlerFoo = function() {
                result += 'foo'
            }
            var handlerBar = function() {
                result += 'bar'
            }
            kd.setHandler('alt+w', 'mock', handlerFoo)
            kd.setHandler('alt+w', 'mock', handlerBar) // this should overwrite the handler, making handlerBar the one in force
            var altW = {"objectName":"","key":87,"text":"w","modifiers":134217728,"isAutoRepeat":false,"count":1,"nativeScanCode":25,"accepted":false}
            kd.activeStack.push('mock');
            kd.keyPress(altW);
            kd.activeStack.pop();
            compare(result, 'bar');
        }

        function test_endToEnd_global_smoke() {
            var result = 0;
            var handler = function() {
                result++;
            }
            kd.setGlobalHandler('ctrl+g', handler);
            var ctrlG = {"objectName":"","key":71,"text":"\u0007","modifiers":67108864,"isAutoRepeat":false,"count":1,"nativeScanCode":42,"accepted":false}
            kd.keyPress(ctrlG);
            compare(result, 1);
        }

        function test_endToEnd_global_unsetting() {
            var result = 0;
            var handler = function() {
                result++;
            }
            kd.setGlobalHandler('alt+e', handler)
            kd.unsetGlobalHandler('alt+e')
            var altE = {"objectName":"","key":69,"text":"e","modifiers":134217728,"isAutoRepeat":false,"count":1,"nativeScanCode":26,"accepted":false}
            kd.keyPress(altE);
            compare(result, 0);
        }

        function test_endToEnd_ownedOverGlobal() {
            var result = '';
            var ownedHandler = function() {
                result += 'owned';
            }
            var globalHandler = function() {
                result += 'global';
            }
            kd.setHandler('ctrl+h', 'mock', ownedHandler);
            kd.setGlobalHandler('ctrl+h', globalHandler);
            var ctrlH = {"objectName":"","key":72,"text":"\b","modifiers":67108864,"isAutoRepeat":false,"count":1,"nativeScanCode":43,"accepted":false};
            kd.activeStack.push('mock');
            kd.keyPress(ctrlH);
            kd.activeStack.pop();
            compare(result, 'owned');
        }

        function test_keyPress_capturesHandled() {
            var result = '';
            var handler = function() {
                result += 'from handler'
            }
            var signalHandler = function() {
                result += 'from signal'
            }
            kd.onKeyPressed.connect(signalHandler);

            kd.setHandler('alt+r', 'mock', handler)
            var altR = {"objectName":"","key":82,"text":"r","modifiers":134217728,"isAutoRepeat":false,"count":1,"nativeScanCode":27,"accepted":false}
            kd.activeStack.push('mock');
            kd.keyPress(altR);
            kd.activeStack.pop();
            compare(result, 'from handler');
        }

        function test_keyPress_forwardsUnhandled() {
            var result = '';
            var handler = function() {
                result += 'from handler'
            }
            var signalHandler = function() {
                result += 'from signal'
            }
            kd.onKeyPressed.connect(signalHandler);

            kd.setHandler('alt+x', 'mock', handler)
            var altR = {"objectName":"","key":82,"text":"r","modifiers":134217728,"isAutoRepeat":false,"count":1,"nativeScanCode":27,"accepted":false}
            kd.activeStack.push('mock');
            kd.keyPress(altR);
            kd.activeStack.pop();
            compare(result, 'from signal');
        }

        function test_keyPress_forwardsUnhandledAfterUnsetting() {
            var result = '';
            var handler = function() {
                result += 'from handler'
            }
            var signalHandler = function() {
                result += 'from signal'
            }
            kd.onKeyPressed.connect(signalHandler);

            kd.setHandler('alt+r', 'mock', handler)
            kd.unsetHandler('alt+r', 'mock', handler)
            var altR = {"objectName":"","key":82,"text":"r","modifiers":134217728,"isAutoRepeat":false,"count":1,"nativeScanCode":27,"accepted":false}
            kd.keyPress(altR);
            compare(result, 'from signal');
        }
    }
}

