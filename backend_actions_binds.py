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
#  基于新 backend.py 模板的所有可用动作和绑定
#  格式与 controls.py 的 ACTIONS / STATUS_BINDS 完全一致
# ───────────────────────────────────────────────────

ACTIONS = {
    "═══ 以下为新增动作 ═══": "",
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
    "GOTO_SAFE_Z":          "backend.gotoSafeZ()",
    "GOTO_XY_ZERO":         "backend.gotoXYZero()",

    # ── JOG 点动 ──
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

    # ── MDI ──
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

    # ── 杂项 ──
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
    "CUSTOM":               "",
}

STATUS_BINDS = {
    "═══ 以下为新增绑定 ═══": "",
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

    # ── JOG ──
    "--- JOG ---":          "",
    "jogSpeed":             "backend.jogPercent",
    "jogMode":              "backend.jogMode",
    "jogStep":              "backend.currentJogStep",
    "jogStepIdx":           "backend.jogStepIndex",

    # ── 坐标系选择 ──
    "--- 坐标系 ---":       "",
    "currentIndex":         "backend.currentIndex",
    "isMachineCoord":       "backend.isMachineCoordActive",
}
