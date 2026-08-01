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

import QtQuick

// qmlvcp 内置控件：双帧 LED 指示灯（精灵图左右/上下各一帧）
Item {
    id: root
    
    property string source: ""
    property bool active: false
    property bool isHorizontal: true
    
    width: isHorizontal ? (ledImage.sourceSize.width / 2) : ledImage.sourceSize.width
    height: isHorizontal ? ledImage.sourceSize.height : (ledImage.sourceSize.height / 2)
    
    clip: true
    
    Image {
        id: ledImage
        source: root.source
        x: root.active && root.isHorizontal ? -width / 2 : 0
        y: root.active && !root.isHorizontal ? -height / 2 : 0
    }
}
