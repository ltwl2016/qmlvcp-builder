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
from backend_actions_binds import ACTIONS as _NEW_ACTIONS, STATUS_BINDS as _NEW_STATUS_BINDS

CONTROLS = []
from builder.templates import CONTROLS as _cts
CONTROLS = _cts


# ====================================================================
#  预定义动作 / 绑定列表
# ====================================================================

ACTIONS = {
    # ── 指令 (command，优先) ──
    "--- command ---":  "",
    "cmd.homeAll":      "command.homeAll()",
    "cmd.unhomeAll":    "command.unhomeAll()",
    "cmd.homeX":        "command.homeAxis(0)",
    "cmd.homeY":        "command.homeAxis(1)",
    "cmd.homeZ":        "command.homeAxis(2)",
    "cmd.homeA":        "command.homeAxis(3)",
    "cmd.modeManual":   "command.setModeManual()",
    "cmd.modeAuto":     "command.setModeAuto()",
    "cmd.modeMDI":      "command.setModeMDI()",
    "cmd.estop":        "command.setEstop(1)",
    "cmd.estopReset":   "command.setEstop(0)",
    "cmd.powerOn":      "command.setMachinePower(1)",
    "cmd.powerOff":     "command.setMachinePower(0)",
    "cmd.zeroX":        'command.zero_axis("X")',
    "cmd.zeroY":        'command.zero_axis("Y")',
    "cmd.zeroZ":        'command.zero_axis("Z")',
    "cmd.safeZ":        "command.gotoSafeZ()",
    "cmd.floodOn":      "command.setFlood(1)",
    "cmd.floodOff":     "command.setFlood(0)",
    "cmd.mistOn":       "command.setMist(1)",
    "cmd.mistOff":      "command.setMist(0)",
    "cmd.spindleCW":    "command.setSpindle(1, 0)",
    "cmd.spindleCCW":   "command.setSpindle(-1, 0)",
    "cmd.spindleStop":  "command.setSpindle(0, 0)",
    "cmd.progRun":      "command.programRun(0)",
    "cmd.progPause":    "command.programPause()",
    "cmd.progResume":   "command.programResume()",
    "cmd.progStop":     "command.programStop()",
    "cmd.progOpen":     "command.programOpen(backend.programFile)",
    "cmd.progRewind":   "command.programRewind()",
    "cmd.progSetLine":  "command.programSetLine(currentLine)",
    "cmd.blockDel":     "command.setBlockDelete(!status.blockDelete)",

    # ── MDI 指令 ──
    "--- MDI ---":      "",
    "mdi.G0_X0Y0":      'command.mdi("G0 X0 Y0")',
    "mdi.G28":          'command.mdi("G28")',
    "mdi.G53_Z0":       'command.mdi("G53 Z0")',
    "mdi.fromValue":    'command.mdi("G10 L20 P1 X" + value)',
    "mdi.G92.1":        'command.mdi("G92.1")',

    # ── 页面切换 ──
    "--- 页面切换 ---": "",
    "page.主页":         "stack.currentIndex = 0",
    "page.page1":         "stack.currentIndex = 1",
    "page.page2":         "stack.currentIndex = 2",
    "page.page3":         "stack.currentIndex = 3",
    "page.page4":         "stack.currentIndex = 4",
    "page.page5":         "stack.currentIndex = 5",

    "CUSTOM":           "",

    # ═══════════════════════════════════════════
    # ▼ 以下来自 backend_actions_binds.py，便于日后整块删除
    # ═══════════════════════════════════════════
}

