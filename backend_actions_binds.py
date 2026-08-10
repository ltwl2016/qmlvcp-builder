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
#  按控件类型分组的动作 / 绑定注册表
#
#  顶层 key = 控件类型名 (与 builder/templates/__init__.py
#              CONTROLS 列表里的 type 字段一致)
#  特殊 key "_all" = 所有控件都显示的公用条目
#
#  查找规则:
#    get_actions("ImageButton") → _all + ImageButton 的合并结果
#    get_actions(None)          → 仅 _all
# ───────────────────────────────────────────────────

ACTIONS = {

    # ═══════════════════════════════════════════════════
    # ▼ 所有控件通用的公用动作
    # ═══════════════════════════════════════════════════
    "_all": {
        "CUSTOM":           "",
    },

    # ═══════════════════════════════════════════════════
    # ▼ 按钮类 —— 回零 / 主轴 / 程序 / 模式 / MDI / 冷却液 / 电源 / 工具
    # ═══════════════════════════════════════════════════
    "ImageButton": {
        # ── 回零 / 工件坐标 ──
        "--- 回零 ---":         "",
        "HOME_ALL":             "backend.homeAll()",
        "UNHOME_ALL":           "backend.unhomeAll()",
        "TOGGLE_HOME_ALL":      "backend.toggleHomeAll()",
        "HOME_X":               "backend.toggleHoming(0)",
        "HOME_Y":               "backend.toggleHoming(1)",
        "HOME_Z":               "backend.toggleHoming(2)",
        "HOME_A":               "backend.toggleHoming(3)",
        "ZERO_X":               'backend.zeroAxis("X")',
        "ZERO_Y":               'backend.zeroAxis("Y")',
        "ZERO_Z":               'backend.zeroAxis("Z")',
        "ZERO_A":               'backend.zeroAxis("A")',
        "ZERO_C":               'backend.zeroAxis("C")',
        "GOTO_SAFE_Z":          "backend.gotoSafeZ()",
        "GOTO_XY_ZERO":         "backend.gotoXYZero()",

        # ── 倍率 ──
        "--- 倍率 ---":         "",
        "FEED_UP":              "backend.incFeedOverride()",
        "FEED_DOWN":            "backend.decFeedOverride()",
        "FEED_RESET":           "backend.resetFeedOverride()",
        "FEED_SET_50":          "backend.setFeedOverride(50)",
        "FEED_SET_100":         "backend.setFeedOverride(100)",
        "FEED_SET_150":         "backend.setFeedOverride(150)",
        "SPDL_UP":              "backend.incSpindleOverride()",
        "SPDL_DOWN":            "backend.decSpindleOverride()",
        "SPDL_SET_50":          "backend.setSpindleOverride(50)",
        "SPDL_SET_100":         "backend.setSpindleOverride(100)",
        "SPDL_SET_150":         "backend.setSpindleOverride(150)",

        # ── 主轴 ──
        "--- 主轴 ---":         "",
        "TOGGLE_SPINDLE":       "backend.toggleSpindle()",
        "SPINDLE_CW":           "backend.setSpindle(1, 1000)",
        "SPINDLE_CCW":          "backend.setSpindle(-1, 1000)",
        "SPINDLE_STOP":         "backend.setSpindle(0, 0)",

        # ── 电源 / 急停 ──
        "--- 电源 ---":         "",
        "TOGGLE_POWER":         "backend.togglePowerState()",
        "POWER_ON":             "backend.setMachinePower(1)",
        "POWER_OFF":            "backend.setMachinePower(0)",
        "ESTOP":                "backend.setEstop(1)",
        "ESTOP_RESET":          "backend.setEstop(0)",
        "CLEAR_ALARM":          "backend.clearAlarm()",

        # ── 程序控制 ──
        "--- 程序 ---":         "",
        "LOAD_PROG":            "backend.loadProgram(backend.programFile)",
        "PROG_RUN":             "backend.programRun(0)",
        "PROG_PAUSE":           "backend.programPause()",
        "PROG_STOP":            "backend.programStop()",
        "PROG_REWIND":          "backend.rewindProgram()",
        "PROG_CLOSE":           "backend.closeProgram()",
        "PROG_RELOAD":          "backend.reloadProgram()",
        "PROG_EDIT":            "backend.editProgram()",

        # ── 模式切换 ──
        "--- 模式 ---":         "",
        "MODE_MANUAL":          'backend.setMachineMode("手动")',
        "MODE_AUTO":            'backend.setMachineMode("自动")',
        "MODE_MDI":             'backend.setMachineMode("MDI")',
        "TOGGLE_MODE":          "backend.toggleTaskMode()",
        "TOGGLE_MACHINE_COORD": "backend.toggleMachineCoordinates()",
        "SELECT_COORD_0":       "backend.selectSystem(0)",
        "SELECT_COORD_1":       "backend.selectSystem(1)",
        "SELECT_COORD_2":       "backend.selectSystem(2)",
        "SELECT_COORD_3":       "backend.selectSystem(3)",

        # ── MDI（静态指令，无需 text） ──
        "--- MDI ---":          "",
        "MDI_G0_X0Y0":          'backend.submitCommand("G0 X0 Y0")',
        "MDI_G28":              'backend.submitCommand("G28")',
        "MDI_G53_Z0":           'backend.submitCommand("G53 Z0")',
        "MDI_G92.1":            'backend.submitCommand("G92.1")',
        "MDI_G54":              'backend.submitCommand("G54")',
        "MDI_M3_S1000":         'backend.submitCommand("M3 S1000")',
        "MDI_M5":               'backend.submitCommand("M5")',

        # ── 冷却液 ──
        "--- 冷却液 ---":       "",
        "FLOOD_ON":             "backend.setFlood(1)",
        "FLOOD_OFF":            "backend.setFlood(0)",
        "MIST_ON":              "backend.setMist(1)",
        "MIST_OFF":             "backend.setMist(0)",

        # ── 工具 ──
        "--- 工具 ---":         "",
        "HAL_SHOW":             "backend.showHalShow()",
        "TOGGLE_SINGLE_BLOCK":  "backend.toggleSingleBlock()",
        "TOGGLE_BLOCK_DELETE":  "backend.toggleBlockDelete()",
        "TOGGLE_RTCP":          "backend.toggleRtcp(status.rtcpActive)",
        "TOGGLE_Z_INHIBIT":     "backend.toggleZInhibit()",
        "AUTO_TOOL_ZERO":       "backend.autoToolZero()",
        "REMEMBER_POS":         "backend.rememberPosition()",
        "RETURN_POS":           "backend.returnPosition()",
        "CHANGE_DIR":           'backend.changeDir("/media/cnc/programs")',
        "RUN_FROM_LINE":        "backend.requestRunFromLine(0)",
        "LAUNCH_HAL_SHOW":      "backend.launchHalShow()",

        # ── 页面切换 ──
        "--- 页面切换 ---":     "",
        "page.主页":            "stack.currentIndex = 0",
        "page.page1":           "stack.currentIndex = 1",
        "page.page2":           "stack.currentIndex = 2",
        "page.page3":           "stack.currentIndex = 3",
        "page.page4":           "stack.currentIndex = 4",
        "page.page5":           "stack.currentIndex = 5",
    },

    # ═══════════════════════════════════════════════════
    # ▼ SpriteButton —— 同 ImageButton
    # ═══════════════════════════════════════════════════
    "SpriteButton": {},  # 空 = 继承 ImageButton，在 get_actions 里处理

    # ═══════════════════════════════════════════════════
    # ▼ JOG 按钮 —— 只显示 JOG 动作
    # ═══════════════════════════════════════════════════
    "JOGButton": {
        "--- JOG ---":          "",
        "JOG_X+":               "backend.jogAxis(0, 1)",
        "JOG_X-":               "backend.jogAxis(0, -1)",
        "JOG_Y+":               "backend.jogAxis(1, 1)",
        "JOG_Y-":               "backend.jogAxis(1, -1)",
        "JOG_Z+":               "backend.jogAxis(2, 1)",
        "JOG_Z-":               "backend.jogAxis(2, -1)",
        "JOG_A+":               "backend.jogAxis(3, 1)",
        "JOG_A-":               "backend.jogAxis(3, -1)",
        "JOG_B+":               "backend.jogAxis(4, 1)",
        "JOG_B-":               "backend.jogAxis(4, -1)",
        "JOG_C+":               "backend.jogAxis(5, 1)",
        "JOG_C-":               "backend.jogAxis(5, -1)",
        "JOG_X_STOP":           "backend.stopJog(0)",
        "JOG_Y_STOP":           "backend.stopJog(1)",
        "JOG_Z_STOP":           "backend.stopJog(2)",
        "JOG_A_STOP":           "backend.stopJog(3)",
        "JOG_SPEED_UP":         "backend.incJogSpeed()",
        "JOG_SPEED_DOWN":       "backend.decJogSpeed()",
        "JOG_MODE_CONTINUOUS":  "backend.setJogMode(0)",
        "JOG_MODE_STEP":        "backend.setJogMode(1)",
        "JOG_MODE_MPG":         "backend.setJogMode(2)",
        "JOG_SET_STEP_0":       "backend.setJogStepIndex(0)",
        "JOG_SET_STEP_1":       "backend.setJogStepIndex(1)",
        "JOG_SET_STEP_2":       "backend.setJogStepIndex(2)",
        "JOG_SET_STEP_3":       "backend.setJogStepIndex(3)",
    },

    # ═══════════════════════════════════════════════════
    # ▼ 输入控件 —— 需要 text 的动态 MDI 动作
    # ═══════════════════════════════════════════════════
    "MachTextInput": {
        "--- MDI (动态) ---":   "",
        "MDI_G10_L10":          'backend.submitCommand("G10 L10 Q0 X" + text)',
        "CUSTOM":               "",
    },

    # ═══════════════════════════════════════════════════
    # ▼ 急停 —— 只显示电源相关
    # ═══════════════════════════════════════════════════
    "EmergencyStop": {
        "--- 电源 ---":         "",
        "--- 电源 ---":         "",
        "TOGGLE_POWER":         "backend.togglePowerState()",
        "POWER_ON":             "backend.setMachinePower(1)",
        "POWER_OFF":            "backend.setMachinePower(0)",
        "ESTOP":                "backend.setEstop(1)",
        "ESTOP_RESET":          "backend.setEstop(0)",
        "CLEAR_ALARM":          "backend.clearAlarm()",
    },

    # ═══════════════════════════════════════════════════
    # ▼ Timer —— 定期触发动作
    # ═══════════════════════════════════════════════════
    "Timer": {},  # 继承 ImageButton

    # ═══════════════════════════════════════════════════
    # ▼ 显示类 —— 无动作（LED / FlashLED / Text (DRO) / Text (Label) / GCodeViewer）
    # ═══════════════════════════════════════════════════
    "LED":                 {},
    "FlashLED":            {},
    "Text (DRO)":          {},
    "Text (Label)":        {},
    "GCodeViewer":         {},
    "GCodeGraphics":       {},
    "Rectangle":           {},
    "Slider":              {},
    "HalSlider":           {},
}


