/*
 * This file is part of Checkbox
 *
 * Copyright 2014 Canonical Ltd.
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

/*! \brief Page for test results

    This page displays a pie charts and test results stats
    See design document at: http://goo.gl/6Igmhn
*/

import QtQuick 2.0
import Ubuntu.Components 1.1
import QtQuick.Layouts 1.1
import "vendor/qchart_js"
import "vendor/qchart_js/QChart.js" as Charts

Page {
    title: i18n.tr("Test Results")
    visible: false

    property var results: {"totalPassed": 0, "totalFailed": 0, "totalSkipped": 0}
    signal saveReportClicked()
    signal endTesting()

    head {
        actions: [
            Action {
                iconName: "window-close"
                text: i18n.tr("Close")
                onTriggered: endTesting();
            }
        ]
    }

    onResultsChanged: {
        chart_pie.chartData = [
            {
                value: results.totalPassed,
                color:"#6AA84F",
            },
            {
                value: results.totalFailed,
                color: "#DC3912",
            },
            {
                value: results.totalSkipped,
                color: "#FF9900",
            }];
        chart_pie.repaint();
    }

    ColumnLayout {
        spacing: units.gu(2)
        anchors.margins: units.gu(3);
        anchors.fill: parent

        Label {
            fontSize: "x-large"
            text: "Summary"
        }

        Chart {
            id: chart_pie;
            Layout.fillHeight: true
            Layout.fillWidth: true
            chartAnimated: true;
            chartAnimationEasing: Easing.Linear;
            chartAnimationDuration: 1000;
            chartType: Charts.ChartType.PIE;
            chartOptions: {"segmentStrokeColor": "#ECECEC"};
        }

        Column {
            id: legend
            Row {
                spacing: units.gu(1)
                Text {
                    text: "█"
                    color:"#6AA84F"
                }
                Text {
                    text: results.totalPassed + " tests passed"
                }
            }
            Row {
                spacing: units.gu(1)
                Text {
                    text: "█"
                    color:"#DC3912"
                }
                Text {
                    text: results.totalFailed + " tests failed"
                }
            }
            Row {
                spacing: units.gu(1)
                Text {
                    text: "█"
                    color:"#FF9900"
                }
                Text {
                    text: results.totalSkipped + " tests skipped"
                }
            }
        }

        LatchButton {
            id: saveResultsButton
            unlatchedColor: UbuntuColors.green
            Layout.fillWidth: true
            text: i18n.tr("Save detailed report")
            onLatchedClicked: saveReportClicked();
        }
    }
}
