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
import Ubuntu.Components 1.3

/*! \brief Helper for delegating keypresses
    \inherits Item

    This component helps to register keystroke handlers in a human-friendly
    manner. Once handler is assigned to a given keystroke, the next time
    keyPress will be called with event matching the key combination expressed
    as registered keystroke, the supplied handler will be called.
    There are two kinds of handlers: owned (normal), and 'global'.
    Owned are registered with 'owner' parameter, that owner must match the top
    of the 'activeStack' in order for the handler to be called.
    Global handlers are handler regardless of what's on activeStack.
    Note that owned handlers take precedence over global ones. I.e. if you have
    registered two handlers for the same keystroke and the owner of the owned
    one is on activeStack, ONLY that one will be called.
    Example usage:
    KeysDelegator {
        id: keysDelegator
    }
    Keys.onPressed: keysDelegator.keyPress(event)
    (...)
    kd.setGlobalHandler('ctrl+q', Qt.quit);
    kd.setHandler('ctrl+y', yesButton.clicked);
*/

Item {

    /*!
      Gets signalled when no handler was found for given keystroke.
     */
    signal keyPressed(var event);

    /*!
      Handle a keyboard event.
      This is intended to be called as a handler for Keys.onPressed in your MainView.
     */
    function keyPress(event) {
        // build the keystroke string
        var keystroke ='';
        if (event.modifiers & Qt.AltModifier) keystroke += 'alt+';
        if (event.modifiers & Qt.ControlModifier) keystroke += 'ctrl+';
        if (event.modifiers & Qt.ShiftModifier) keystroke += 'shift+';
        keystroke += String.fromCharCode(event.key).toLowerCase();

        var ownedHandlerHit = false;
        // get the object this keystroke should be processed for
        if (activeStack.length > 0) {
            var candidate = activeStack[activeStack.length - 1];
            if (candidate in _handlers) {
                if (keystroke in _handlers[candidate]) {
                    _handlers[candidate][keystroke]();
                    ownedHandlerHit = true;
                }
            }
        }
        if (!ownedHandlerHit) {
            if (keystroke in _globalHandlers) {
                _globalHandlers[keystroke]();
            } else {
                // no handlers set, forwarding as keyPressed signal
                keyPressed(event);
            }
        }
    }

    /*!
      Make given page receive all (yet) unhandled keystrokes while it's visible.
      Note, page must have its own KeysDelegator exposed as 'keys'.
     */
    function forwardPressesWhileVisible(page) {
        var handler = function() {
            if (page.visible == true) {
                root.onKeyPressed.connect(page.keys.keyPress);
            } else {
                root.onKeyPressed.disconnect(page.keys.keyPress);
            }
        }
        page.onVisibleChanged.connect(handler);
        page.Component.onDestruction.connect(function() {
            page.onVisibleChanged.disconnect(handler);
        });
    }

    /*!
      Set handler for given keystroke.
      This function stores `handler` as the function that is to be called if
      `keystroke` is processed and owner is on the top of the activeStack.
      `keystroke` is in form of [<mod_key>+...]<key>, E.g. 'ctrl+x'

      If called with the keystroke that's already in the registry, it will
      overwrite the previous handler.
     */
    function setHandler(keystroke, owner, handler) {
        if (!(owner in _handlers)) {
            _handlers[owner] = [];
        }

        _handlers[owner][_normalizeKeystroke(keystroke)] = handler;
    }

    /*!
      Unset handler for a given keystroke for a given owner.

      It silently ignores keystroke entries that are not in the registry
     */
    function unsetHandler(keystroke, owner) {
        if (!(owner in _handlers)) {
            return;
        }
        delete _handlers[owner][_normalizeKeystroke(keystroke)];
    }

    /*!
      Unset handlers owned by the given owner.
     */
    function unsetHandlersByOwner(owner) {
        _handlers[owner] = [];
    }

    /*!
      Unset all handlers.
     */
    function unsetAllHandlers() {
        _handlers = [];
    }

    /*!
      Set global handler for a keystroke.
     */
    function setGlobalHandler(keystroke, handler) {
        _globalHandlers[_normalizeKeystroke(keystroke)] = handler;
    }

    /*!
      Unset global handler for a given keystroke.
      NOTE: owned handlers will not be affected
     */
    function unsetGlobalHandler(keystroke) {
        delete _globalHandlers[_normalizeKeystroke(keystroke)];
    }

    /*!
      Unset all global handlers.
      NOTE: owned handlers will not be affected
     */
    function unsetAllGlobalHandlers() {
        _globalHandlers = [];
    }

    property var activeStack: []

    property var _handlers : []

    property var _globalHandlers : []

    /*!
      Validate and normalize keystroke description.

      This function 'repairs' strings that depict keystroke to match following template:
      [<mod_key>+...]<key>
      where:
        * `mod_key`is one of the modifier keys defined as `allowedModifiers` below
        * given `mod_key` is supplied at most once
        * `key` is an lowercase alphanumeric character - [a-z0-9]
        * supplied `mod_key`s occur in alphabetic order

      Examples:
        _normalizeKeystroke('ctrl+alt+K') -> 'alt+ctrl+k'
        _normalizeKeystroke('Q') -> 'q'
        _normalizeKeystroke('shift+W') -> 'shift+w'

      Returns normalized keystroke
      Throws an `Error` when parsing of keystroke string failed
     */
    function _normalizeKeystroke(keystroke) {
        var allowedModifiers = ['alt', 'ctrl', 'shift'];
        var parts = keystroke.toLowerCase().split('+');
        var k = parts.pop();
        if (!k) {
           throw  new Error('Missing key in the keystroke. Got: "%1"'.arg(keystroke));
        }
        if (!k.match(/^[a-z0-9]$/)) {
            throw  new Error('Picked key "%1" is not an alphanumeric. Got: "%2"'.arg(k).arg(keystroke));
        }

        var modifiers = {}

        while (parts.length > 0) {
            var modifier = parts.shift();
            if (allowedModifiers.indexOf(modifier) < 0) {
                throw new Error('Unknown modifier key "%1". Allowed modifiers: %2'.arg(modifier).arg(allowedModifiers));
            }
            modifiers[modifier] = true;
        }
        var normalizedKeystroke = '';
        for (var i in allowedModifiers) {
            if (allowedModifiers[i] in modifiers) {
                normalizedKeystroke += allowedModifiers[i] + '+';
            }
        }
        normalizedKeystroke += k;
        return normalizedKeystroke;
    }
}
