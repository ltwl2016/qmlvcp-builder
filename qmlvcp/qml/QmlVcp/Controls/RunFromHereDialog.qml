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
import QtQuick.Layouts

Popup {
    id: root
    property int targetLine: -1
    
    // 弹窗对外暴露的确认信号，附带高级参数对象
    signal runConfirmed(int line, var options)
    
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    width: 600
    height: 500
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    
    background: Rectangle {
        color: "#eeeeee"
        border.color: "#cc0000"
        border.width: 3
        radius: 8
    }
    
    Column {
        anchors.centerIn: parent
        spacing: 15
        width: parent.width * 0.9
        
        Text {
            text: "⚠️ 高级五轴安全起步中心 (第 " + root.targetLine + " 行)"
            font.pixelSize: 22
            font.bold: true
            color: "#cc0000"
            anchors.horizontalCenter: parent.horizontalCenter
        }
        
        GridLayout {
            columns: 2
            rowSpacing: 10
            columnSpacing: 20
            anchors.horizontalCenter: parent.horizontalCenter
            
            // 1. WCS
            Text { text: "工件坐标系:"; font.pixelSize: 16 }
            ComboBox {
                id: cbWcs
                model: ["G54", "G55", "G56", "G57", "G58", "G59"]
                width: 200
                font.pixelSize: 16
            }
            
            // 2. Spindle
            CheckBox { 
                id: chkSpindle; text: "主轴控制"; checked: true; font.pixelSize: 16 
            }
            Row {
                spacing: 10
                enabled: chkSpindle.checked
                ComboBox {
                    id: cbSpindleDir
                    model: ["M3 (正转)", "M4 (反转)"]
                    width: 120
                    font.pixelSize: 16
                }
                TextField {
                    id: txtSpindleSpeed
                    text: "10000"
                    width: 70
                    font.pixelSize: 16
                }
            }
            
            // 3. Coolant
            CheckBox {
                id: chkCoolant
                text: "开启冷却液 (M8)"
                checked: false
                font.pixelSize: 16
            }
            Item { width: 1; height: 1 } // placeholder
            
            // 4. G43 Tool Length
            CheckBox {
                id: chkG43
                text: "开启长度补偿 (G43 H)"
                checked: true
                font.pixelSize: 16
            }
            Row {
                spacing: 10
                enabled: chkG43.checked
                Text { text: "刀号:"; font.pixelSize: 16; anchors.verticalCenter: parent.verticalCenter }
                TextField {
                    id: txtToolNumber
                    text: "1"
                    width: 60
                    font.pixelSize: 16
                }
            }
            
            // 5. RTCP M428
            CheckBox {
                id: chkRtcp
                text: "开启五轴 RTCP (M428 Q)"
                checked: false
                font.pixelSize: 16
                onCheckedChanged: {
                    if (checked) chkRtcpCancel.checked = false
                }
            }
            Row {
                spacing: 10
                enabled: chkRtcp.checked
                Text { text: "Q参数:"; font.pixelSize: 16; anchors.verticalCenter: parent.verticalCenter }
                TextField {
                    id: txtRtcpQ
                    text: "1"
                    width: 60
                    font.pixelSize: 16
                }
            }
            
            // 6. RTCP Cancel M429
            CheckBox {
                id: chkRtcpCancel
                text: "强制关闭 RTCP (M429)"
                checked: false
                font.pixelSize: 16
                onCheckedChanged: {
                    if (checked) chkRtcp.checked = false
                }
            }
            Item { width: 1; height: 1 } // placeholder
            
            // 7. Single Block
            CheckBox {
                id: chkSingleBlock
                text: "开启安全单步 (发车即暂停)"
                checked: true
                font.pixelSize: 16
                Layout.columnSpan: 2
            }
        }
        
        Text {
            text: "提示：主轴、冷却、刀补若不勾选，将默认强制下发取消指令 (M5/M9/G49)。\nRTCP 为独立控制，请明确勾选开启或关闭。"
            font.pixelSize: 14
            color: "#666"
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
        }
        
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 50
            
            Button {
                text: "取消 (Cancel)"
                width: 130; height: 45
                font.pixelSize: 16
                onClicked: root.close()
            }
            
            Button {
                text: "强制启动 (START)"
                width: 130; height: 45
                font.pixelSize: 16
                font.bold: true
                background: Rectangle {
                    color: parent.down ? "#990000" : "#cc0000"
                    radius: 4
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    var target = root.targetLine;
                    var opts = {
                        "wcs": cbWcs.currentText,
                        "spindleEnabled": chkSpindle.checked,
                        "spindleDir": cbSpindleDir.currentIndex === 0 ? "M3" : "M4",
                        "spindleSpeed": parseInt(txtSpindleSpeed.text) || 0,
                        "coolantOn": chkCoolant.checked,
                        "g43Enabled": chkG43.checked,
                        "toolNumber": parseInt(txtToolNumber.text) || 0,
                        "rtcpEnabled": chkRtcp.checked,
                        "rtcpQ": parseInt(txtRtcpQ.text) || 0,
                        "rtcpCancel": chkRtcpCancel.checked,
                        "singleBlock": chkSingleBlock.checked
                    };
                    root.close();
                    root.runConfirmed(target, opts);
                }
            }
        }
    }
}