STATUS_BINDS = {
    # ── 状态 (status 优先) ──
    "--- status ---":   "",
    "st.homedX":        "status.homedX",
    "st.homedY":        "status.homedY",
    "st.homedZ":        "status.homedZ",
    "st.homedA":        "status.homedA",
    "st.isAllHomed":    "status.isAllHomed",
    "st.hasError":      "status.hasError",
    "st.interpIdle":    "status.interpIdle",
    "st.spindleSpeed":  "status.spindleSpeed",
    "st.spindleDir":    "status.spindleDir",
    "st.spindleOverride": "status.spindleOverride",
    "st.feed":          "status.feed",
    "st.actualFeed":    "status.actualFeed",
    "st.feedOverride":  "status.feedOverride",
    "st.flood":         "status.flood",
    "st.mist":          "status.mist",
    "st.toolInSpindle": "status.toolInSpindle",
    "st.toolDiameter":  "status.toolDiameter",
    "st.toolOffsetZ":   "status.toolOffsetZ",
    "st.motionLine":    "status.motionLine",
    "st.readLine":      "status.readLine",
    "st.blockDelete":   "status.blockDelete",
    "st.machineMode":   "status.taskMode",
    "st.interpState":   "status.interpState",
    "st.absoluteX":     "status.absoluteX",
    "st.absoluteY":     "status.absoluteY",
    "st.absoluteZ":     "status.absoluteZ",
    "st.machineX":      "status.machineX",
    "st.machineY":      "status.machineY",
    "st.machineZ":      "status.machineZ",

    # ═══════════════════════════════════════════
    # ▼ 以下来自 backend_actions_binds.py，便于日后整块删除
    # ═══════════════════════════════════════════
}

# ── 合并 backend 动作/绑定（保留旧值，新值追加） ──
ACTIONS.update(_NEW_ACTIONS)
STATUS_BINDS.update(_NEW_STATUS_BINDS)

# ====================================================================
#  属性中文说明 & 可绑定列表
# ====================================================================

