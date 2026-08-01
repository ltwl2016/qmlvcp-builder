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
#  用法: from builder.templates.controls import CONTROLS
# ────────────────────────────────────────────────────────────────

CONTROLS = [
    {  # ── 基础控件 ──
        "type":       "Image",
        "category":   "基础控件",
        "properties": ["source", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":   "Image",
    },
    {
        "type":       "Rectangle",
        "category":   "基础控件",
        "properties": ["bgColor", "border", "borderW", "borderC", "container", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100, "bgColor": "#333333", "border": False, "borderW": 1, "borderC": "#ffffff"},
        "template":   "Rectangle",
    },
    {
        "type":       "Text (Label)",
        "category":   "基础控件",
        "properties": ["text", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 200, "h": 40, "text": "Label"},
        "template":   "Text (Label)",
    },
    {
        "type":       "TextField",
        "category":   "基础控件",
        "properties": ["placeholder", "text", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 200, "h": 50},
        "template":   "TextField",
    },

    {  # ── 交互控件 ──
        "type":       "ImageButton",
        "category":   "交互控件",
        "properties": ["source", "action", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":   "ImageButton",
    },
    {
        "type":       "SpriteButton",
        "category":   "交互控件",
        "properties": ["source", "action", "half", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":   "SpriteButton",
    },
    {
        "type":       "JOGButton",
        "category":   "交互控件",
        "properties": ["source", "action_press", "action_release", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":   "JOGButton",
    },
    {
        "type":       "EmergencyStop",
        "category":   "交互控件",
        "properties": ["half", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":   "EmergencyStop",
    },

    {  # ── CNC 控件 ──
        "type":       "GCodeGraphics",
        "category":   "CNC 控件",
        "properties": ["showWorkAxes", "isOrthographic", "cameraZoom", "allowSelection", "activeLine", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 400, "h": 300},
        "template":   "GCodeGraphics",
    },
    {
        "type":       "GCodeViewer",
        "category":   "CNC 控件",
        "properties": ["allowSelection", "activeLine", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 400, "h": 300},
        "template":   "GCodeViewer",
    },
    {
        "type":       "MachTextInput",
        "category":   "CNC 控件",
        "properties": ["pinName", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 200, "h": 50},
        "template":   "MachTextInput",
    },
    {
        "type":       "RunFromHereDialog",
        "category":   "CNC 控件",
        "properties": ["extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":   "RunFromHereDialog",
    },
    {
        "type":       "Text (DRO)",
        "category":   "CNC 控件",
        "properties": ["axis", "decimals", "unit", "value", "text", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 200, "h": 40, "axis": "x"},
        "template":   "Text (DRO)",
    },

    {  # ── HAL 控件 ──
        "type":       "LED",
        "category":   "HAL 控件",
        "properties": ["pinName", "half", "defaultColor", "activeColor", "inactiveColor", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 40, "h": 40},
        "template":   "LED",
    },
    {
        "type":       "FlashLED",
        "category":   "HAL 控件",
        "properties": ["src", "interval", "half", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 40, "h": 40, "interval": 500},
        "template":   "FlashLED",
    },

    {  # ── 其他 ──
        "type":       "Timer",
        "category":   "其他",
        "properties": ["interval", "extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100, "interval": 1000},
        "template":   "Timer",
    },
    {
        "type":       "FileDialog",
        "category":   "其他",
        "properties": ["extraQml"],
        "defaults":   {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":   "FileDialog",
    },
]
