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
import QmlVcp.Controls 1.0

// ================================================================
// Demo CNC 主界面 — 展示 Builder 可生成的所有常用控件
// ================================================================
Rectangle {
    id: root
    width: 1024
    height: 768
    color: "#1a1a2e"

    // ────────────── 顶栏：机床名称 + 状态 ──────────────
    Rectangle {
        id: titleBar
        width: parent.width; height: 50
        color: "#16213e"
        Text {
            anchors.centerIn: parent
            text: backend.machineName + " — QmlVcp Builder Demo"
            font.pixelSize: 20; color: "#e0e0e0"
        }
    }

    // ────────────── 左侧：DRO 坐标显示区 ──────────────
    Rectangle {
        id: droPanel
        x: 10; y: 60
        width: 280; height: 300
        color: "#0f3460"; radius: 8

        Column {
            anchors.centerIn: parent
            spacing: 12

            Text { text: "DRO 坐标"; font.pixelSize: 18; color: "#00d2ff"; anchors.horizontalCenter: parent.horizontalCenter }

            // X 轴
            Row { spacing: 10
                Text { text: "X:"; font.pixelSize: 24; color: "#888"; width: 30 }
                Text { text: backend.displayX.toFixed(4); font.pixelSize: 24; color: "#00ff88" }
            }
            // Y 轴
            Row { spacing: 10
                Text { text: "Y:"; font.pixelSize: 24; color: "#888"; width: 30 }
                Text { text: backend.displayY.toFixed(4); font.pixelSize: 24; color: "#00ff88" }
            }
            // Z 轴
            Row { spacing: 10
                Text { text: "Z:"; font.pixelSize: 24; color: "#888"; width: 30 }
                Text { text: backend.displayZ.toFixed(4); font.pixelSize: 24; color: "#00ff88" }
            }
            // A 轴
            Row { spacing: 10
                Text { text: "A:"; font.pixelSize: 24; color: "#888"; width: 30 }
                Text { text: backend.displayA.toFixed(4); font.pixelSize: 24; color: "#00ff88" }
            }
        }
    }

    // ────────────── 中下：JOG 方向键区 ──────────────
    Rectangle {
        id: jogPanel
        x: 10; y: 370
        width: 280; height: 260
        color: "#0f3460"; radius: 8

        Grid {
            anchors.centerIn: parent
            columns: 3; spacing: 8

            // 空位
            Item { width: 70; height: 70 }

            // Y+
            Rectangle {
                width: 70; height: 70; radius: 10; color: "#16213e"
                Text { anchors.centerIn: parent; text: "Y+"; font.pixelSize: 22; color: "#fff" }
                MouseArea { anchors.fill: parent
                    onPressed:  backend.jogAxis(1, 1)
                    onReleased: backend.jogAxis(1, 0)
                }
            }
            Item { width: 70; height: 70 }

            // X-
            Rectangle {
                width: 70; height: 70; radius: 10; color: "#16213e"
                Text { anchors.centerIn: parent; text: "X-"; font.pixelSize: 22; color: "#fff" }
                MouseArea { anchors.fill: parent
                    onPressed:  backend.jogAxis(0, -1)
                    onReleased: backend.jogAxis(0, 0)
                }
            }
            // 回零
            Rectangle {
                width: 70; height: 70; radius: 10; color: "#533483"
                Text { anchors.centerIn: parent; text: "回零"; font.pixelSize: 16; color: "#fff" }
                MouseArea { anchors.fill: parent; onClicked: backend.homeAll() }
            }
            // X+
            Rectangle {
                width: 70; height: 70; radius: 10; color: "#16213e"
                Text { anchors.centerIn: parent; text: "X+"; font.pixelSize: 22; color: "#fff" }
                MouseArea { anchors.fill: parent
                    onPressed:  backend.jogAxis(0, 1)
                    onReleased: backend.jogAxis(0, 0)
                }
            }

            Item { width: 70; height: 70 }
            // Y-
            Rectangle {
                width: 70; height: 70; radius: 10; color: "#16213e"
                Text { anchors.centerIn: parent; text: "Y-"; font.pixelSize: 22; color: "#fff" }
                MouseArea { anchors.fill: parent
                    onPressed:  backend.jogAxis(1, -1)
                    onReleased: backend.jogAxis(1, 0)
                }
            }
            Item { width: 70; height: 70 }
        }
    }

    // ────────────── 右侧：程序控制按钮 ──────────────
    Rectangle {
        id: ctrlPanel
        x: 310; y: 60
        width: 200; height: 400
        color: "#0f3460"; radius: 8

        Column {
            anchors.centerIn: parent
            spacing: 16

            Text { text: "程序控制"; font.pixelSize: 18; color: "#00d2ff"; anchors.horizontalCenter: parent.horizontalCenter }

            // 启动
            Rectangle {
                width: 150; height: 50; radius: 8; color: "#00b894"
                Text { anchors.centerIn: parent; text: "▶ 启动"; font.pixelSize: 18; color: "#fff" }
                MouseArea { anchors.fill: parent; onClicked: backend.cycleStart() }
            }
            // 暂停
            Rectangle {
                width: 150; height: 50; radius: 8; color: "#fdcb6e"
                Text { anchors.centerIn: parent; text: "⏸ 暂停"; font.pixelSize: 18; color: "#333" }
                MouseArea { anchors.fill: parent; onClicked: backend.cycleStop() }
            }
            // 急停
            Rectangle {
                width: 150; height: 50; radius: 8; color: "#d63031"
                Text { anchors.centerIn: parent; text: "■ 急停"; font.pixelSize: 18; color: "#fff" }
                MouseArea { anchors.fill: parent; onClicked: backend.emergencyStop() }
            }
            // 上电
            Rectangle {
                width: 150; height: 50; radius: 8; color: "#6c5ce7"
                Text { anchors.centerIn: parent; text: "⚡ 上电"; font.pixelSize: 18; color: "#fff" }
                MouseArea { anchors.fill: parent; onClicked: backend.machineOn() }
            }
            // 自定义计数器演示
            Rectangle {
                width: 150; height: 50; radius: 8; color: "#0984e3"
                Text { anchors.centerIn: parent; text: "累加: " + backend.customCounter; font.pixelSize: 14; color: "#fff" }
                MouseArea { anchors.fill: parent; onClicked: backend.incrementCounter() }
            }
        }
    }

    // ────────────── 右侧信息：主轴 + 状态 ──────────────
    Rectangle {
        id: infoPanel
        x: 310; y: 470
        width: 200; height: 200
        color: "#0f3460"; radius: 8

        Column {
            anchors.centerIn: parent
            spacing: 14

            Text { text: "状态信息"; font.pixelSize: 18; color: "#00d2ff"; anchors.horizontalCenter: parent.horizontalCenter }

            Text {
                text: "机床: " + backend.machineState
                font.pixelSize: 16; color: "#dfe6e9"
            }
            Text {
                text: "主轴: " + backend.spindleSpeed.toFixed(0) + " rpm"
                font.pixelSize: 16; color: "#dfe6e9"
            }
            Text {
                text: "方向: " + backend.spindleDir
                font.pixelSize: 16; color: "#dfe6e9"
            }
        }
    }

    // ────────────── GCode 预览区（占位） ──────────────
    Rectangle {
        id: gcodePreview
        x: 530; y: 60
        width: 480; height: 610
        color: "#0a0a1a"; radius: 8
        border.color: "#2d3436"; border.width: 1

        Text {
            anchors.centerIn: parent
            text: "GCodeViewer / GCodeGraphics\n控件放置区域\n\n用 Builder 拖入查看效果"
            font.pixelSize: 16; color: "#636e72"
            horizontalAlignment: Text.AlignHCenter
        }
    }

    // ────────────── 底栏 ──────────────
    Rectangle {
        id: statusBar
        y: parent.height - 30; width: parent.width; height: 30
        color: "#16213e"
        Text {
            anchors.centerIn: parent
            text: "基于 QmlVcp Builder 生成 | GPL v3"
            font.pixelSize: 12; color: "#555"
        }
    }
}
