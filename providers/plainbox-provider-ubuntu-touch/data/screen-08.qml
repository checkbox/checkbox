/*
 * This file is part of Checkbox.
 *
 * Copyright 2015 Canonical Ltd.
 * Written by:
 *   Maciej Kisielewski <maciej.kisielewski@canonical.com>
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
import Ubuntu.Components 1.1
import QtGraphicalEffects 1.0
import QtQuick.Window 2.1
import QtQuick.Layouts 1.1
import Plainbox 0.1

QmlJob {
    id: root

    anchors.fill: parent

    Page {
        Canvas {
            id: canvas
            anchors.fill: parent

            property var state: "preparing"
            property var visited: []
            property var radius: Screen.pixelDensity * 20
            property var visitedRadius: Math.round(radius / 1.3)
            property var pixelsLeft: Math.round(canvas.height / visitedRadius * canvas.width / visitedRadius)

            onPaint: {
                function textFillWrap(text, textX, textY, maxWidth, textHeight) {
                    // print text at textX and textY and split into multiple
                    // lines if text would exceed maxWidth. Every next line is
                    // drawn textHeight lower.
                    var words = text.split(' ');
                    var fittingLine = '';
                    for (var i = 0; i< words.length; i++) {
                        var currentLine = fittingLine + words[i] + ' ';
                        var currentWidth = ctx.measureText(currentLine).width;
                        if (i > 0  && currentWidth > maxWidth) {
                            ctx.fillText(fittingLine, textX, textY);
                            fittingLine = words[i] + ' ';
                            textY += textHeight;
                        } else {
                            fittingLine = currentLine;
                        }
                    }
                    ctx.fillText(fittingLine, textX, textY);
                }
                var ctx = getContext('2d');
                var textX = canvas.width / 2, textY = canvas.height / 2;
                var fontSize = radius / 2;
                ctx.font="%1px sans-serif".arg(fontSize);
                ctx.textAlign = "center"
                if (state==="preparing") {
                    // clear the canvas
                    ctx.fillStyle = "black";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    // draw the intruction text
                    ctx.fillStyle = "white";
                    textFillWrap(i18n.tr("Paint on the screen until fully covered with pink. Triple tap to quit"), textX, textY, canvas.width, fontSize);
                }
                if (state==="painting") {
                    var x = area.mouseX, y = area.mouseY;
                    // it's possible to go to negative values, or values beyond
                    // canvas size, by pressing and dragging outside the
                    // window (desktop). Let's cap the values
                    x = Math.max(0, x); x = Math.min(x, canvas.width);
                    y = Math.max(0, y); y = Math.min(y, canvas.height);
                    var visitedX = Math.floor(x / visitedRadius);
                    var visitedY = Math.floor(y / visitedRadius);
                    var visitedWidth = canvas.width / visitedRadius;
                    if (!visited[visitedWidth * visitedY + visitedX]) {
                        visited[visitedWidth * visitedY + visitedX] = true;
                        pixelsLeft--;
                    }
                    var grd=ctx.createRadialGradient(x, y, 0, x, y, radius);
                    grd.addColorStop(0, "#FF00FF");
                    grd.addColorStop(1, Qt.rgba(255, 0, 255, 0));
                    ctx.fillStyle=grd;

                    ctx.fillRect(x-radius, y-radius, radius*2, radius*2);

                    if (pixelsLeft < 1) {
                        state = "finished";
                    }
                }
                if (state==="finished") {
                    ctx.shadowColor = "black"
                    ctx.shadowBlur = 5;
                    ctx.fillStyle = "green"
                    ctx.strokeStyle = "green"
                    ctx.fillText(i18n.tr("Done"), textX, textY);
                    closingDelay.start();
                    return;
                }
            }
            Timer {
                id: closingDelay
                interval: 2000
                onTriggered: {
                    testDone({'outcome':'pass'});
                }
            }
            MouseArea {
                id: area
                anchors.fill: parent
                onPositionChanged: {
                    if (canvas.state === "preparing") {
                        canvas.state = "painting";
                    }
                    canvas.requestPaint();
                }
                Timer {
                    id: tripleClickTimeout
                    interval: 250

                    property var clickCount: 0
                    onTriggered: {
                        clickCount = 0;
                        stop();
                    }
                }
                onPressed: {
                    tripleClickTimeout.restart();
                    if (++tripleClickTimeout.clickCount > 2) {
                        testDone({'outcome':'fail'});
                        tripleClickTimeout.stop();
                        tripleClickTimeout.clickCount = 0;
                    }
                }
            }
        }
    }
}