# ═══════════════════════════════════════════════════════════
# 属性注册表（唯一真源）— 新增属性只需加在这里
# ═══════════════════════════════════════════════════════════
# 格式: { name: (label, kind, default, tooltip, options) }
FIELD_KINDS = {
    "id":              ("标识符",     "text",          "",     "QML id (同文件内其他控件可通过此 id 引用)", {}),
    "title":           ("标题",       "text",          "",     "对话框标题", {}),
    "src":             ("贴图",       "path",          "",     "贴图文件路径 (assets/xxx.png)", {}),
    "pressedSource":   ("备用贴图",   "path",          "",     "按下状态时显示的贴图（可选，留空则同 src）", {"optional": True}),
    "pressedSrc":      ("备用贴图",   "path",          "",     "按下状态时显示的贴图", {"optional": True}),
    "bg":              ("背景",       "path",          "",     "背景贴图路径", {}),
    "bgW":             ("背景宽",     "int",           0,      "背景贴图渲染宽度 (0=跟随页面宽度)", {"range": (0, 4096)}),
    "bgH":             ("背景高",     "int",           0,      "背景贴图渲染高度 (0=跟随页面高度)", {"range": (0, 4096)}),
    "action":          ("动作",       "action_combo",  "",     "点击触发的动作 (onClicked / onLineSelected)", {}),
    "action_press":    ("按下",       "jog_action_combo", "",     "按下时执行的 JOG 动作", {}),
    "action_release":  ("抬起",       "jog_action_combo", "",     "抬起时执行的 JOG 动作", {}),
    "bind":            ("绑定",       "bind_combo",    "",     "绑定到状态变量 (status.xxx / backend.xxx)", {}),
    "enabled":         ("允许条件:",  "bool_expr",     True,   "true/false 或绑定表达式 (如 backend.machineOn)", {}),
    "active":          ("亮灭",       "bool",          False,  "LED 亮/灭状态", {}),
    "isSprite":        ("精灵图",     "bool",          False,  "是否为精灵图控件", {}),
    "isHorizontal":    ("水平布局",   "bool",          True,   "精灵图排列方向：开=横向，关=纵向", {}),
    "isToggle":        ("切换模式",   "bool",          False,  "切换开关模式 (按下锁定/松开弹起)", {}),
    "repeat":          ("循环",       "bool",          False,  "是否循环触发", {}),
    "running":         ("运行",       "bool",          True,   "是否启动定时器", {}),
    "container":       ("容器",       "bool",          False,  "作为子控件容器（子控件相对定位）", {}),
    "border":          ("边框",       "bool",          False,  "是否显示边框", {}),
    "allowSelection":  ("允许选择",   "bool",          True,   "GCodeViewer 是否允许手动点选行", {}),
    "showWorkAxes":    ("显示工件轴", "bool",          False,  "GCodeGraphics 是否显示工件坐标轴", {}),
    "isOrthographic":  ("正交",       "bool",          True,   "GCodeGraphics 正交/透视视图", {}),
    "fontSize":        ("字号",       "int",           16,     "字体大小（像素）", {"range": (1, 200)}),
    "decimals":        ("小数位",     "int",           4,      "小数位数", {"range": (0, 10)}),
    "activeLine":      ("高亮行",     "int",           -1,     "GCodeViewer 当前执行行号高亮", {"range": (-1, 999999)}),
    "interval":        ("间隔(ms)",   "int",           1000,   "定时器触发间隔（毫秒）", {"range": (1, 999999)}),
    "borderThickness": ("边框厚度",   "int",           2,      "按钮内芯裁切边框厚度（像素）", {"range": (0, 20)}),
    "shrinkAmount":    ("下陷像素",   "int",           2,      "按下时内芯塌陷像素", {"range": (0, 20)}),
    "borderW":         ("边框宽",     "int",           1,      "边框宽度（像素）", {"range": (0, 20)}),
    "z":               ("z层级",      "int",           0,      "控件 z 层级", {"range": (0, 999)}),
    "opacity":         ("透明度",     "int",           100,    "透明度 (10-100%)", {"range": (10, 100)}),
    "cameraZoom":      ("缩放",       "float",         5.0,    "GCodeGraphics 正交相机缩放倍率", {"range": (0.1, 10.0)}),
    "value":           ("值",         "float",         0,      "当前值", {"range": (-9999, 99999)}),
    "from":            ("最小值",     "float",         0,      "滑动条最小值", {"range": (-9999, 99999)}),
    "to":              ("最大值",     "float",         200,    "滑动条最大值", {"range": (-9999, 99999)}),
    "color":           ("文字色",     "color",         "#ffffff", "文字颜色 (Hex 色值)", {}),
    "textColor":       ("文字色",     "color",         "#ffffff", "文字颜色", {}),
    "bgColor":         ("背景色",     "color",         "#1e1e1e", "背景填充色 (Hex 色值)", {}),
    "accentColor":     ("主题色",     "color",         "#3388ff", "主题强调色", {}),
    "activeColor":     ("激活色",     "color",         "#00ff00", "激活/点亮时的颜色", {}),
    "inactiveColor":   ("未激活色",   "color",         "#555555", "未激活/熄灭时的颜色", {}),
    "defaultColor":    ("默认色",     "color",         "#0088ff", "HalButton 默认背景色", {}),
    "pressedColor":    ("按下色",     "color",         "#00ffff", "按下时的颜色", {}),
    "highlightColor":  ("高亮色",     "color",         "#00cc00", "高亮/主题强调色", {}),
    "borderC":         ("边框色",     "color",         "#555555", "边框颜色 (Hex 色值)", {}),
    "text":            ("文字",       "text",          "",     "显示的文本内容", {}),
    "label":           ("标签",       "text",          "",     "标签文字 (HalSlider 标题)", {}),
    "unit":            ("单位",       "text",          "",     "数值单位 (mm / % / rpm 等)", {}),
    "pinName":         ("引脚",       "text",          "",     "HAL 硬件引脚名称", {}),
    "spriteFrame":     ("精灵帧",     "expression",    "",     "精灵图当前帧，支持表达式", {"placeholder": "例: status.homedX ? 0 : 1"}),
    "sourceClipRect":  ("裁剪区域",   "expression",    "",     "图片裁剪区域，例: Qt.rect(0,0,16,26)", {"placeholder": "例: Qt.rect(0,0,16,26)"}),
    "half":            ("帧方向",     "half",          "none", "精灵图方向：左=第0帧，右=第1帧", {}),
    "spriteOrientation":("精灵图方向","int",           0,      "", {"range": (0, 3)}),
    "machineName":     ("机床名",     "text",          "",     "机床名称显示", {}),
    "maxVelocity":     ("最大速度",   "float",         3000,   "", {"range": (0, 99999)}),
    "primaryColor":    ("主色",       "color",         "#2196F3", "", {}),
    "extraQml":        ("手写备用属性", "extra_qml",      "",     "展开后手写 QML 属性，将插入到控件定义末尾", {}),
}

