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
统一控件定义 — 基于 qmlvcp 控件源码的属性定义。

每个控件:
  - type:        Builder 内显示的名称
  - category:    分类
  - properties:  属性面板要显示的字段 > x y w h 以外
  - defaults:    默认值
  - template:    模板名 → builder/templates/ 下对应的 .qml 文件
"""

import os
from backend_actions_binds import get_actions, get_binds, get_all_actions, get_all_binds
from lang import Tr

CONTROLS = []
from builder.templates import CONTROLS as _cts
CONTROLS = _cts

# ====================================================================
#  属性中文说明 & 可绑定列表
# ====================================================================

# ═══════════════════════════════════════════════════════════
# 属性注册表（唯一真源）— 新增属性只需加在这里
# ═══════════════════════════════════════════════════════════
# 格式: { name: (label, kind, default, tooltip, options) }
FIELD_KINDS = {
    "id":              (Tr.t("controls.s1_f3c00c", "Identifier"),     "text",          "",     Tr.t("controls.s2_ee5078", "QML id (referenced by other controls)"), {}),
    "title":           (Tr.t("controls.s3_32c65d", "Title"),       "text",          "",     Tr.t("controls.s4_6f4ced", "Dialog title"), {}),
    "src":             (Tr.t("controls.s5_75432c", "Sprite"),       "path",          "",     Tr.t("controls.s6_f1f0fb", "Sprite file path (assets/xxx.png)"), {}),
    "pressedSource":   (Tr.t("controls.s9_15764f", "Alt Sprite"),   "path",          "",     Tr.t("controls.s8_64c7d7", "Sprite for pressed state (optional, leave blank to use src)"), {"optional": True}),
    "pressedSrc":      (Tr.t("controls.s9_15764f", "Alt Sprite"),   "path",          "",     Tr.t("controls.s10_c906e2", "Pressed-state image"), {"optional": True}),
    "bg":              (Tr.t("controls.s11_8e1b94", "Background"),       "path",          "",     Tr.t("controls.s12_bb52ec", "Background image path"), {}),
    "bgW":             (Tr.t("controls.s13_95dd65", "Background width"),     "int",           0,      Tr.t("controls.s14_ac82ed", "Render width (0=follow page width)"), {"range": (0, 4096)}),
    "bgH":             (Tr.t("controls.s15_5a9586", "Background height"),     "int",           0,      Tr.t("controls.s16_e5a633", "Render height (0=follow page height)"), {"range": (0, 4096)}),
    "action":          (Tr.t("controls.s17_c500cf", "Action"),       "action_combo",  "",     Tr.t("controls.s18_7456d5", "Action on click (onClicked / onLineSelected)"), {}),
    "action_press":    (Tr.t("controls.s19_70cf0a", "Press"),       "jog_action_combo", "",     Tr.t("controls.s20_4eb283", "JOG action on press"), {}),
    "action_release":  (Tr.t("controls.s21_daa3ce", "Release"),       "jog_action_combo", "",     Tr.t("controls.s22_c2050e", "JOG action on release"), {}),
    "bind":            (Tr.t("controls.s23_f4f12c", "Bind"),       "bind_combo",    "",     Tr.t("controls.s24_0000e7", "Bind to state variable (status.xxx / backend.xxx)"), {}),
    "enabled":         (Tr.t("controls.s25_56a30e", "Allow condition:"),  "bool_expr",     True,   Tr.t("controls.s26_d8aab0", "true/false or bind expr (e.g. backend.machineOn)"),
                        {"options": [
                        "true", "false",
                        """!(backend.machineMode === "自动" && !backend.interpIdle)""",
                        "backend.machineOn",
                        ]}),
    "active":          (Tr.t("controls.s27_90f89a", "On/Off"),       "bool",          False,  Tr.t("controls.s28_c5b0f8", "LED on/off state"), {}),
    "isSprite":        (Tr.t("controls.s29_5b60ad", "Sprite"),     "bool",          False,  Tr.t("controls.s30_e13ae0", "Sprite-based control"), {}),
    "isHorizontal":    (Tr.t("controls.s31_db572d", "Horizontal layout"),   "bool",          True,   Tr.t("controls.s32_59e3f5", "Sprite layout: on=horizontal, off=vertical"), {}),
    "isToggle":        (Tr.t("controls.s33_4417d2", "Toggle mode"),   "bool",          False,  Tr.t("controls.s34_53b6a2", "Toggle switch (press=latched / release=unlatched)"), {}),
    "repeat":          (Tr.t("controls.s35_69bdc6", "Loop"),       "bool",          False,  Tr.t("controls.s36_b69760", "Whether to loop trigger"), {}),
    "running":         (Tr.t("controls.s37_4c763b", "Run"),       "bool",          True,   Tr.t("controls.s38_eaf2d6", "Whether to start the timer"), {}),
    "container":       (Tr.t("controls.s39_22c799", "Container"),       "bool",          False,  Tr.t("controls.s40_7e20fe", "Child control container (relative positioning)"), {}),
    "border":          (Tr.t("controls.s41_961534", "Border"),       "bool",          False,  Tr.t("controls.s42_739282", "Whether to show border"), {}),
    "allowSelection":  (Tr.t("controls.s43_674dbd", "Allow selection"),   "bool",          True,   Tr.t("controls.s44_a69824", "GCodeViewer manual line selection"), {}),
    "showWorkAxes":    (Tr.t("controls.s45_98cba5", "Show work axis"), "bool",          False,  Tr.t("controls.s46_6090b3", "GCodeGraphics show workpiece axes"), {}),
    "isOrthographic":  (Tr.t("controls.s47_90674d", "Ortho"),       "bool",          True,   Tr.t("controls.s48_6b4f05", "GCodeGraphics ortho/perspective view"), {}),
    "fontSize":        (Tr.t("controls.s49_fc55af", "Font size"),       "int",           16,     Tr.t("controls.s50_1b03d0", "Font size (pixels)"), {"range": (1, 200)}),
    "decimals":        (Tr.t("controls.s51_0378d9", "Precision"),     "int",           4,      Tr.t("controls.s52_e284e6", "Decimal places"), {"range": (0, 10)}),
    "activeLine":      (Tr.t("controls.s53_fcb663", "Highlight line"),     "int",           -1,     Tr.t("controls.s54_480744", "GCodeViewer active line highlight"), {"range": (-1, 999999)}),
    "interval":        (Tr.t("controls.s55_579052", "Interval (ms)"),   "int",           1000,   Tr.t("controls.s56_1d4dab", "Timer trigger interval (ms)"), {"range": (1, 999999)}),
    "borderThickness": (Tr.t("controls.s57_ae1776", "Border thickness"),   "int",           2,      Tr.t("controls.s58_9a4b54", "Button inner border thickness (pixels)"), {"range": (0, 20)}),
    "shrinkAmount":    (Tr.t("controls.s59_4e98d1", "Sunken Pixels"),   "int",           2,      Tr.t("controls.s60_862f24", "Pressed core collapse pixels"), {"range": (0, 20)}),
    "borderW":         (Tr.t("controls.s61_61bf5b", "Border Width"),     "int",           1,      Tr.t("controls.s62_605c53", "Border width (pixels)"), {"range": (0, 20)}),
    "z":               (Tr.t("controls.s63_4af0aa", "Z Level"),      "int",           0,      Tr.t("controls.s64_3eb6ad", "Control z-order level"), {"range": (0, 999)}),
    "opacity":         (Tr.t("controls.s65_34dac4", "Opacity"),     "int",           100,    Tr.t("controls.s66_8ad257", "Opacity (10-100%)"), {"range": (10, 100)}),
    "cameraZoom":      (Tr.t("controls.s67_05853d", "Zoom"),       "float",         5.0,    Tr.t("controls.s68_afb166", "GCodeGraphics orthographic camera zoom ratio"), {"range": (0.1, 10.0)}),
    "value":           ("值",         "float",         0,      Tr.t("controls.s70_e52c27", "Current value"), {"range": (-9999, 99999)}),
    "from":            (Tr.t("controls.s71_c322ed", "Min"),     "float",         0,      Tr.t("controls.s72_769d19", "Slider minimum value"), {"range": (-9999, 99999)}),
    "to":              (Tr.t("controls.s73_5da893", "Max"),     "float",         200,    Tr.t("controls.s74_7bed8c", "Slider maximum value"), {"range": (-9999, 99999)}),
    "color":           (Tr.t("controls.s77_94e49c", "Text Color"),     "color",         "#ffffff", Tr.t("controls.s76_f682db", "Text color (Hex color value)"), {}),
    "textColor":       (Tr.t("controls.s77_94e49c", "Text Color"),     "color",         "#ffffff", Tr.t("controls.s78_7ec907", "Text color"), {}),
    "bgColor":         (Tr.t("controls.s79_2f97db", "Background Color"),     "color",         "transparent", Tr.t("controls.s80_308179", "Background fill color (Hex color value)"), {}),
    "accentColor":     (Tr.t("controls.s81_b47707", "Theme Color"),     "color",         "#3388ff", Tr.t("controls.s82_206c42", "Theme accent color"), {}),
    "activeColor":     (Tr.t("controls.s83_df85ba", "Active Color"),     "color",         "#00ff00", Tr.t("controls.s84_a7c732", "Active/highlighted color"), {}),
    "inactiveColor":   (Tr.t("controls.s85_d088bc", "Inactive Color"),   "color",         "#555555", Tr.t("controls.s86_caa2f1", "Inactive/off color"), {}),
    "defaultColor":    (Tr.t("controls.s87_d65d5b", "Default Color"),     "color",         "#0088ff", Tr.t("controls.s88_110cad", "HalButton default background color"), {}),
    "pressedColor":    (Tr.t("controls.s89_da7910", "Pressed Color"),     "color",         "#00ffff", Tr.t("controls.s90_98c5bd", "Pressed state color"), {}),
    "highlightColor":  (Tr.t("controls.s91_900697", "Highlight Color"),     "color",         "#00cc00", Tr.t("controls.s92_c0a125", "Highlight/theme accent color"), {}),
    "borderC":         (Tr.t("controls.s93_b5c63e", "Border Color"),     "color",         "#555555", Tr.t("controls.s94_b74b89", "Border color (Hex color value)"), {}),
    "text":            (Tr.t("controls.s95_ca746b", "Text"),       "text",          "",     Tr.t("controls.s96_a2f537", "Displayed text content"), {}),
    "label":           (Tr.t("controls.s97_14d342", "Label"),       "text",          "",     Tr.t("controls.s98_52f8ff", "Label text (HalSlider title)"), {}),
    "unit":            (Tr.t("controls.s99_f29968", "Unit"),       "text",          "",     Tr.t("controls.s163_6c924a", "Unit (mm/ %/ rpm)"), {}),
    "pinName":         (Tr.t("controls.s101_be46a7", "Pin"),       "text",          "",     Tr.t("controls.s150_1db13e", "HAL pin name"), {}),
    "spriteFrame":     (Tr.t("controls.s103_84e5df", "Sprite frame"),     "expression",    "",     Tr.t("controls.s104_a151eb", "Current sprite frame expression"), {"placeholder": Tr.t("controls.s105_d516f4", "e.g. status.homedX ? 0 : 1")}),
    "sourceClipRect":  (Tr.t("controls.s106_f785a3", "Clip region"),   "expression",    "",     Tr.t("controls.s107_ae3efd", "Image clip region Qt.rect(...)"), {"placeholder": Tr.t("controls.s108_571964", "e.g. Qt.rect(0,0,16,26)")}),
    "half":            (Tr.t("controls.s109_10455a", "Frame direction"),     "half",          "none", Tr.t("controls.s131_17d306", "Direction: Left=0, Right=1"), {}),
    "spriteOrientation":(Tr.t("controls.s111_6c1b9b", "Sprite direction"),"int",           0,      "", {"range": (0, 3)}),
    "machineName":     (Tr.t("controls.s112_9ea6a0", "Machine name"),     "text",          "",     Tr.t("controls.s113_c42dc4", "Machine name display"), {}),
    "maxVelocity":     (Tr.t("controls.s114_15c184", "Max speed"),   "float",         3000,   "", {"range": (0, 99999)}),
    "primaryColor":    (Tr.t("controls.s115_fbae87", "Main color"),       "color",         "#2196F3", "", {}),
    "extraQml":        (Tr.t("controls.s116_a04024", "Custom properties"), "extra_qml",      "",     Tr.t("controls.s117_9a32d0", "Write custom QML properties appended to control"), {}),
}

PROP_TOOLTIPS = {
    "src":           Tr.t("controls.s6_f1f0fb", "Sprite file path (assets/xxx.png)"),
    "pressedSource": Tr.t("controls.s8_64c7d7", "Sprite for pressed state (optional, leave blank to use src)"),
    "action":        Tr.t("controls.s120_58f9f8", "Action on click (onClicked)"),
    "action_press":  Tr.t("controls.s121_fc64fb", "JOG action on press (JOG_X+ etc.)"),
    "action_release": Tr.t("controls.s122_bc65ec", "JOG action on release (JOG_X_STOP etc.)"),
    "sourceClipRect":Tr.t("controls.s123_016e44", "Clip region Qt.rect(0,0,w,h)"),
    "spriteFrame":   Tr.t("controls.s124_900bce", "Sprite frame expr (status.homedX ? 0 : 1)"),
    "interval":      Tr.t("controls.s56_1d4dab", "Timer trigger interval (ms)"),
    "repeat":        Tr.t("controls.s36_b69760", "Whether to loop trigger"),
    "running":       Tr.t("controls.s38_eaf2d6", "Whether to start the timer"),
    "enabled":       Tr.t("controls.s128_7ac135", "Interactive (bindable to backend.isIdle)"),
    "borderThickness": Tr.t("controls.s58_9a4b54", "Button inner border thickness (pixels)"),
    "shrinkAmount":  Tr.t("controls.s60_862f24", "Pressed core collapse pixels"),
    "half":          Tr.t("controls.s131_17d306", "Direction: Left=0, Right=1"),
    "isHorizontal":  Tr.t("controls.s32_59e3f5", "Sprite layout: on=horizontal, off=vertical"),
    "active":        Tr.t("controls.s133_a932eb", "LED on/off (bindable)"),
    "bind":          Tr.t("controls.s24_0000e7", "Bind to state variable (status.xxx / backend.xxx)"),
    "text":          Tr.t("controls.s96_a2f537", "Displayed text content"),
    "fontSize":      Tr.t("controls.s50_1b03d0", "Font size (pixels)"),
    "color":         Tr.t("controls.s76_f682db", "Text color (Hex color value)"),
    "bgColor":       Tr.t("controls.s80_308179", "Background fill color (Hex color value)"),
    "opacity":       Tr.t("controls.s139_c4da5e", "Opacity (10-100%)"),
    "border":        Tr.t("controls.s42_739282", "Whether to show border"),
    "borderW":       Tr.t("controls.s62_605c53", "Border width (pixels)"),
    "borderC":       Tr.t("controls.s94_b74b89", "Border color (Hex color value)"),
    "container":     Tr.t("controls.s40_7e20fe", "Child control container (relative positioning)"),
    "decimals":      Tr.t("controls.s144_b4f40a", "Decimal places"),
    "activeLine":    Tr.t("controls.s145_c4d3bd", "Active line (bind lineNumber)"),
    "allowSelection":Tr.t("controls.s146_9c6327", "Manual line sel (bind isIdle)"),
    "showWorkAxes":  Tr.t("controls.s46_6090b3", "GCodeGraphics show workpiece axes"),
    "isOrthographic":Tr.t("controls.s48_6b4f05", "GCodeGraphics ortho/perspective view"),
    "cameraZoom":    Tr.t("controls.s68_afb166", "GCodeGraphics orthographic camera zoom ratio"),
    "pinName":       Tr.t("controls.s150_1db13e", "HAL pin name"),
    "isToggle":      Tr.t("controls.s34_53b6a2", "Toggle switch (press=latched / release=unlatched)"),
    "defaultColor":  Tr.t("controls.s88_110cad", "HalButton default background color"),
    "pressedColor":  Tr.t("controls.s90_98c5bd", "Pressed state color"),
    "textColor":     Tr.t("controls.s78_7ec907", "Text color"),
    "highlightColor":Tr.t("controls.s92_c0a125", "Highlight/theme accent color"),
    "accentColor":   Tr.t("controls.s156_7527f6", "Theme accent (title/Slider/DRO)"),
    "activeColor":   Tr.t("controls.s84_a7c732", "Active/highlighted color"),
    "inactiveColor": Tr.t("controls.s86_caa2f1", "Inactive/off color"),
    "label":         Tr.t("controls.s98_52f8ff", "Label text (HalSlider title)"),
    "value":         Tr.t("controls.s160_0e82c0", "Current value (bindable)"),
    "from":          Tr.t("controls.s72_769d19", "Slider minimum value"),
    "to":            Tr.t("controls.s74_7bed8c", "Slider maximum value"),
    "unit":          Tr.t("controls.s163_6c924a", "Unit (mm/ %/ rpm)"),
}

# 支持绑定表达式（生成 $prop: backend.xxx 而非固定值）
PROP_BINDABLE = {
    "activeLine", "allowSelection", "enabled", "active",
    "value", "isToggle", "showWorkAxes", "isOrthographic",
    "cameraZoom", "isHorizontal", "decimals",
    "sourceClipRect", "spriteFrame",
}

# ====================================================================
#  查询 API
# ====================================================================

def _get_tmpl(ctype: str) -> str:
    """从 templates/ 目录加载控件的 QML 模板字符串。"""
    from builder.templates import get_template
    for c in CONTROLS:
        if c["type"] == ctype:
            return get_template(c.get("template", ctype))
    return ""

def get_properties(ctype):
    """返回控件需要的属性字段（从模板自动解析，不再依赖 properties 列表）。"""
    from builder.field_registry import parse_template, FIELD_KINDS
    for c in CONTROLS:
        if c["type"] == ctype:
            tmpl = _get_tmpl(c["type"])
            if tmpl:
                raw = parse_template(tmpl)
                fields = [f for f in raw
                          if f not in {"x", "y", "w", "h", "src"}
                          and f in FIELD_KINDS]
                # 特殊补丁：Text 系控件 $bind → text 字段也要显示（作为静态回退）
                if "bind" in fields and "text" not in fields and ctype in ("Text (DRO)", "Text (Label)"):
                    fields.append("text")
                # 补丁：SpriteButton/LED 的 half（图帧预览开关）
                if ctype in ("SpriteButton", "LED", "EmergencyStop", "FlashLED") and "half" not in fields:
                    fields.append("half")
                # 补丁：Rectangle 的容器/边框开关 → 无模板占位符的特殊属性
                if ctype == "Rectangle":
                    for k in ("border", "container"):
                        if k not in fields:
                            fields.append(k)
                return fields
            return c.get("properties", [])
    return []

def get_display_list():
    """返回控件列表供 UI 显示（含分类分隔符）。"""
    result = []
    seen = set()
    for c in CONTROLS:
        cat = c["category"]
        if cat not in seen:
            result.append({"name": f"--- {cat} ---", "type": None})
            seen.add(cat)
        result.append({"name": c.get("displayName", c["type"]), "type": c["type"]})
    return result

def get_defaults(ctype):
    """获取控件默认值。"""
    for c in CONTROLS:
        if c["type"] == ctype:
            d = dict(c["defaults"])
            d["type"] = ctype
            return d
    return None

def get_qml_template(ctype):
    """获取控件 QML 导出模板。"""
    return _get_tmpl(ctype)

def _bind_val(ctrl, key, *args):
    """绑定表达式优先：如果 <key>Bind 存在则返回原始表达式，否则返回静态值。
    
    用法:
        _bind_val(ctrl, "enabled")         → bool, 默认 true
        _bind_val(ctrl, "enabled", "true", "false")
        _bind_val(ctrl, "activeLine")      → 数值, 默认 -1
        _bind_val(ctrl, "activeLine", 0)   → 数值, 指定默认 0
    """
    bind_expr = ctrl.get(f"{key}Bind", "")
    if bind_expr:
        return bind_expr
    val = ctrl.get(key)
    if val is not None and val != "":
        if isinstance(val, bool):
            return "true" if val else "false"
        return str(val)
    # 回退到默认值
    if len(args) == 2:
        # bool: _bind_val(ctrl, k, true_val, false_val)
        return args[1]  # false_val = default
    elif len(args) == 1:
        return str(args[0])  # 数值默认
    return "true"  # 最终兜底

def fill_template(ctrl):
    """将控件字典填入 QML 模板。"""
    ctype = ctrl.get("type", "ImageButton")
    template = get_qml_template(ctype)
    if not template:
        return ""

    result = template
    bind_val = ctrl.get("bind", get_defaults(ctype).get("bind", ""))
    fallback = ctrl.get("text", "")
    tk = {
        "$x":          str(ctrl.get("x", 0)),
        "$y":          str(ctrl.get("y", 0)),
        "$w":          str(ctrl.get("w", 80)),
        "$h":          str(ctrl.get("h", 40)),
        "$src":        os.path.basename(ctrl.get("src", "")).replace("\\\\", "/").replace("\\", "/") or "placeholder.png",
        "$pressedSrc":  (lambda _n: f'assetsDir + "/assets/{_n}"' if _n else '""')(
            os.path.basename(ctrl.get("pressedSource", "")).replace("\\\\", "/").replace("\\", "/")
        ),
        "$action":     ctrl.get("action", ""),
        "$fontSize":   str(ctrl.get("fontSize", 28)),
        "$color":      ctrl.get("color", "#00ff00"),
		"$bgColor":    ctrl.get("bgColor") or "#00000000",
		"$borderC":    ctrl.get("borderC") or "#555",
		"$borderW":    str(ctrl.get("borderW", 1)),
        "$id":         ctrl.get("id", ""),
        "$text":       ctrl.get("text", ""),
        "$title":      ctrl.get("title", Tr.t("fill_template.s165_d823a0", "Load G-Code file")),
        "$decimals":   str(ctrl.get("decimals", 4)),
        "$enabled":    _bind_val(ctrl, "enabled", "true", "false"),
        "$isHorizontal": _bind_val(ctrl, "isHorizontal", "true", "false"),
        "$active":     _bind_val(ctrl, "active", "true", "false"),
        "$activeLine": _bind_val(ctrl, "activeLine", -1),
        "$allowSelection": _bind_val(ctrl, "allowSelection", "true", "false"),
        "$showWorkAxes": _bind_val(ctrl, "showWorkAxes", "true", "false"),
        "$isOrthographic": _bind_val(ctrl, "isOrthographic", "true", "false"),
        "$cameraZoom": _bind_val(ctrl, "cameraZoom", 1.0),
        "$bind":        bind_val if bind_val else (f'"{fallback}"' if fallback else ""),
        "$pinName":    ctrl.get("pinName", ""),
        "$label":      ctrl.get("label", ctrl.get("text", "")),
        "$from":       str(ctrl.get("from", 0.0)),
        "$to":         str(ctrl.get("to", 200.0)),
        "$value":      _bind_val(ctrl, "value", 0),
        "$unit":       ctrl.get("unit", ""),
        "$isToggle":   _bind_val(ctrl, "isToggle", "true", "false"),
        "$defaultColor":  ctrl.get("defaultColor", "#15FFFFFF"),
        "$pressedColor":  ctrl.get("pressedColor", "#00E5FF"),
        "$textColor":     ctrl.get("textColor", "#FFFFFF"),
        "$highlightColor": ctrl.get("highlightColor", "#00E5FF"),
        "$accentColor":   ctrl.get("accentColor", "#00E5FF"),
        "$activeColor":   ctrl.get("activeColor", "#00E5FF"),
        "$inactiveColor": ctrl.get("inactiveColor", "#333333"),
        "$interval":     str(ctrl.get("interval", 500)),
        "$repeat":       "true" if ctrl.get("repeat", True) else "false",
        "$running":      "true" if ctrl.get("running", True) else "false",
        "$action_press":      ctrl.get("action_press", ""),
        "$action_release":    ctrl.get("action_release", ""),
        "$sourceClipRect":    ctrl.get("sourceClipRectBind", "") or ctrl.get("sourceClipRect", ""),
    }
    for k, v in sorted(tk.items(), key=lambda x: -len(x[0])):
        result = result.replace(k, v)
    # pressedSource 别名兼容
    result = result.replace("$pressedSource", tk["$pressedSrc"] or "")

    sf = 1 if ctrl.get("half_w_dir") == "right" else 0
    # spriteFrame 优先级: 绑定表达式 > 手动输入 > half 默认值
    sprite_val = ctrl.get("spriteFrameBind", "") or ctrl.get("spriteFrame", "")
    if sprite_val:
        result = result.replace("$spriteFrame", str(sprite_val))
    else:
        result = result.replace("$spriteFrame", str(sf))
    result = result.replace("$borderThickness", str(ctrl.get("borderThickness", 2)))
    result = result.replace("$shrinkAmount",    str(ctrl.get("shrinkAmount", 2)))

    if ctrl.get("z", 0) > 0:
        result = result.replace('\n                y:', f'\n                z: {ctrl["z"]}\n                y:', 1)

    # id 注入：Timer 替换 __timer__；其他模板若已有 id: 则跳过避免重复
    cid = ctrl.get("id", "")
    if cid:
        if "__timer__" in result:
            result = result.replace("__timer__", cid, 1)
        elif "            id:" not in result:
            result = result.replace('\n                {', f'\n                id: {cid}\n                {{', 1)

    # 清理空属性行（未填时删除整行）
    import re
    result = re.sub(r'                (onPressed|onReleased|onAccepted|onClicked|onTriggered|sourceClipRect): \n', '', result)
    result = re.sub(r'                text: \n', '', result)
    result = re.sub(r'                gcodeLines: \n', '', result)
    result = re.sub(r'                onClicked: \n', '', result)
    result = re.sub(r'                latched: \n', '', result)
    result = re.sub(r'                id: \n', '', result)
    # 注入手写备用属性（extraQml）
    extra = ctrl.get("extraQml", "").strip()
    if extra:
        idx = result.find("$extraQml")
        if idx >= 0:
            # 有 $extraQml 占位符：用占位符所在行的缩进作为基准，整行替换
            line_start = result.rfind("\n", 0, idx) + 1
            line_end = result.find("\n", idx)
            if line_end < 0:
                line_end = len(result)
            indent = result[line_start:idx]  # 占位符前的缩进前缀
            extra_lines = extra.split("\n")
            extra_block = "\n".join(indent + ln for ln in extra_lines)
            result = result[:line_start] + extra_block + "\n" + result[line_end + 1:]
        else:
            # 没有占位符：注入到最后一个 } 之前
            idx = result.rfind("}")
            if idx >= 0:
                indent = "        "
                extra_lines = extra.split("\n")
                extra_block = "\n".join(indent + ln for ln in extra_lines)
                result = result[:idx] + extra_block + "\n    " + result[idx:]
    else:
        result = result.replace("$extraQml", "")

    return result


def export_controls_qml(controls):
    """将控件列表导出为 QML 代码片段，canvas 输出为 Item。"""
    lines = []
    children_of = {}
    for i, c in enumerate(controls):
        pid = c.get("_parent_id")
        if pid is not None:
            children_of.setdefault(int(pid), []).append((i, c))

    exported = set()

    def _write_item(idx, ctrl):
        if idx in exported or ctrl.get("_skip_export"):
            exported.add(idx)
            return
        exported.add(idx)
        # canvas Rectangle → Item 块
        if ctrl.get("canvas"):
            # 输出 Item 包裹
            snippet = '            Item {\n'
            snippet += f'                x: {ctrl.get("x", 0)}\n                y: {ctrl.get("y", 0)}\n'
            snippet += f'                width: {ctrl.get("w", 400)}\n                height: {ctrl.get("h", 300)}\n'
            for ci, kid in children_of.get(idx, []):
                snippet += fill_template(kid)
            snippet += '            }\n'
            lines.append(snippet)
            return
        # 普通容器（嵌套）
        snippet = fill_template(ctrl)
        kids = children_of.get(idx, [])
        if kids and ctrl.get("type") == "Rectangle" and ctrl.get("container"):
            snippet = snippet.rstrip()
            if snippet.endswith('}'):
                snippet = snippet[:-1] + '\n'
                for ci, kid in kids:
                    exported.add(ci)
                    snippet += fill_template(kid)
                snippet += '            }\n'
        lines.append(snippet)

    for i, c in enumerate(controls):
        pid = c.get("_parent_id")
        if c.get("_skip_export") or pid is not None:
            continue
        _write_item(i, c)

    return "".join(lines)
