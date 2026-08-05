# QmlVcp Builder - CNC HMI Visual Construction Toolkit
# Copyright (C) 2026 ltwl2016
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# ────────────────────────────────────────────────────────────────
#  控件定义汇总 — 每个控件一个 CONTROL dict
# ────────────────────────────────────────────────────────────────

CONTROLS = [
    {  # ── 基础控件 ──
        "type":        "Image",
        "displayName": "Image",
        "category":    "基础控件",
        "properties":  ["source", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "Image",
    },
    {
        "type":        "Rectangle",
        "displayName": "Rectangle",
        "category":    "基础控件",
        "properties":  ["bgColor", "border", "borderW", "borderC", "container", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100, "bgColor": "#333333", "border": False, "borderW": 1, "borderC": "#ffffff"},
        "template":    "Rectangle",
    },
    {
        "type":        "Text (Label)",
        "displayName": "Text (Label)",
        "category":    "基础控件",
        "properties":  ["text", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 40, "text": "Label"},
        "template":    "Text (Label)",
    },

    {  # ── 按钮 ──
        "type":        "ImageButton",
        "displayName": "贴图按钮",
        "category":    "按钮",
        "properties":  ["source", "action", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "ImageButton",
    },
    {
        "type":        "SpriteButton",
        "displayName": "精灵按钮",
        "category":    "按钮",
        "properties":  ["source", "action", "half", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "SpriteButton",
    },
    {
        "type":        "JOGButton",
        "displayName": "JOG控制按钮",
        "category":    "按钮",
        "properties":  ["source", "action_press", "action_release", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "JOGButton",
    },
    {
        "type":        "EmergencyStop",
        "displayName": "急停按钮",
        "category":    "按钮",
        "properties":  ["half", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "EmergencyStop",
    },

    {  # ── 显示控件 ──
        "type":        "GCodeGraphics",
        "displayName": "GCode轨迹图3D",
        "category":    "显示控件",
        "properties":  ["showWorkAxes", "isOrthographic", "cameraZoom", "allowSelection", "activeLine", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 400, "h": 300},
        "template":    "GCodeGraphics",
    },
    {
        "type":        "GCodeViewer",
        "displayName": "GCode文本查看器",
        "category":    "显示控件",
        "properties":  ["allowSelection", "activeLine", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 400, "h": 300},
        "template":    "GCodeViewer",
    },
    {
        "type":        "Text (DRO)",
        "displayName": "数字 (DRO)",
        "category":    "显示控件",
        "properties":  ["axis", "decimals", "unit", "value", "text", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 40, "axis": "x"},
        "template":    "Text (DRO)",
    },            
    { # ── 输入框 ──
        "type":        "MachTextInput",
        "displayName": "数值输入框",
        "category":    "输入框",
        "properties":  ["pinName", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 50},
        "template":    "MachTextInput",
    },
    {
        "type":        "TextField",
        "displayName": "MDI输入框",
        "category":    "输入框",
        "properties":  ["placeholder", "text", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 50},
        "template":    "TextField",
    },    

    {  # ── 指示灯 ──
        "type":        "LED",
        "displayName": "普通LED灯",
        "category":    "指示灯",
        "properties":  ["pinName", "half", "defaultColor", "activeColor", "inactiveColor", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 40, "h": 40},
        "template":    "LED",
    },
    {
        "type":        "FlashLED",
        "displayName": "闪烁LED灯",
        "category":    "指示灯",
        "properties":  ["src", "interval", "half", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 40, "h": 40, "interval": 500},
        "template":    "FlashLED",
    },

    {  # ── 其他 ──
        "type":        "Timer",
        "displayName": "定时器",
        "category":    "其他",
        "properties":  ["interval", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100, "interval": 1000},
        "template":    "Timer",
    },
    {
        "type":        "FileDialog",
        "displayName": "文件对话框",
        "category":    "其他",
        "properties":  ["extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "FileDialog",
    },
    {
        "type":        "RunFromHereDialog",
        "displayName": "从行运行对话框",
        "category":    "其他",
        "properties":  ["extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "RunFromHereDialog",
    },
    { 
        "type":        "HalInputMonitor",
        "displayName": "HAL引脚监视器",
        "category":    "其他",
        "properties":  ["pinName", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 30, "pinName": ""},
        "template":    "HalInputMonitor",
    },        
]