PROP_TOOLTIPS = {
    "src":           "贴图文件路径 (assets/xxx.png)",
    "pressedSource": "按下状态时显示的贴图（可选，留空则同 src）",
    "action":        "点击触发的动作 (onClicked)",
    "action_press":  "按下时执行的 JOG 动作，通常选 JOG_X+/JOG_Y+ 等方向移动",
    "action_release": "抬起时执行的 JOG 动作，通常选 JOG_X_STOP/JOG_Y_STOP 等停止",
    "sourceClipRect":"图片裁剪区域，例: Qt.rect(0, 0, 16, 26)",
    "spriteFrame":   "精灵图当前帧，支持表达式: status.homedX ? 0 : 1",
    "interval":      "定时器触发间隔（毫秒）",
    "repeat":        "是否循环触发",
    "running":       "是否启动定时器",
    "enabled":       "控件是否可交互（可绑定 backend.isIdle 等）",
    "borderThickness": "按钮内芯裁切边框厚度（像素）",
    "shrinkAmount":  "按下时内芯塌陷像素",
    "half":          "精灵图方向：左=第0帧，右=第1帧",
    "isHorizontal":  "精灵图排列方向：开=横向，关=纵向",
    "active":        "LED 亮/灭状态（可绑定 status.homedX 等）",
    "bind":          "绑定到状态变量 (status.xxx / backend.xxx)",
    "text":          "显示的文本内容",
    "fontSize":      "字体大小（像素）",
    "color":         "文字颜色 (Hex 色值)",
    "bgColor":       "背景填充色 (Hex 色值)",
    "opacity":       "透明度 (10-100%，数值越小越透明)",
    "border":        "是否显示边框",
    "borderW":       "边框宽度（像素）",
    "borderC":       "边框颜色 (Hex 色值)",
    "container":     "作为子控件容器（子控件相对定位）",
    "decimals":      "小数位数（数值输入框精度）",
    "activeLine":    "GCodeViewer 当前执行行号高亮 (可绑定 status.lineNumber)",
    "allowSelection":"GCodeViewer 是否允许手动点选行 (可绑定 backend.isIdle)",
    "showWorkAxes":  "GCodeGraphics 是否显示工件坐标轴",
    "isOrthographic":"GCodeGraphics 正交/透视视图",
    "cameraZoom":    "GCodeGraphics 正交相机缩放倍率",
    "pinName":       "HAL 硬件引脚名称",
    "isToggle":      "切换开关模式 (按下锁定/松开弹起)",
    "defaultColor":  "HalButton 默认背景色",
    "pressedColor":  "按下时的颜色",
    "textColor":     "文字颜色",
    "highlightColor":"高亮/主题强调色",
    "accentColor":   "主题强调色 (标题栏/Slider/DRO 高亮)",
    "activeColor":   "激活/点亮时的颜色",
    "inactiveColor": "未激活/熄灭时的颜色",
    "label":         "标签文字 (HalSlider 标题)",
    "value":         "当前值 (可绑定 status.spindleSpeed 等实时值)",
    "from":          "滑动条最小值",
    "to":            "滑动条最大值",
    "unit":          "数值单位 (mm / % / rpm 等)",
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
        result.append({"name": c["type"], "type": c["type"]})
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
        "$pressedSrc":  os.path.basename(ctrl.get("pressedSource", "")).replace("\\\\", "/").replace("\\", "/") or "",
        "$action":     ctrl.get("action", ""),
        "$fontSize":   str(ctrl.get("fontSize", 28)),
        "$color":      ctrl.get("color", "#00ff00"),
		"$bgColor":    ctrl.get("bgColor") or "#00000000",
		"$borderC":    ctrl.get("borderC") or "#555",
		"$borderW":    str(ctrl.get("borderW", 1)),
        "$id":         ctrl.get("id", ""),
        "$text":       ctrl.get("text", ""),
        "$title":      ctrl.get("title", "加载 G-Code 文件"),
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
    result = result.replace("$extraQml", "")

    # 注入手写备用属性（extraQml）到控件定义末尾
    extra = ctrl.get("extraQml", "").strip()
    if extra:
        idx = result.rfind("}")
        if idx >= 0:
            indent = "        "
            extra_lines = extra.split("\n")
            extra_block = "\n".join(indent + ln for ln in extra_lines)
            result = result[:idx] + extra_block + "\n    " + result[idx:]

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
