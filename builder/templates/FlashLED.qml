// QmlVcp Builder - CNC HMI Visual Construction Toolkit
// Copyright (C) 2026 ltwl2016
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

Item {
    x: $x
    y: $y
    width: $w
    height: $h
    property bool flashState: false

    Timer {
        running: $bind
        repeat: true
        interval: $interval
        onTriggered: parent.flashState = !parent.flashState
        onRunningChanged: if (!running) parent.flashState = false
    }

    Image {
        anchors.fill: parent
        source: assetsDir + "/assets/$src"
        sourceClipRect: ($bind && parent.flashState) ? Qt.rect($w, 0, $w, $h) : Qt.rect(0, 0, $w, $h)
    }
}