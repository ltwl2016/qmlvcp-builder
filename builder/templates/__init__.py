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

# ───────────────────────────────────────────────────
#  控件 QML 模板汇总 — 每个控件一个 .qml 文件
#  用法: from builder.templates import get_template
# ───────────────────────────────────────────────────
import os

_TEMPLATE_DIR = os.path.dirname(__file__)

_FILE_MAP = {
    "HalInputMonitor":     "HalInputMonitor.qml",
    "ImageButton":          "ImageButton.qml",
    "JOGButton":            "JOGButton.qml",
    "SpriteButton":         "SpriteButton.qml",
    "LED":                  "LED.qml",
    "FlashLED":             "FlashLED.qml",
    "MachTextInput":        "MachTextInput.qml",
    "GCodeGraphics":        "GCodeGraphics.qml",
    "GCodeViewer":          "GCodeViewer.qml",
    "RunFromHereDialog":    "RunFromHereDialog.qml",
    "Text (DRO)":           "Text_DRO.qml",
    "Text (Label)":         "Text_Label.qml",
    "Image":                "Image.qml",
    "TextField":            "TextField.qml",
    "Timer":                "Timer.qml",
    "Rectangle":            "Rectangle.qml",
    "FileDialog":           "FileDialog.qml",
    "EmergencyStop":        "EmergencyStop.qml",
}

_CACHE: dict = {}
_INDENT = "            "  # 12 spaces, 与原始模板一致


def get_template(ctype: str) -> str:
    """读 .qml 模板文件，加回 12 空格缩进。"""
    if ctype not in _CACHE:
        fname = _FILE_MAP.get(ctype)
        if fname is None:
            return ""
        path = os.path.join(_TEMPLATE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        # 每行加 12 空格缩进
        lines = raw.strip("\n").split("\n")
        tmpl = "\n".join(_INDENT + ln if ln else "" for ln in lines) + "\n"
        _CACHE[ctype] = tmpl
    return _CACHE[ctype]

from .control_defs import CONTROLS
