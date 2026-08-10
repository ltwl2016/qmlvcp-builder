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

// qmlvcp 内置控件：自锁贴图按钮
// 点一下锁定（显示备用贴图并保持按下状态），再点一下解锁。
// 视觉/交互参考 MachImageButton，但自锁状态由本组件自行管理。
Item {
    id: root

    property string source: ""
    property string pressedSource: ""
    property bool enabled: true

    // 锁定状态（外部绑定属性，接收 $bind 绑定的外部信号）
    property bool latched: false

    // 内部翻转状态（点击控制，视觉/信号基于此；外部信号通过 onLatchedChanged 跟随）
    property bool internalToggle: false

    // 锁定状态变化信号，供模板挂接动作（对应 action_press / action_release）
    signal pressed()
    signal released()

    // 翻转内部状态（供点击触发）
    function toggle() {
        root.internalToggle = !root.internalToggle
    }

    // 视觉：锁定态且备用贴图非空 → 显示 pressedSource；否则显示 source（双图机制，参考 MachImageButton）
    Image {
        anchors.fill: parent
        source: root.internalToggle && root.pressedSource !== "" ? root.pressedSource : root.source
        fillMode: Image.Stretch
        smooth: true
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: root.enabled
        onClicked: root.toggle()
    }

    // 外部信号（latched）变化 → 内部状态跟随其电平
    onLatchedChanged: root.internalToggle = root.latched

    // 内部状态翻转时触发对应动作信号
    onInternalToggleChanged: {
        if (root.internalToggle) {
            root.pressed()      // 锁定 → 触发锁定动作
        } else {
            root.released()     // 解锁 → 触发解锁动作
        }
    }
}