STATUS_BINDS = {

    # ═══════════════════════════════════════════════════
    # ▼ 所有控件通用的公用绑定
    # ═══════════════════════════════════════════════════
    "_all": {
        "CUSTOM":               "",
    },

    # ═══════════════════════════════════════════════════
    # ▼ 显示类 —— DRO / Label 需要坐标和状态绑定
    # ═══════════════════════════════════════════════════
    "Text (DRO)": {
        # ── 坐标 ──
        "--- 坐标 ---":         "",
        "displayX":             "backend.displayToolX.toFixed(4)",
        "displayY":             "backend.displayToolY.toFixed(4)",
        "displayZ":             "backend.displayToolZ.toFixed(4)",
        "displayA":             "backend.displayToolA.toFixed(4)",
        "displayB":             "backend.displayToolB.toFixed(4)",
        "displayC":             "backend.displayToolC.toFixed(4)",
        "workOffX":             "backend.workOffsetX.toFixed(4)",
        "workOffY":             "backend.workOffsetY.toFixed(4)",
        "workOffZ":             "backend.workOffsetZ.toFixed(4)",

        # ── 状态 (status) ──
        "--- status ---":       "",
        "st.homedX":            "status.homedX",
        "st.homedY":            "status.homedY",
        "st.homedZ":            "status.homedZ",
        "st.homedA":            "status.homedA",
        "st.isAllHomed":        "status.isAllHomed",
        "st.hasError":          "status.hasError",
        "st.interpIdle":        "status.interpIdle",
        "st.spindleSpeed":      "status.spindleSpeed",
        "st.spindleDir":        "status.spindleDir",
        "st.spindleOverride":   "status.spindleOverride",
        "st.feed":              "status.feed",
        "st.actualFeed":        "status.actualFeed",
        "st.feedOverride":      "status.feedOverride",
        "st.flood":             "status.flood",
        "st.mist":              "status.mist",
        "st.toolInSpindle":     "status.toolInSpindle",
        "st.toolDiameter":      "status.toolDiameter",
        "st.toolOffsetZ":       "status.toolOffsetZ",
        "st.motionLine":        "status.motionLine",
        "st.readLine":          "status.readLine",
        "st.blockDelete":       "status.blockDelete",
        "st.machineMode":       "status.taskMode",
        "st.interpState":       "status.interpState",
        "st.absoluteX":         "status.absoluteX",
        "st.absoluteY":         "status.absoluteY",
        "st.absoluteZ":         "status.absoluteZ",
        "st.machineX":          "status.machineX",
        "st.machineY":          "status.machineY",
        "st.machineZ":          "status.machineZ",

        # ── backend 状态 ──
        "--- backend 状态 ---": "",
        "isRunning":            "backend.machineOn",
        "isTeleop":             "backend.isTeleop",
        "machineMode":          "backend.machineMode",
        "motionType":           "backend.motionType",
        "interpIdle":           "backend.interpIdle",
        "interpState":          "backend.interpState",
        "machineName":          "backend.machineName",
        "maxVelocity":          "backend.maxVelocity",
        "singleBlock":          "backend.singleBlockEnabled",
        "blockDelete":          "backend.blockDelete",
        "spindleDir":           "backend.spindleDir",
        "spindlePercent":       "backend.spindlePercent",
        "spindleLed":           "backend.spindleLedState",
        "feedPercent":          "backend.feedPercent",
        "feedLed":              "backend.feedLedState",

        # ── JOG ──
        "--- JOG ---":          "",
        "jogSpeed":             "backend.jogPercent",
        "jogMode":              "backend.jogMode",
        "jogStep":              "backend.currentJogStep",
        "jogStepIdx":           "backend.jogStepIndex",

        # ── 程序 ──
        "--- 程序 ---":         "",
        "programFile":          "backend.programFile",
        "programName":          "backend.programName",
        "programLines":         "backend.programLines",
        "lineNumber":           "backend.lineNumber",
        "modal":                "backend.modal",
        "timeRunning":          "backend.processingTimeStr",
        "timeTotal":            "backend.totalTimeStr",
        "dateStr":              "backend.dateStr",
        "timeStr":              "backend.timeStr",

        # ── 坐标系 ──
        "--- 坐标系 ---":       "",
        "currentIndex":         "backend.currentIndex",
        "isMachineCoord":       "backend.isMachineCoordActive",
    },

    # ═══════════════════════════════════════════════════
    # ▼ Text (Label) —— 同 DRO 但需要程序相关
    # ═══════════════════════════════════════════════════
    "Text (Label)": {"_inherit":           "LED",
    },

    # ═══════════════════════════════════════════════════
    # ▼ 输入控件 —— 需要坐标 + status 绑定
    # ═══════════════════════════════════════════════════
    "MachTextInput": {
        "--- 坐标 ---":         "",
        "displayX":             "backend.displayToolX.toFixed(4)",
        "displayY":             "backend.displayToolY.toFixed(4)",
        "displayZ":             "backend.displayToolZ.toFixed(4)",
        "displayA":             "backend.displayToolA.toFixed(4)",

        "--- status ---":       "",
        "st.spindleSpeed":      "status.spindleSpeed",
        "st.feed":              "status.feed",
        "st.feedOverride":      "status.feedOverride",
    },

    # ═══════════════════════════════════════════════════
    # ▼ LED / FlashLED —— 状态指示灯绑定
    # ═══════════════════════════════════════════════════
    "LED": {
        "--- status ---":       "",
        "st.homedX":            "status.homedX",
        "st.homedY":            "status.homedY",
        "st.homedZ":            "status.homedZ",
        "st.homedA":            "status.homedA",
        "st.isAllHomed":        "status.isAllHomed",
        "st.hasError":          "status.hasError",
        "st.interpIdle":        "status.interpIdle",
        "st.spindleSpeed":      "status.spindleSpeed",
        "st.flood":             "status.flood",
        "st.mist":              "status.mist",

        "--- 程序 ---":            "",
        "isProgRunning":        "(backend.interpState === 2 || backend.interpState === 4)",
        "isProgPause":          "(backend.interpState === 3)",        

        "--- backend 状态 ---": "",
        "isRunning":            "backend.machineOn",
        "spindleLed":           "backend.spindleLedState",
        "feedLed":              "backend.feedLedState",
        "singleBlock":          "backend.singleBlockEnabled",
        "blockDelete":          "backend.blockDelete",
        "isflood":               "backend.flood",
        "ismist":               "backend.mist",
        "--- 坐标系 ---":       "",
        "currentIndex":         "backend.currentIndex",
        "isMachineCoord":       "backend.isMachineCoordActive",        
    },

    "FlashLED": {"_inherit":           "LED",
    },

    # ═══════════════════════════════════════════════════
    # ▼ 无绑定的控件
    # ═══════════════════════════════════════════════════
    "ImageButton":          {},
    "SpriteButton":         {},
    "JOGButton":            {},
    "EmergencyStop":        {},
    "Timer":                {},
    "TextField":            {},
    "Rectangle":            {},
    "GCodeViewer":          {},
    "GCodeGraphics":        {},
    "Slider":               {},
    "HalSlider":            {},
    "ComboBox":             {},
}


