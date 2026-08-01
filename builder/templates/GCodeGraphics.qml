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

Rectangle {
    x: $x
    y: $y
    width: $w
    height: $h
    color: "$bgColor"
    border.color: "white"
    border.width: 2
    clip: true
    GCodeGraphics {
        anchors.fill: parent
		anchors.margins: 2
        showWorkAxes: $showWorkAxes
        isOrthographic: $isOrthographic
        cameraZoom: $cameraZoom
    }
    Text {
        z: 1
        x: 5
        y: 5
        text: "刀具: " + status.toolInSpindle
        font.pixelSize: 12
        font.bold: true
        color: "white"
    }
}