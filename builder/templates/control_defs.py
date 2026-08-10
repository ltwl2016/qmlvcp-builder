from lang import Tr
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
        "category":    Tr.t("control_defs.s3_31dec3", "Basic controls"),
        "properties":  ["source", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "Image",
    },
    {
        "type":        "Rectangle",
        "displayName": "Rectangle",
        "category":    Tr.t("control_defs.s3_31dec3", "Basic controls"),
        "properties":  ["bgColor", "border", "borderW", "borderC", "container", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100, "bgColor": "#333333", "border": False, "borderW": 1, "borderC": "#ffffff"},
        "template":    "Rectangle",
    },
    {
        "type":        "Text (Label)",
        "displayName": "Text (Label)",
        "category":    Tr.t("control_defs.s3_31dec3", "Basic controls"),
        "properties":  ["text", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 40, "text": "Label"},
        "template":    "Text (Label)",
    },

    {  # ── 按钮 ──
        "type":        "ImageButton",
        "displayName": Tr.t("control_defs.s4_a94bc7", "Image button"),
        "category":    Tr.t("control_defs.s9_fa9663", "Button"),
        "properties":  ["source", "action", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "ImageButton",
    },
    {
        "type":        "SpriteButton",
        "displayName": Tr.t("control_defs.s6_7c6ac7", "Sprite button"),
        "category":    Tr.t("control_defs.s9_fa9663", "Button"),
        "properties":  ["source", "action", "half", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "SpriteButton",
    },
    {
        "type":        "JOGButton",
        "displayName": Tr.t("control_defs.s8_a3ce31", "JOG control button"),
        "category":    Tr.t("control_defs.s9_fa9663", "Button"),
        "properties":  ["source", "action_press", "action_release", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "JOGButton",
    },
    {
        "type":        "ToggleButton",
        "displayName": Tr.t("control_defs.s35_toggle", "Toggle button"),
        "category":    Tr.t("control_defs.s9_fa9663", "Button"),
        "properties":  ["source", "bind", "action_press", "action_release", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "ToggleButton",
    },    
    {
        "type":        "EmergencyStop",
        "displayName": Tr.t("control_defs.s10_b3f365", "E-Stop button"),
        "category":    Tr.t("control_defs.s9_fa9663", "Button"),
        "properties":  ["half", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "EmergencyStop",
    },

    {  # ── 显示控件 ──
        "type":        "GCodeGraphics",
        "displayName": Tr.t("control_defs.s12_eba989", "GCode 3D viewer"),
        "category":    Tr.t("control_defs.s17_4a7487", "Display"),
        "properties":  ["showWorkAxes", "isOrthographic", "cameraZoom", "allowSelection", "activeLine", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 400, "h": 300},
        "template":    "GCodeGraphics",
    },
    {
        "type":        "GCodeViewer",
        "displayName": Tr.t("control_defs.s14_9c208c", "GCode text viewer"),
        "category":    Tr.t("control_defs.s17_4a7487", "Display"),
        "properties":  ["allowSelection", "activeLine", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 400, "h": 300},
        "template":    "GCodeViewer",
    },
    {
        "type":        "Text (DRO)",
        "displayName": Tr.t("control_defs.s16_773083", "Digital readout (DRO)"),
        "category":    Tr.t("control_defs.s17_4a7487", "Display"),
        "properties":  ["axis", "decimals", "unit", "value", "text", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 40, "axis": "x"},
        "template":    "Text (DRO)",
    },            
    { # ── 输入框 ──
        "type":        "MachTextInput",
        "displayName": Tr.t("control_defs.s18_2339e0", "Number spinner"),
        "category":    Tr.t("control_defs.s21_9b6425", "Input"),
        "properties":  ["pinName", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 50},
        "template":    "MachTextInput",
    },
    {
        "type":        "TextField",
        "displayName": Tr.t("control_defs.s20_ee90e7", "MDI input"),
        "category":    Tr.t("control_defs.s21_9b6425", "Input"),
        "properties":  ["placeholder", "text", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 200, "h": 50},
        "template":    "TextField",
    },    

    {  # ── 指示灯 ──
        "type":        "LED",
        "displayName": Tr.t("control_defs.s22_280853", "Basic LED"),
        "category":    Tr.t("control_defs.s25_267d46", "Indicator"),
        "properties":  ["pinName", "half", "defaultColor", "activeColor", "inactiveColor", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 40, "h": 40},
        "template":    "LED",
    },
    {
        "type":        "FlashLED",
        "displayName": Tr.t("control_defs.s24_9e425e", "Flashing LED"),
        "category":    Tr.t("control_defs.s25_267d46", "Indicator"),
        "properties":  ["src", "interval", "half", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 40, "h": 40, "interval": 500},
        "template":    "FlashLED",
    },

    {  # ── 其他 ──
        "type":        "Timer",
        "displayName": Tr.t("control_defs.s26_fec3d6", "Timer"),
        "category":    Tr.t("control_defs.s33_0d98c7", "Other"),
        "properties":  ["interval", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100, "interval": 1000},
        "template":    "Timer",
    },
    {
        "type":        "FileDialog",
        "displayName": Tr.t("control_defs.s28_7ecc3d", "File dialog"),
        "category":    Tr.t("control_defs.s33_0d98c7", "Other"),
        "properties":  ["extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "FileDialog",
    },
    {
        "type":        "RunFromHereDialog",
        "displayName": Tr.t("control_defs.s30_e79630", "Run-from-line dialog"),
        "category":    Tr.t("control_defs.s33_0d98c7", "Other"),
        "properties":  ["extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 100},
        "template":    "RunFromHereDialog",
    },
    { 
        "type":        "HalInputMonitor",
        "displayName": Tr.t("control_defs.s32_4c7053", "HAL pin monitor"),
        "category":    Tr.t("control_defs.s33_0d98c7", "Other"),
        "properties":  ["pinName", "extraQml"],
        "defaults":    {"x": 0, "y": 0, "w": 100, "h": 30, "pinName": ""},
        "template":    "HalInputMonitor",
    },        
]
