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
import QtQuick.Controls.Basic

// qmlvcp 内置控件：贴图按钮（支持精灵图、按下效果）
Item {
    id: root
    
    property string source: ""
    property string pressedSource: ""
    property bool isSprite: false
    property int spriteOrientation: 0    // 0: 横向, 1: 纵向
    property int spriteFrame: 0
    property bool enabled: true
    readonly property bool isPressed: mouseArea.pressed && enabled
    property int borderThickness: 2       // 内芯裁切边框厚度
    property int shrinkAmount: 2          // 按下时塌陷像素
    
    signal clicked()
    signal pressed()
    signal released()
    
    clip: true

    Image {
        id: bgImage
        source: root.isPressed && !root.isSprite && root.pressedSource !== "" ? root.pressedSource : root.source
        fillMode: Image.Stretch
        smooth: true
        width: root.isSprite && root.spriteOrientation === 0 ? root.width * 2 : root.width
        height: root.isSprite && root.spriteOrientation === 1 ? root.height * 2 : root.height
        x: root.isSprite && root.spriteOrientation === 0 ? -root.spriteFrame * root.width : 0
        y: root.isSprite && root.spriteOrientation === 1 ? -root.spriteFrame * root.height : 0
        opacity: (!root.enabled) ? 0.5 : 1.0
    }

    property int fw: root.isSprite && root.spriteOrientation === 0 ? (bgImage.sourceSize.width / 2) : bgImage.sourceSize.width
    property int fh: root.isSprite && root.spriteOrientation === 1 ? (bgImage.sourceSize.height / 2) : bgImage.sourceSize.height
    property int frameX: root.isSprite && root.spriteOrientation === 0 ? root.spriteFrame * fw : 0
    property int frameY: root.isSprite && root.spriteOrientation === 1 ? root.spriteFrame * fh : 0

    Image {
        source: root.source
        visible: !(root.isPressed && !root.isSprite && root.pressedSource !== "")
        sourceClipRect: Qt.rect(frameX + borderThickness, frameY + borderThickness, fw - borderThickness * 2, fh - borderThickness * 2)
        smooth: true
        x: (root.isPressed && (root.isSprite || root.pressedSource === "")) ? borderThickness + shrinkAmount : borderThickness
        y: (root.isPressed && (root.isSprite || root.pressedSource === "")) ? borderThickness + shrinkAmount : borderThickness
        width: (root.isPressed && (root.isSprite || root.pressedSource === "")) ? root.width - (borderThickness + shrinkAmount) * 2 : root.width - borderThickness * 2
        height: (root.isPressed && (root.isSprite || root.pressedSource === "")) ? root.height - (borderThickness + shrinkAmount) * 2 : root.height - borderThickness * 2
    }

    implicitWidth: root.isSprite && root.spriteOrientation === 0 ? (bgImage.sourceSize.width / 2) : bgImage.sourceSize.width
    implicitHeight: root.isSprite && root.spriteOrientation === 1 ? (bgImage.sourceSize.height / 2) : bgImage.sourceSize.height
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: root.enabled
        onClicked: root.clicked()
        onPressed: root.pressed()
        onReleased: root.released()
    }
}
