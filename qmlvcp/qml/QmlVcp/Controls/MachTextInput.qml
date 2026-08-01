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

TextInput {
    id: root
    
    // --- 对外暴露的核心绑定属性 ---
    property int decimals: 4         // 默认保留的小数位数（整数设为0即可）
    
    // --- 默认 UI 外观（可通过外部覆写） ---
    color: "black"
    font.pixelSize: 26
    font.bold: false
    verticalAlignment: TextInput.AlignVCenter
    horizontalAlignment: TextInput.AlignHCenter
    clip: true
    selectByMouse: true
    
    // --- CNC 工业级优化：点击获取焦点时，自动全选数值 ---
    onActiveFocusChanged: {
        if (activeFocus) {
            selectAll()
        } else {
            deselect()
        }
    }
    
    selectionColor: "#774a90e2"
    selectedTextColor: "white"
    
    // --- 白色细边框（可视化占位辅助） ---
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.color: "white"
        border.width: 1
        z: -1
    }
    
    // --- 工业级防错验证 ---
    validator: DoubleValidator {
        bottom: -9999.9999; top: 9999.9999
        decimals: root.decimals
        notation: DoubleValidator.StandardNotation
    }
    
    // --- 自动格式化逻辑 ---
    // 当按下回车键，或者用户点屏幕别的地方（失去焦点）时触发
    onEditingFinished: {
        if (text !== "") {
            var val = Number(text);
            if (!isNaN(val)) {
                text = val.toFixed(root.decimals);
                root.valueChanged(val);
            }
        }
    }
    
    // 按下回车键时主动释放焦点（去掉闪烁的光标和蓝底色）
    onAccepted: {
        focus = false
    }
    
    signal valueChanged(real newValue)
}
