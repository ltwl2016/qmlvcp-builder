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

// qmlvcp 通用 HAL 输入监视器
// 监听任意全局 HAL 引脚（如 motion.probe-input），实时刷新。
//
// 暴露两个属性:
//   active : bool   — 引脚是否为真（bit=1 / float≠0 / int≠0），适合驱动 LED 等开关
//   value  : var    — 引脚原始值（bit/float/s32/u32 原样透传），适合显示数值
//
// 用法:
//   HalInputMonitor {
//       id: probeMonitor
//       pin: "motion.probe-input"
//   }
//   // 开关用途:
//   MachLED { active: probeMonitor.active }
//   // 数值用途:
//   Text { text: probeMonitor.value }
Item {
    id: root

    // 要监听的全局 HAL 引脚名（在 hal_manager 的 watchSysPin 轮询范围内）
    property string pin: ""
    // 引脚当前是否有效（bit 引脚 =1 / float 非 0 / int 非 0 视为 true）
    property bool active: false
    // 引脚原始值（bit/float/s32/u32 原样透传）
    property var value: false

    // 初次加载即读取一次当前值，避免等待下一次轮询才刷新
    Component.onCompleted: {
        if (root.pin) {
            hal.watchSysPin(root.pin)
            var v = hal.getPin(root.pin)
            root.value = v
            root.active = toBool(v)
        }
    }

    // 引脚发生变化时由 hal_manager 的 sysPinChanged 通知刷新
    Connections {
        target: hal
        function onSysPinChanged(name, value) {
            if (name === root.pin) {
                root.value = value
                root.active = toBool(value)
            }
        }
    }

    // 辅助：把 HAL 值转成 bool（bit/float/s32 都兼容）
    function toBool(val) {
        return val !== 0 && val !== "0" && val !== false && val !== null && val !== undefined
    }
}