# ═══════════════════════════════════════════════════════
#  查找函数
# ═══════════════════════════════════════════════════════
#
#  规则:
#    1. 你在 ACTIONS / STATUS_BINDS 里注册了某控件 → 只显示你注册的条目
#       （空 {} = 继承 _FALLBACK_ACTION 的动作，绑定则为空）
#    2. 你未注册某控件 → 自动获得全部动作 / 全部绑定（不限制）
#
#  这意味着：你想限制一个控件就注册它，不限制就不用管，
#  新控件天生就有全部选项，不会"给定死"。
# ═══════════════════════════════════════════════════════

_FALLBACK_ACTION = "ImageButton"   # 空 { } 继承谁的动作


def get_actions(ctype=None):
    """返回指定控件类型的扁平动作字典。

    未注册的 ctype → 返回所有动作（不限制）。
    空 {} 的 ctype → 继承 _FALLBACK_ACTION 的动作列表。
    """
    if ctype and ctype in ACTIONS:
        sub = ACTIONS[ctype]
        result = dict(ACTIONS.get("_all", {}))
        if not sub:
            sub = ACTIONS.get(_FALLBACK_ACTION, {})
        result.update(sub)
        return result

    # 未注册 → 返回全部
    return _build_all_actions()


def get_binds(ctype=None):
    """返回指定控件类型的扁平绑定字典。

    未注册的 ctype → 返回所有绑定（不限制）。
    支持 {"_inherit": "ParentType"} 继承父控件的绑定。
    """
    if ctype and ctype in STATUS_BINDS:
        result = dict(STATUS_BINDS.get("_all", {}))
        _resolve_bind_inherit(result, ctype)
        return result

    # 未注册 → 返回全部
    return _build_all_binds()


