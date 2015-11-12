/*
 * This file is part of Checkbox
 *
 * Copyright 2015 Canonical Ltd.
 *
 * Authors:
 * - Sylvain Pineau <sylvain.pineau@canonical.com>
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

/*! \Pie Chart component

    Using the canvas element.
*/

import QtQuick 2.0

Canvas {
    id: canvas

    property var chartData;
    property var borderColor: "#ECECEC";
    property int borderWidth: 1;
    property real progress: 0;
    property alias duration: animation.duration;

    onPaint: {
        var centreX = width / 2;
        var centreY = height / 2;
        var size = Math.min(width, height) / 2;
        var total = 0;
        for (var i = 0; i < chartData.length; i++) total += chartData[i].value;
        var arcTotal = -Math.PI / 2;
        var ctx = getContext("2d");
        ctx.reset();
        for (var i = 0; i < chartData.length; i++) {
            var arc = progress * chartData[i].value / total * Math.PI / 50;
            ctx.beginPath();
            ctx.fillStyle = chartData[i].color;
            ctx.moveTo(centreX, centreY);
            ctx.arc(centreX, centreY, size, arcTotal, arc + arcTotal);
            ctx.lineTo(centreX, centreY);
            ctx.fill();
            ctx.lineWidth = borderWidth;
            ctx.strokeStyle = borderColor;
            ctx.stroke();
            arcTotal += arc;
        }
        animation.start();
    }

    onProgressChanged: {
        requestPaint();
    }

    function repaint() {
        progress = 0;
        animation.start();
    }

    PropertyAnimation {
        id: animation;
        target: canvas;
        property: "progress";
        to: 100;
        duration: 1000; // milliseconds
    }
}
