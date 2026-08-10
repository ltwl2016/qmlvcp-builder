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

"""PropertiesMixin - 属性表单构建 & 读写逻辑."""
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QCheckBox, QFileDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
    QPushButton,
)
from PyQt5.QtGui import QPixmap

from builder.preview_canvas import _setup_combo_search


class PropertiesMixin:
    """Mixin providing property form build / read / write methods for MainWindow."""

    def _build_field_widgets(self) -> dict:

        """数据驱动：从 FIELD_KINDS 自动生成所有标准属性编辑控件。

        排除手动创建的特殊控件（x/y/w/h/z/type/id/action/bind/src/pressedSource/half）。

        返回 { field_name: widget } 字典。"""

        from builder.field_registry import _widget_factories

        from builder.controls import FIELD_KINDS as FK

        make = _widget_factories()

        widgets = {}

        manual = {"x", "y", "w", "h", "type", "id",

                  "src", "pressedSource", "action", "bind", "half",

                  "spriteFrame",

                  "bg", "label", "machineName", "maxVelocity", "primaryColor"}



        for name, (label, kind, default, tooltip, opts) in FK.items():

            if name in manual:

                continue

            info = {"label": label, "kind": kind, "default": default,

                    "tooltip": tooltip, "options": opts}

            w = make(info)

            w.setToolTip(tooltip)



            # 连接信号

            if kind == "path":

                w.edit.textChanged.connect(self._on_prop_changed)

            elif kind in ("action_combo", "bind_combo", "jog_action_combo"):

                w.currentTextChanged.connect(self._on_prop_changed)

                _setup_combo_search(w)

            elif kind == "bool":

                w.clicked.connect(self._on_prop_changed)

            elif kind == "bool_expr":

                w.currentTextChanged.connect(self._on_prop_changed)

            elif kind in ("int", "float"):

                w.valueChanged.connect(self._on_prop_changed)

            elif kind == "extra_qml":

                w.textChanged.connect(self._on_prop_changed)

            else:  # text, expression, color

                w.textChanged.connect(self._on_prop_changed)



            self._props_form.addRow(label + ":", w)

            widgets[name] = w



        return widgets




    def _build_property_form(self):

        """在 propScrollContent 中构建属性编辑表单 (动态)。"""

        from builder.controls import get_all_actions, get_all_binds

        container = self.propScrollContent

        if container.layout() is None:

            container.setLayout(QVBoxLayout())

        else:

            ly = container.layout()

            while ly.count():

                item = ly.takeAt(0)

                if item.widget():

                    item.widget().deleteLater()



        self._props_form = QFormLayout()

        container.layout().addLayout(self._props_form)



        # 类型选择

        self._prop_type = QComboBox()

        self._prop_type.addItem("(window)")

        from builder.controls import CONTROLS as _CTRLS

        self._prop_type.addItems([c["type"] for c in _CTRLS])

        self._prop_type.currentTextChanged.connect(self._on_prop_type_changed)

        self._props_form.addRow(Tr.t("_prop_type.s2_436358", "Type:"), self._prop_type)



        # ID

        self._prop_id = QLineEdit()

        self._prop_id.setPlaceholderText(Tr.t("_prop_id.s3_2f2da9", "QML identifier (optional)"))

        self._prop_id.textChanged.connect(self._on_prop_changed)

        self._props_form.addRow("ID:", self._prop_id)



        # X

        self._prop_x = QSpinBox()

        self._prop_x.setRange(0, 4000)

        self._prop_x.valueChanged.connect(self._on_prop_changed)

        self._props_form.addRow("X:", self._prop_x)



        # Y

        self._prop_y = QSpinBox()

        self._prop_y.setRange(0, 4000)

        self._prop_y.valueChanged.connect(self._on_prop_changed)

        self._props_form.addRow("Y:", self._prop_y)



        # 宽

        self._prop_w = QSpinBox()

        self._prop_w.setRange(10, 4000)

        self._prop_w.valueChanged.connect(self._on_prop_changed)

        w_row = QHBoxLayout()

        w_row.addWidget(self._prop_w)

        self._chk_left_w = QCheckBox("左")

        self._chk_left_w.clicked.connect(self._on_half_w_changed)

        w_row.addWidget(self._chk_left_w)

        self._chk_right_w = QCheckBox("右")

        self._chk_right_w.toggled.connect(self._on_half_w_changed)

        w_row.addWidget(self._chk_right_w)

        self._props_form.addRow(Tr.t("_chk_right_w.s6_2589e7", "Width:"), w_row)



        # 高

        self._prop_h = QSpinBox()

        self._prop_h.setRange(10, 4000)

        self._prop_h.valueChanged.connect(self._on_prop_changed)

        h_row = QHBoxLayout()

        h_row.addWidget(self._prop_h)

        self._chk_top_h = QCheckBox("上")

        self._chk_top_h.toggled.connect(self._on_half_h_changed)

        h_row.addWidget(self._chk_top_h)

        self._chk_bottom_h = QCheckBox("下")

        self._chk_bottom_h.toggled.connect(self._on_half_h_changed)

        h_row.addWidget(self._chk_bottom_h)

        self._props_form.addRow(Tr.t("_chk_bottom_h.s9_8084a2", "Height:"), h_row)



        # 贴图

        self._prop_src = QLineEdit()

        self._prop_src.setPlaceholderText("assets/my_btn.png")

        self._prop_src.textChanged.connect(self._on_prop_changed)

        src_row = QHBoxLayout()

        src_row.addWidget(self._prop_src)

        self._btn_browse_src = QPushButton("...")

        self._btn_browse_src.setFixedWidth(30)

        self._btn_browse_src.clicked.connect(self._browse_src)

        src_row.addWidget(self._btn_browse_src)

        self._props_form.addRow(Tr.t("_btn_browse_src.s10_cd9887", "Image:"), src_row)



        # 动作

        self._prop_action = QComboBox()

        self._prop_action.setEditable(True)

        self._prop_action.setInsertPolicy(QComboBox.NoInsert)

        self._prop_action.addItems([""] + list(get_all_actions()))

        self._prop_action.currentTextChanged.connect(self._on_prop_changed)

        _setup_combo_search(self._prop_action)

        self._props_form.addRow(Tr.t("_prop_action.s11_3cf4dc", "Action:"), self._prop_action)

        self._prop_action.setToolTip(Tr.t("_prop_action.s12_7b14d2", "Filter: home, jog, spindle…"))



        # 绑定

        self._prop_bind = QComboBox()

        self._prop_bind.setEditable(True)

        self._prop_bind.setInsertPolicy(QComboBox.NoInsert)

        self._prop_bind.addItems([""] + list(get_all_binds()))

        self._prop_bind.currentTextChanged.connect(self._on_prop_changed)

        _setup_combo_search(self._prop_bind)

        self._props_form.addRow(Tr.t("_prop_bind.s13_df01b3", "Bind:"), self._prop_bind)

        self._prop_bind.setToolTip(Tr.t("_prop_bind.s14_5cf817", "Filter: spindle, mode, homed…"))



        # ── 数据驱动：工厂循环生成标准属性控件 ──

        self._field_widgets = self._build_field_widgets()

        # 向后兼容别名

        self._prop_text = self._field_widgets["text"]

        self._prop_font_size = self._field_widgets["fontSize"]

        self._prop_bg_color = self._field_widgets["bgColor"]

        self._prop_opacity = self._field_widgets["opacity"]

        self._chk_border = self._field_widgets["border"]

        self._prop_border_w = self._field_widgets["borderW"]

        self._prop_border_color = self._field_widgets["borderC"]

        self._prop_border_thickness = self._field_widgets["borderThickness"]

        self._prop_shrink_amount = self._field_widgets["shrinkAmount"]

        self._chk_container = self._field_widgets["container"]

        self._prop_z = self._field_widgets["z"]

        self._prop_decimals = self._field_widgets["decimals"]

        self._prop_active_line = self._field_widgets["activeLine"]

        self._chk_enabled = self._field_widgets["enabled"]

        self._chk_allow_sel = self._field_widgets["allowSelection"]

        self._chk_is_horizontal = self._field_widgets["isHorizontal"]

        self._chk_active = self._field_widgets["active"]

        self._chk_is_toggle = self._field_widgets["isToggle"]

        self._prop_value = self._field_widgets["value"]

        self._prop_from = self._field_widgets["from"]

        self._prop_to = self._field_widgets["to"]

        self._prop_unit = self._field_widgets["unit"]

        self._prop_pin = self._field_widgets["pinName"]

        self._prop_accent_color = self._field_widgets["accentColor"]

        self._prop_text_color = self._field_widgets["textColor"]

        self._prop_active_color = self._field_widgets["activeColor"]

        self._prop_inactive_color = self._field_widgets["inactiveColor"]

        self._prop_default_color = self._field_widgets["defaultColor"]

        self._prop_pressed_color = self._field_widgets["pressedColor"]

        self._prop_action_press = self._field_widgets["action_press"]

        self._prop_action_release = self._field_widgets["action_release"]

        self._prop_source_clip = self._field_widgets["sourceClipRect"]

        self._prop_interval = self._field_widgets["interval"]

        self._chk_repeat = self._field_widgets["repeat"]

        self._chk_running = self._field_widgets["running"]

        self._chk_show_work_axes = self._field_widgets["showWorkAxes"]

        self._chk_is_ortho = self._field_widgets["isOrthographic"]

        self._prop_camera_z = self._field_widgets["cameraZoom"]



        # ── 手动特殊控件 ──

        # 备用贴图 pressedSource

        self._prop_pressed_src = QLineEdit()

        self._prop_pressed_src.setPlaceholderText(Tr.t("_prop_pressed_src.s15_3f9046", "Pressed-state image (optional)"))

        self._prop_pressed_src.textChanged.connect(self._on_prop_changed)

        psrc_row = QHBoxLayout()

        psrc_row.addWidget(self._prop_pressed_src)

        self._btn_browse_psrc = QPushButton("...")

        self._btn_browse_psrc.setFixedWidth(30)

        self._btn_browse_psrc.clicked.connect(self._browse_pressed_src)

        psrc_row.addWidget(self._btn_browse_psrc)

        self._props_form.addRow(Tr.t("_btn_browse_psrc.s16_dc4685", "Alt image:"), psrc_row)



        # 绑定表达式

        self._prop_active_line_bind = QLineEdit()

        self._prop_active_line_bind.setPlaceholderText(Tr.t("_prop_active_line_bind.s17_c198bc", "e.g. status.lineNumber"))

        self._prop_active_line_bind.textChanged.connect(self._on_prop_changed)

        self._props_form.addRow("  ↳ 绑定:", self._prop_active_line_bind)



        self._prop_allow_sel_bind = QLineEdit()

        self._prop_allow_sel_bind.setPlaceholderText(Tr.t("_prop_allow_sel_bind.s19_01eb43", "e.g. backend.isIdle"))

        self._prop_allow_sel_bind.textChanged.connect(self._on_prop_changed)

        self._props_form.addRow("  ↳ 绑定:", self._prop_allow_sel_bind)



        self._prop_active_bind = QLineEdit()

        self._prop_active_bind.setPlaceholderText(Tr.t("_prop_active_bind.s21_c72839", "e.g. status.isAllHomed"))

        self._prop_active_bind.textChanged.connect(self._on_prop_changed)

        self._props_form.addRow("  ↳ 绑定:", self._prop_active_bind)



        self._prop_value_bind = QLineEdit()

        self._prop_value_bind.setPlaceholderText(Tr.t("_prop_value_bind.s23_de0d25", "e.g. status.spindleSpeed"))

        self._prop_value_bind.textChanged.connect(self._on_prop_changed)

        self._props_form.addRow("  ↳ 绑定:", self._prop_value_bind)



        self._prop_source_clip_bind = QLineEdit()

        self._prop_source_clip_bind.setPlaceholderText(Tr.t("_prop_source_clip_bind.s25_232aa0", "e.g. backend.isMachineCoordActive ? Qt.rect(118,0,118,15) : Qt.rect(0,0,118,15)"))

        self._prop_source_clip_bind.textChanged.connect(self._on_prop_changed)

        self._props_form.addRow("  ↳ 绑定:", self._prop_source_clip_bind)



        # 精灵帧 spriteFrame

        self._prop_sprite_frame = QLineEdit()

        self._prop_sprite_frame.setPlaceholderText(Tr.t("controls.s105_d516f4", "e.g. status.homedX ? 0 : 1"))

        self._prop_sprite_frame.textChanged.connect(self._on_prop_changed)

        sframe_row = QHBoxLayout()

        sframe_row.addWidget(self._prop_sprite_frame)

        self._btn_gen_sprite = QPushButton("⟳")

        self._btn_gen_sprite.setFixedWidth(32)

        self._btn_gen_sprite.setToolTip(Tr.t("_btn_gen_sprite.s28_fab7bf", "Generate expression from current half and bind values"))

        self._btn_gen_sprite.clicked.connect(self._gen_sprite_frame_expr)

        sframe_row.addWidget(self._btn_gen_sprite)

        self._props_form.addRow(Tr.t("_btn_gen_sprite.s29_514f17", "Sprite frame:"), sframe_row)

        self._prop_sprite_frame_bind = QLineEdit()

        self._prop_sprite_frame_bind.setPlaceholderText(Tr.t("_prop_sprite_frame_bind.s30_35a9da", "Expression takes priority (e.g. status.homedX ? 1 : 0)"))

        self._prop_sprite_frame_bind.textChanged.connect(self._on_prop_changed)

        self._props_form.addRow("  ↳ 绑定:", self._prop_sprite_frame_bind)



        # 建立 field_widget → label_widget 映射

        self._field_to_label = {}

        for i in range(self._props_form.rowCount()):

            fi = self._props_form.itemAt(i, QFormLayout.FieldRole)

            li = self._props_form.itemAt(i, QFormLayout.LabelRole)

            if not (fi and li):

                continue

            lw = li.widget()

            if not lw:

                continue

            fw = fi.widget()

            if not fw and fi.layout():

                for j in range(fi.layout().count()):

                    child = fi.layout().itemAt(j)

                    if child and child.widget():

                        fw = child.widget()

                        break

            if fw:

                self._field_to_label[fw] = lw



        # 合并手动 + 工厂 widget，统一入口

        self._prop_widgets = dict(self._field_widgets)

        manual_widgets = {

            "id":              self._prop_id,

            "src":             self._prop_src,

            "action":          self._prop_action,

            "bind":            self._prop_bind,

            "half":            self._chk_left_w,

            "pressedSource":   self._prop_pressed_src,

            "spriteFrame":     self._prop_sprite_frame,

            "spriteFrameBind": self._prop_sprite_frame_bind,

            "sourceClipRectBind": self._prop_source_clip_bind,

            "activeLineBind":    self._prop_active_line_bind,

            "allowSelectionBind":self._prop_allow_sel_bind,

            "activeBind":        self._prop_active_bind,

            "valueBind":         self._prop_value_bind,

        }

        self._prop_widgets.update(manual_widgets)



        # 初始隐藏全部属性行

        for key in self._prop_widgets:

            w = self._prop_widgets[key]

            w.setVisible(False)

            lbl = self._field_to_label.get(w)

            if lbl:

                lbl.setVisible(False)



        # 属性 tooltip

        from builder.controls import PROP_TOOLTIPS

        for key, tip in PROP_TOOLTIPS.items():

            w = self._prop_widgets.get(key)

            if w:

                w.setToolTip(tip)

                lbl = self._field_to_label.get(w)

                if lbl:

                    lbl.setToolTip(tip)



        container.layout().addStretch()



    # ═══════════════════════════════════════════

    #  ③ 项目导出标签页

    # ═══════════════════════════════════════════




    def _pick_image_for_control(self):

        path, _ = QFileDialog.getOpenFileName(

            self, Tr.t("_pick_image_for_control.s32_0994e6", "Select control image"), "",

            "Images (*.png *.jpg *.jpeg)"

        )

        if path and self._canvas._sel_index >= 0:

            c = self._active_controls[self._canvas._sel_index]

            c["src"] = path

            # 取图片尺寸

            pm = QPixmap(path)

            if not pm.isNull():

                c["w"] = pm.width()

                c["h"] = pm.height()

            self._refresh_canvas()

            self._refresh_props(self._canvas._sel_index)




    def _on_half_w_changed(self, checked):

        """左/右半宽互斥（仅视觉裁切，不影响 w/h）。"""

        s = self.sender()

        if checked:

            if s is self._chk_left_w:

                self._chk_right_w.setChecked(False)

            else:

                self._chk_left_w.setChecked(False)

        self._on_prop_changed()




    def _on_half_h_changed(self, checked):

        """上/下半高互斥。"""

        s = self.sender()

        if checked:

            if s is self._chk_top_h:

                self._chk_bottom_h.setChecked(False)

            else:

                self._chk_top_h.setChecked(False)

        self._on_prop_changed()




    def _on_prop_changed(self):

        """数据驱动：属性面板控件值变化时，写回当前选中控件。"""

        if self._props_refreshing:

            return

        idx = self._canvas._sel_index

        if idx < 0:

            self._on_zone_prop_changed()

            return

        controls = self._active_controls

        if idx >= len(controls):

            return

        ctrl = controls[idx]



        if self._undo_needs_push:

            self._push_undo_snapshot()



        # 类型变更

        new_type = self._prop_type.currentText()

        if ctrl.get("type") != new_type and new_type != "(window)":

            ctrl["type"] = new_type

            from builder.controls import CONTROLS

            for cc in CONTROLS:

                if cc["type"] == new_type:

                    defaults = cc.get("defaults", {})

                    for k, v in defaults.items():

                        ctrl.setdefault(k, v)

                    break

            self._canvas.update()

            self._refresh_props(idx)

            return



        # 用 _read_prop_fields 读取并写入

        self._read_prop_fields(ctrl)



        # half 复选框 → 控件数据（仅视觉裁切，不参与属性管道）

        if self._chk_left_w.isChecked(): ctrl["half_w_dir"] = "left"

        elif self._chk_right_w.isChecked(): ctrl["half_w_dir"] = "right"

        else: ctrl.pop("half_w_dir", None)

        if self._chk_top_h.isChecked(): ctrl["half_h_dir"] = "top"

        elif self._chk_bottom_h.isChecked(): ctrl["half_h_dir"] = "bottom"

        else: ctrl.pop("half_h_dir", None)



        # 贴图导入一次性适配：仅当 src 变化时自动设 w/h

        if not hasattr(self, '_ctrl_src_cache'):

            self._ctrl_src_cache = {}

        ctrl_id = ctrl.get("id", str(id(ctrl)))

        new_src = ctrl.get("src", "")

        if new_src and new_src != self._ctrl_src_cache.get(ctrl_id):

            if os.path.exists(new_src):

                from PyQt5.QtGui import QPixmap

                pm = QPixmap(new_src)

                if not pm.isNull():

                    ctrl["w"] = pm.width()

                    ctrl["h"] = pm.height()

                    self._canvas._pixmap_cache[new_src] = pm

                    self._props_refreshing = True

                    self._write_prop_fields(ctrl)

                    self._props_refreshing = False

            self._ctrl_src_cache[ctrl_id] = new_src



        self._canvas.update()




    def _on_prop_type_changed(self, ctype: str):

        """控件类型变化 — 更新默认宽高。"""

        from builder.controls import get_defaults

        if ctype == "(window)":

            self._canvas._sel_index = -1

            self._canvas.update()

            self._show_page_props()

            return

        idx = self._canvas._sel_index

        if idx < 0:

            return

        d = get_defaults(ctype)

        if d is None:

            return

        self._prop_w.setValue(d.get("w", 80))

        self._prop_h.setValue(d.get("h", 40))



    _props_refreshing = False  # 刷新属性面板时禁止 _on_prop_changed 写回

    # ── 数据驱动属性面板核心 ──




    def _prop_map(self):

        """数据驱动：从 _field_widgets 直接生成属性→(widget,kind,default)映射。"""

        from builder.controls import FIELD_KINDS as FK

        kind_overrides = {

            "action": ("action_combo", ""), "bind": ("bind_combo", ""),

            "action_press": ("jog_action_combo", ""), "action_release": ("jog_action_combo", ""),

            "src": ("path", ""), "pressedSource": ("path", ""), "half": ("half", "none"),

        }

        result = {}

        for name, (label, kind, default, tooltip, opts) in FK.items():

            w = None

            if name in self._field_widgets:

                w = self._field_widgets[name]

                k = kind_overrides.get(name, (kind, default))[0]

            elif hasattr(self, f"_prop_{name}"):

                w, k = getattr(self, f"_prop_{name}"), kind

            if w is None:

                continue

            if k == "float":

                result[name] = (w, "float", default)

            elif k == "bool":

                result[name] = (w, "bool", default)

            elif k == "bool_expr":

                result[name] = (w, "bool_expr", default)

            elif k == "int":

                result[name] = (w, "spin100" if name == "opacity" else "spin", default)

            elif k in ("action_combo", "bind_combo", "half", "jog_action_combo"):

                result[name] = (w, k, default)

            elif k == "extra_qml":

                result[name] = (w, "extra_qml", default)

            elif k == "path":

                result[name] = (w.edit if hasattr(w, 'edit') else w, "text", default)

            elif k == "color":

                result[name] = (w, "text", default)

            else:

                result[name] = (w, "text", default)

        # 手动控件 (src/action/bind/pressedSource + x/y/w/h/z)

        for name, w in [(k, getattr(self, f"_prop_{k}", None)) for k in ("x","y","w","h","z")]:

            if w:

                result[name] = (w, "spin", 0)

        _manual_attrs = {

            "id": "_prop_id",

            "src": "_prop_src", "action": "_prop_action", "bind": "_prop_bind",

            "pressedSource": "_prop_pressed_src",

            "spriteFrame": "_prop_sprite_frame",

        }

        for name, attr in _manual_attrs.items():

            if hasattr(self, attr):

                result[name] = (getattr(self, attr), kind_overrides.get(name, ("text",""))[0], "")

        return result




    def _repopulate_combo(self, combo, items_dict):
        """以 items_dict 的 key 重新填充一个可编辑下拉框，不触发信号。"""
        values = [""] + list(items_dict)
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(values)
        combo.blockSignals(False)


    def _write_prop_fields(self, ctrl: dict):

        """从 control dict 写入属性面板控件。"""

        from builder.controls import get_actions, get_binds

        ctype = ctrl.get("type", "")
        actions = get_actions(ctype)
        binds = get_binds(ctype)

        # 动态追加当前编辑区所有 HalInputMonitor 的绑定选项（xxx.开关 / xxx.数值）
        for c in self._active_controls:
            if c.get("type") == "HalInputMonitor":
                cid = c.get("id", "").strip()
                if cid:
                    binds[f"{cid}.开关"] = f"{cid}.active"
                    binds[f"{cid}.数值"] = f"{cid}.value"

        # 按控件类型重新填充动作/绑定下拉框
        self._repopulate_combo(self._prop_action, actions)
        self._repopulate_combo(self._prop_bind, binds)

        # 如果 JOGButton 的 action_press / action_release 下拉框也存在，同步过滤
        for fname in ("action_press", "action_release"):
            w = self._field_widgets.get(fname)
            if w and isinstance(w, QComboBox):
                self._repopulate_combo(w, actions)

        for name, (w, kind, default) in self._prop_map().items():

            val = ctrl.get(name, default)

            if kind == "spin":

                w.setValue(int(val) if val is not None else default)

            elif kind == "spin100":

                w.setValue(int(val) if val is not None else default)

            elif kind == "float":

                w.setValue(float(val) if val is not None else default)

            elif kind == "bool":

                w.setChecked(bool(val))

            elif kind == "bool_expr":

                if isinstance(val, bool):

                    w.setCurrentText("true" if val else "false")

                else:

                    w.setCurrentText(str(val))

            elif kind in ("action_combo", "jog_action_combo"):

                # 实际值 → 显示名（backend.jogAxis(0,1) → JOG_X+）

                name_map = {v: k for k, v in actions.items()}

                label = name_map.get(str(val), str(val))

                idx = w.findText(label)

                if idx >= 0: w.setCurrentIndex(idx)

                else: w.setCurrentText(str(val))

            elif kind == "bind_combo":

                name_map = {v: k for k, v in binds.items()}

                label = name_map.get(str(val), str(val))

                idx = w.findText(label)

                if idx >= 0: w.setCurrentIndex(idx)

                else: w.setCurrentText(str(val))

            elif kind == "combo":

                idx = w.findText(str(val))

                if idx >= 0: w.setCurrentIndex(idx)

                else: w.setCurrentText(str(val))

            elif kind == "extra_qml":

                w.setText(str(val) if val else "")

            else:  # text

                w.setText(str(val) if val else "")



        # Half 复选框同步（仅视觉，不在 _prop_map 里）

        hw = ctrl.get("half_w_dir", "")

        if hasattr(self, '_chk_left_w'):

            self._chk_left_w.setChecked(hw == "left")

            self._chk_right_w.setChecked(hw == "right")

        hh = ctrl.get("half_h_dir", "")

        if hasattr(self, '_chk_top_h'):

            self._chk_top_h.setChecked(hh == "top")

            self._chk_bottom_h.setChecked(hh == "bottom")




    def _read_prop_fields(self, ctrl: dict):

        """从属性面板控件读取值，写回 control dict。"""

        from builder.controls import get_actions, get_binds

        ctype = ctrl.get("type", "")
        actions = get_actions(ctype)
        binds = get_binds(ctype)

        # 与 _write_prop_fields 保持一致：动态追加当前编辑区 HalInputMonitor 的绑定选项
        for c in self._active_controls:
            if c.get("type") == "HalInputMonitor":
                cid = c.get("id", "").strip()
                if cid:
                    binds[f"{cid}.开关"] = f"{cid}.active"
                    binds[f"{cid}.数值"] = f"{cid}.value"

        for name, (w, kind, default) in self._prop_map().items():

            try:

                if kind == "spin":

                    ctrl[name] = w.value()

                elif kind == "spin100":

                    ctrl[name] = w.value()

                elif kind == "float":

                    ctrl[name] = w.value()

                elif kind == "bool":

                    ctrl[name] = w.isChecked()

                elif kind == "bool_expr":

                    t = w.currentText()

                    if t in ("true", "false"):

                        ctrl[name] = (t == "true")

                    else:

                        ctrl[name] = t

                elif kind in ("action_combo", "jog_action_combo"):

                    # 下拉显示名 → 实际值（JOG_X+ → backend.jogAxis(0,1)）

                    ctrl[name] = actions.get(w.currentText(), w.currentText())

                elif kind == "bind_combo":

                    ctrl[name] = binds.get(w.currentText(), w.currentText())

                elif kind == "combo":

                    ctrl[name] = w.currentText()

                elif kind == "extra_qml":

                    val = w.text()

                    ctrl[name] = val if val else ""

                else:

                    ctrl[name] = w.text()

            except:

                pass




    def _refresh_props(self, idx: int):

        """数据驱动：将 controls[idx] 的值填入属性面板。"""

        controls = self._active_controls

        if idx < 0 or idx >= len(controls):

            return

        ctrl = controls[idx]

        self._props_refreshing = True

        self._prop_type.blockSignals(True)

        self._prop_type.setCurrentText(ctrl.get("type", "ImageButton"))

        self._prop_type.blockSignals(False)

        self._prop_id.setPlaceholderText(f"#  {idx}  [{self._edit_mode}]")

        self._write_prop_fields(ctrl)

        self._update_props_visibility(ctrl)

        self._props_refreshing = False




    def _gen_sprite_frame_expr(self):

        """根据当前 half 和 bind 值生成 spriteFrame 表达式。"""

        hw = ""

        hh = ""

        bind_val = self._prop_bind.currentText()

        if self._chk_right_w.isChecked():

            hw = "right"

        elif self._chk_left_w.isChecked():

            hw = "left"

        if self._chk_bottom_h.isChecked():

            hh = "bottom"

        elif self._chk_top_h.isChecked():

            hh = "top"



        # 确定亮/灭帧号

        on_frame, off_frame = 1, 0  # 默认右=1=亮

        if hw == "left":

            on_frame, off_frame = 0, 1

        if hh == "top":

            on_frame, off_frame = 0, 1

        elif hh == "bottom":

            on_frame, off_frame = 1, 0



        from builder.controls import get_all_binds
        all_binds = get_all_binds()
        bind_actual = all_binds.get(bind_val, bind_val)

        if not bind_actual:

            bind_actual = "status.homedX"



        expr = f"{bind_actual} ? {on_frame} : {off_frame}"

        self._prop_sprite_frame_bind.setText(expr)

        # 同时写入静态值作为导出前的回退

        self._prop_sprite_frame.setText(f"{on_frame}" if hw == "right" or hh == "bottom" else f"{off_frame}")

        self._on_prop_changed()




    def _browse_pressed_src(self):

        """浏览选择按下状态贴图。"""

        path, _ = QFileDialog.getOpenFileName(

            self, Tr.t("_browse_pressed_src.s41_d35e51", "Select pressed-state image"), "",

            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"

        )

        if path:

            self._prop_pressed_src.setText(path)




    def _browse_src(self):

        """浏览选择控件贴图文件。"""

        path, _ = QFileDialog.getOpenFileName(

            self, Tr.t("_browse_src.s43_8d5c1c", "Select image"), "",

            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"

        )

        if path:

            self._prop_src.setText(path)

            # 自动取图片尺寸更新宽高

            pm = QPixmap(path)

            if not pm.isNull():

                self._prop_w.setValue(pm.width())

                self._prop_h.setValue(pm.height())




    def _set_row_visible(self, key: str, visible: bool):

        """隐藏/显示属性整行（label + widget）。"""

        pm = self._prop_map()

        if key not in pm:

            return

        w, kind, default = pm[key]

        # 控件本体

        w.setVisible(visible)

        # 同行 QLabel

        if w in self._field_to_label:

            self._field_to_label[w].setVisible(visible)

        # 关联的浏览按钮

        if key == "src" and hasattr(self, '_btn_browse_src'):

            self._btn_browse_src.setVisible(visible)

        if key == "pressedSource" and hasattr(self, '_btn_browse_psrc'):

            self._btn_browse_psrc.setVisible(visible)

        if key == "spriteFrame" and hasattr(self, '_btn_gen_sprite'):

            self._btn_gen_sprite.setVisible(visible)




    def _update_props_visibility(self, ctrl):

        """根据控件类型显示/隐藏属性字段（数据驱动）。"""

        ctype = ctrl if isinstance(ctrl, str) else ctrl.get("type", "")

        from builder.controls import get_properties, PROP_BINDABLE

        allowed = {"x", "y", "w", "h", "src"} | set(get_properties(ctype))

        for key in self._prop_map():

            self._set_row_visible(key, key in allowed)

        self._set_row_visible("id", True if ctype else False)

        self._set_row_visible("z", True if ctype else False)

        # 绑定表达式行

        for key in ("activeLineBind", "allowSelectionBind",

                    "activeBind", "valueBind", "sourceClipRectBind", "spriteFrameBind"):

            parent = key.replace("Bind", "")

            self._set_row_visible(key, parent in allowed and parent in PROP_BINDABLE)

        show_half = "half" in allowed

        self._chk_left_w.setVisible(show_half)

        self._chk_right_w.setVisible(show_half)

        self._chk_top_h.setVisible(show_half)

        self._chk_bottom_h.setVisible(show_half)




    def _on_zone_prop_changed(self):

        """编辑区属性变化（画布空白处属性）。"""

        if self._undo_needs_push:

            self._push_undo_snapshot()

        zone = self._get_zone_data()

        zone["x"] = int(self._prop_x.value())

        zone["y"] = int(self._prop_y.value())

        zone["width"] = int(self._prop_w.value())

        zone["height"] = int(self._prop_h.value())

        zone["bg"] = self._prop_src.text()

        bgw_w = self._field_widgets.get("bgW")

        bgw_h = self._field_widgets.get("bgH")

        if bgw_w: zone["bgW"] = int(bgw_w.value())

        if bgw_h: zone["bgH"] = int(bgw_h.value())

        # 更新画布偏移和视口

        if self._edit_mode == "side_panel":

            # 侧栏改完只刷新即可，不改变主画布尺寸

            self._refresh_canvas()

        else:

            self._canvas._page_offset = (zone["x"], zone["y"], zone["width"], zone["height"])

            self._canvas._apply_zoom(zone["width"], zone["height"])

            self._refresh_canvas()




    def _on_canvas_select(self, idx: int):

        """画布上选中了某个控件（或无选择时显示页属性）。"""

        self._undo_needs_push = True  # 新的选中 = 新的编辑批次

        if idx >= 0:

            # 根据画布的 sel_zone 决定属性面板读取哪个区域

            self._edit_mode = "side_panel" if self._canvas._sel_zone == "right" else "page"

            self._refresh_props(idx)

        else:

            self._show_page_props()




    def _show_page_props(self):

        """显示当前编辑区（画布）的属性。"""

        self._props_refreshing = True

        zone = self._get_zone_data()

        for widget in (self._prop_type, self._prop_x, self._prop_y,

                       self._prop_w, self._prop_h, self._prop_src,

                       self._prop_action, self._prop_bind, self._prop_text,

                       self._prop_font_size, self._prop_bg_color, self._prop_opacity,

                       self._chk_border, self._prop_border_w, self._prop_border_color):

            widget.blockSignals(True)

        # 画布属性

        self._prop_type.setCurrentText("(window)")

        self._prop_id.setPlaceholderText(f"({self._get_zone_name()})")

        is_zone = (self._edit_mode in ("page", "side_panel"))

        self._prop_x.setValue(self._i(zone.get("x", 0)))

        self._prop_y.setValue(self._i(zone.get("y", 0)))

        self._prop_x.setEnabled(is_zone)

        self._prop_y.setEnabled(is_zone)

        self._prop_w.setValue(self._i(zone.get("width", 1024)))

        self._prop_h.setValue(self._i(zone.get("height", 768)))

        self._prop_src.setText(zone.get("bg", ""))

        self._prop_action.setCurrentText("")

        self._prop_bind.setCurrentText("")

        self._prop_text.setText(zone.get("name", ""))

        # 背景图尺寸（仅 page 级，0=跟随页面尺寸）

        bgw_w = self._field_widgets.get("bgW")

        bgw_h = self._field_widgets.get("bgH")

        if bgw_w:

            bgw_w.blockSignals(True)

            bgw_w.setValue(self._i(zone.get("bgW", 0)))

        if bgw_h:

            bgw_h.blockSignals(True)

            bgw_h.setValue(self._i(zone.get("bgH", 0)))

        for widget in (self._prop_type, self._prop_x, self._prop_y,

                       self._prop_w, self._prop_h, self._prop_src,

                       self._prop_action, self._prop_bind, self._prop_text,

                       self._prop_font_size, self._prop_bg_color, self._prop_opacity,

                       self._chk_border, self._prop_border_w, self._prop_border_color):

            widget.blockSignals(False)

        # 解锁

        if bgw_w: bgw_w.blockSignals(False)

        if bgw_h: bgw_h.blockSignals(False)

        # 只显示 x,y,w,h + src + text + bgW/bgH（区属性），其余整行隐藏

        self._set_row_visible("src", True)

        self._set_row_visible("text", True)

        self._set_row_visible("bgW", True)

        self._set_row_visible("bgH", True)

        for key in ("action", "bind", "fontSize", "bgColor", "opacity",

                    "border", "borderW", "borderC", "container", "half",

                    "pressedSource", "decimals", "activeLine",

                    "enabled", "allowSelection", "isHorizontal",

                    "active", "isToggle", "value", "from", "to",

                    "unit", "pinName", "accentColor", "textColor",

                    "activeColor", "inactiveColor", "defaultColor", "pressedColor",

                    "action_press", "action_release", "sourceClipRect", "sourceClipRectBind",

                    "spriteFrame", "spriteFrameBind",

                    "interval", "repeat", "running",

                    "activeLineBind", "allowSelectionBind",

                    "activeBind", "valueBind", "z"):

            self._set_row_visible(key, False)

        self._chk_left_w.setVisible(False)

        self._chk_right_w.setVisible(False)

        self._chk_top_h.setVisible(False)

        self._chk_bottom_h.setVisible(False)

        self._props_refreshing = False