def _resolve_bind_inherit(result, ctype, visited=None):
    """递归解析 _inherit 链，合并父控件的绑定到 result 中。"""
    if visited is None:
        visited = set()
    if ctype in visited:
        return  # 防止循环引用
    visited.add(ctype)

    sub = STATUS_BINDS.get(ctype, {})
    parent = sub.get("_inherit") if isinstance(sub, dict) else None

    # 先合并父级（深度优先）
    if parent and parent in STATUS_BINDS:
        _resolve_bind_inherit(result, parent, visited)

    # 再合并自己的条目（排除 _inherit 本身）
    for k, v in sub.items():
        if k != "_inherit":
            result[k] = v


def get_all_actions():
    """同 _build_all_actions，向后兼容别名。"""
    return _build_all_actions()


def get_all_binds():
    """同 _build_all_binds，向后兼容别名。"""
    return _build_all_binds()


def _build_all_actions():
    """全量动作合并。"""
    result = dict(ACTIONS.get("_all", {}))
    fallback = ACTIONS.get(_FALLBACK_ACTION, {})
    for k, v in ACTIONS.items():
        if k in ("_all", _FALLBACK_ACTION):
            continue
        result.update(fallback if not v else v)
    return result


def _build_all_binds():
    """全量绑定合并（含 _inherit 继承）。"""
    result = dict(STATUS_BINDS.get("_all", {}))
    for ctype in STATUS_BINDS:
        if ctype == "_all":
            continue
        _resolve_bind_inherit(result, ctype)
    return result
