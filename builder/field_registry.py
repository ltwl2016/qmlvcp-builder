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

"""
属性注册表 — 从 controls.py 导入唯一真源。
新增属性只需改 controls.py 的 FIELD_KINDS 模板定义。
"""

from builder.controls import FIELD_KINDS, get_properties, PROP_BINDABLE as _PROP_BINDABLE
import re


def parse_template(template: str) -> list:
    """从模板字符串提取所有 $xxx 变量名，返回按出现顺序的去重列表。"""
    vars_found = re.findall(r'\$(\w+)', template)
    seen = set()
    result = []
    for v in vars_found:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result


def get_field_info(name: str) -> dict:
    """返回属性的完整信息 (label, kind, default, tooltip, options)。"""
    if name not in FIELD_KINDS:
        return {"label": name, "kind": "text", "default": "", "tooltip": "", "options": {}}
    label, kind, default, tooltip, options = FIELD_KINDS[name]
    return {"label": label, "kind": kind, "default": default,
            "tooltip": tooltip, "options": options}


def is_bindable(name: str) -> bool:
    """判断属性是否支持绑定表达式。"""
    return FIELD_KINDS.get(name, ("", "", "", "", {}))[1] == "expression"


# ═══ Widget 工厂 ═══
def _widget_factories():
    """延迟导入 PyQt5，返回 widget 构建函数。"""
    from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
        QCheckBox, QSpinBox, QDoubleSpinBox, QPushButton, QComboBox,
        QPlainTextEdit, QFileDialog, QColorDialog)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor

    class PathWidget(QWidget):
        """路径选择：文本框 + 浏览按钮。"""
        def __init__(self, optional=False):
            super().__init__()
            self.optional = optional
            lay = QHBoxLayout(self)
            lay.setContentsMargins(0, 0, 0, 0)
            self.edit = QLineEdit()
            self.edit.setReadOnly(True)
            lay.addWidget(self.edit)
            self.btn = QPushButton("...")
            self.btn.setFixedWidth(30)
            self.btn.clicked.connect(self._browse)
            lay.addWidget(self.btn)
        def _browse(self):
            f, _ = QFileDialog.getOpenFileName(self, "选择文件", "",
                "Images (*.png *.jpg *.bmp *.gif *.svg)")
            if f: self.edit.setText(f)
        def text(self): return self.edit.text()
        def setText(self, v): self.edit.setText(v)
        def blockSignals(self, b): self.edit.blockSignals(b)
        def valueChanged(self): pass  # no-op, 信号在 edit.textChanged

    class ExtraQmlWidget(QWidget):
        """手写备用属性：折叠按钮 + 多行文本框（默认隐藏）。"""
        textChanged = None  # will be set after creation
        def __init__(self):
            super().__init__()
            self._collapsed = True
            lay = QVBoxLayout(self)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(2)
            self.btn = QPushButton("▶ 手写备用属性")
            self.btn.clicked.connect(self._toggle)
            lay.addWidget(self.btn)
            self.edit = QPlainTextEdit()
            self.edit.setPlaceholderText("在此输入自定义 QML 属性...")
            self.edit.setMaximumHeight(100)
            self.edit.setVisible(False)
            lay.addWidget(self.edit)
        def _toggle(self):
            self._collapsed = not self._collapsed
            self.edit.setVisible(not self._collapsed)
            self.btn.setText("▼ 手写备用属性" if not self._collapsed else "▶ 手写备用属性")
        def text(self): return self.edit.toPlainText()
        def setText(self, v): self.edit.setPlainText(v if v else "")
        def blockSignals(self, b): self.edit.blockSignals(b)
        def valueChanged(self): pass  # signal wired separately

    class ColorWidget(QPushButton):
        """颜色选择按钮。"""
        def __init__(self):
            super().__init__()
            self.setFixedWidth(50)
            self._color = "#000000"
            self.clicked.connect(self._pick)
        def _pick(self):
            c = QColorDialog.getColor(QColor(self._color), self, "选择颜色")
            if c.isValid():
                self._color = c.name()
                self.setStyleSheet(f"background:{self._color};")
        def text(self): return self._color
        def setText(self, v):
            self._color = v
            if QColor.isValidColor(v):
                self.setStyleSheet(f"background:{v};")
            else:
                self.setStyleSheet("")
        def valueChanged(self): pass

    def _setup_search(combo):
        from PyQt5.QtWidgets import QCompleter
        c = QCompleter(combo.model(), combo)
        c.setCaseSensitivity(Qt.CaseInsensitive)
        c.setFilterMode(Qt.MatchContains)
        combo.setCompleter(c)

    def make(info: dict):
        """根据 info 创建编辑控件。"""
        kind = info["kind"]
        opts = info.get("options", {})
        rng = opts.get("range", (-9999, 99999))

        if kind == "path":
            w = PathWidget(optional=opts.get("optional", False))
            return w
        elif kind == "jog_action_combo":
            w = QComboBox()
            w.setEditable(True)
            w.addItems(["", "--- JOG ---",
                "JOG_X+", "JOG_X-", "JOG_Y+", "JOG_Y-",
                "JOG_Z+", "JOG_Z-", "JOG_A+", "JOG_A-",
                "JOG_B+", "JOG_B-", "JOG_C+", "JOG_C-",
                "JOG_X_STOP", "JOG_Y_STOP", "JOG_Z_STOP", "JOG_A_STOP",
                "JOG_SPEED_UP", "JOG_SPEED_DOWN",
                "JOG_MODE_CONTINUOUS", "JOG_MODE_STEP", "JOG_MODE_MPG",
                "JOG_SET_STEP_0", "JOG_SET_STEP_1", "JOG_SET_STEP_2", "JOG_SET_STEP_3"])
            _setup_search(w)
            return w
        elif kind == "action_combo":
            w = QComboBox()
            w.setEditable(True)
            w.addItems(["","cmd.homeAll","cmd.modeManual","cmd.modeAuto",
                        "cmd.spindleOn","cmd.spindleOff","cmd.emergencyStop",
                        "cmd.toolTable","cmd.programRun","cmd.programPause",
                        "cmd.programStop","cmd.programResume",
                        "command.programSetLine(lineIndex)","command.mdiExecute",
                        "command.floodOn","command.floodOff","command.mistOn","command.mistOff"])
            _setup_search(w)
            return w
        elif kind == "bind_combo":
            w = QComboBox()
            w.setEditable(True)
            w.addItems(["",
                "backend.displayToolX","backend.displayToolY","backend.displayToolZ",
                "backend.displayToolA","backend.displayToolB","backend.displayToolC",
                "st.spindleSpeed","st.spindleOverride","st.feedrate","st.feedOverride",
                "st.isAllHomed","st.isHomedX","st.isHomedY","st.isHomedZ",
                "st.isSpindleOn","st.isSpindleCW","st.machineState",
                "st.currentTool","st.pocketNumber","st.isProgramRunning",
                "st.isOnLimitX","st.isOnLimitY","st.isOnLimitZ",
                "backlog.gcodeLines","backlog.programLines"])
            _setup_search(w)
            return w
        elif kind == "bool":
            return QCheckBox()
        elif kind == "bool_expr":
            w = QComboBox()
            w.setEditable(True)
            w.addItems(["true", "false"])
            _setup_search(w)
            return w
        elif kind == "int":
            w = QSpinBox()
            w.setRange(rng[0], rng[1])
            return w
        elif kind == "float":
            w = QDoubleSpinBox()
            w.setDecimals(2)
            w.setRange(rng[0], rng[1])
            return w
        elif kind == "color":
            w = QLineEdit()
            w.setPlaceholderText("#1e1e1e")
            return w
        elif kind == "text":
            w = QLineEdit()
            return w
        elif kind == "expression":
            w = QLineEdit()
            w.setPlaceholderText(opts.get("placeholder", ""))
            return w
        elif kind == "extra_qml":
            w = ExtraQmlWidget()
            w.textChanged = w.edit.textChanged
            return w
        elif kind == "half":
            w = QComboBox()
            w.addItems(["none","left","right","top","bottom"])
            return w
        else:
            w = QLineEdit()
            return w
    return make
