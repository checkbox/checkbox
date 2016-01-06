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
/*! \brief QML standalone shell for confined tests
*/
import QtQuick 2.0
import Ubuntu.Components 0.1
import Ubuntu.Content 1.1
import io.thp.pyotherside 1.2

MainView {
    id: mainView
    width: units.gu(100)
    height: units.gu(75)

    // information and functionality passed to qml job component
    property var testingShell: {
        "name": "Checkbox-touch qml confined shell",
        "pageStack": pageStack,
        "python": py
    }
    property var activeTransfer;

    Arguments {
        id: args
        Argument {
            name: "job"
            help: "QML-native job to run"
            required: true
            valueNames: ["PATH"]
        }
        Argument {
            name: "checkbox-name"
            help: "Qualified name of Checkbox app to send results to"
            required: true
            valueNames: ["checkbox-touch-x.x.x"]
        }
    }

    Loader {
        id: loader
        anchors.fill: parent
        onStatusChanged: {
            if (loader.status === Loader.Error) {
                testDone({'outcome': 'crash'});
            }
        }
        onLoaded: loader.item.testDone.connect(testDone)
    }
    Python {
        id: py
        Component.onCompleted: {
            addImportPath('./confinement/');
            importModule('os', function() {});
            importModule('plainbox_confined_shell', function() {
                loader.setSource(args.values['job'],
                                 {'testingShell': testingShell});
            });
        }
    }

    function testDone(res) {
        loader.active = false;
        endPage.visible = true;
        var transfer = checkboxPeer.request()
        py.call("plainbox_confined_shell.obj_to_file", [res, 'com.ubuntu.checkbox', 'res.json'], function(resJson) {
            console.log('Result file availble @ ' + resJson);
            mainView.activeTransfer = checkboxPeer.request()
            mainView.activeTransfer.items = [ contentItemComponent.createObject(
                mainView, {url: resJson})]
            mainView.activeTransfer.state = ContentTransfer.Charged;
        });

    }
    Page {
        id: endPage
        visible: false
        anchors.fill: parent
        Label {
            anchors.fill: parent
            text: i18n.tr("Sending report - you should not see this page :-)")
        }
    }
    ContentPeer {
        id: checkboxPeer
        appId: args.values['checkbox-name']
        contentType: ContentType.Documents
        handler: ContentHandler.Destination
    }
    Connections {
        target: mainView.activeTransfer
        onStateChanged: {
            if (mainView.activeTransfer.state === ContentTransfer.Finalized) {
                var resultFile = String(mainView.activeTransfer.items[0].url).replace(
                'file://', '');
                console.log("Transfer completed; removing result file");
                py.call('os.unlink', [resultFile], function() {
                    Qt.quit();
                });
            }
        }
    }

    Component {
        id: contentItemComponent
        ContentItem {
        }
    }

    PageStack {
        id: pageStack
    }

}
