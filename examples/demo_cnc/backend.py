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
Demo CNC Backend — 展示如何在导出项目中添加自定义业务逻辑。

写你自己的 Backend 时，只需:
    1. 继承 QObject
    2. 用 @Property 暴露数据给 QML 绑定
    3. 用 @Slot 暴露方法给 QML 调用
    4. 通过 self.cnc_status / self.cnc_command 与 LinuxCNC 交互
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from qmlvcp.core.status import Status
from qmlvcp.core.command import Command
from qmlvcp.core.jog_controller import JogController
from qmlvcp.core.override_manager import OverrideManager
from qmlvcp.core.runtime_tracker import RuntimeTracker


class Backend(QObject):
    """演示用 Backend — 替换为你自己的 CNC 逻辑"""

    # ── 信号（属性变更时发射，QML 自动刷新） ──
    coordsChanged = Signal()
    statusChanged = Signal()
    spindleChanged = Signal()
    toolChanged = Signal()

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self._config = config
        self._machine_name = config.machine_name if config else "Demo CNC"

        # ── 核心组件（框架自动管理） ──
        self.cnc_status      = Status(config=config, parent=self)
        self.cnc_command     = Command(self)
        self.jog_controller  = JogController(self.cnc_command, self.cnc_status, config)
        self.override_mgr    = OverrideManager(self.cnc_command, self.cnc_status)
        self.runtime_tracker = RuntimeTracker(self.cnc_status)

        # ── 信号中继：状态变化 → QML 更新 ──
        self.cnc_status.positionChanged.connect(self.coordsChanged.emit)
        self.cnc_status.homedChanged.connect(self.coordsChanged.emit)
        self.cnc_status.stateChanged.connect(self.statusChanged.emit)
        self.cnc_status.spindleSpeedChanged.connect(self.spindleChanged.emit)
        self.cnc_status.toolChanged.connect(self.toolChanged.emit)

        # ── 自定义属性初始化 ──
        self._my_counter = 0

    # ==================================================================
    # DRO 坐标（直接委托 Status，QML 绑定 backend.displayX 即可）
    # ==================================================================
    @Property(float, notify=coordsChanged)
    def displayX(self): return self.cnc_status.machineX

    @Property(float, notify=coordsChanged)
    def displayY(self): return self.cnc_status.machineY

    @Property(float, notify=coordsChanged)
    def displayZ(self): return self.cnc_status.machineZ

    @Property(float, notify=coordsChanged)
    def displayA(self): return self.cnc_status.machineA

    # ==================================================================
    # 机床状态（QML 展示状态灯、文字）
    # ==================================================================
    @Property(str, notify=statusChanged)
    def machineState(self):
        """返回当前状态中文描述"""
        states = {
            "ESTOP":  "急停",
            "ESTOP_RESET": "急停复位",
            "OFF":    "断电",
            "ON":     "就绪",
        }
        return states.get(self.cnc_status.state, self.cnc_status.state)

    @Property(str, constant=True)
    def machineName(self): return self._machine_name

    # ==================================================================
    # 主轴信息
    # ==================================================================
    @Property(float, notify=spindleChanged)
    def spindleSpeed(self): return self.cnc_status.spindleSpeed

    @Property(str, notify=spindleChanged)
    def spindleDir(self):
        return "正转" if self.cnc_status.spindleDirection > 0 else ("反转" if self.cnc_status.spindleDirection < 0 else "停止")

    # ==================================================================
    # 自定义 Slot — QML 按钮点击后调用的方法
    # ==================================================================
    @Slot(int, int)
    def jogAxis(self, axis_index, direction):
        """JOG 控制：axis_index 0=X 1=Y 2=Z, direction 1=正 0=停 -1=负"""
        self.jog_controller.jog(axis_index, direction)

    @Slot()
    def homeAll(self):
        """全部轴回零"""
        self.cnc_command.homeAll()

    @Slot()
    def cycleStart(self):
        """启动程序"""
        self.cnc_command.cycleStart()

    @Slot()
    def cycleStop(self):
        """停止程序"""
        self.cnc_command.cycleStop()

    @Slot()
    def emergencyStop(self):
        """急停"""
        self.cnc_command.estop()

    @Slot()
    def machineOn(self):
        """上电"""
        self.cnc_command.machineOn()

    @Slot(int)
    def setSpindleSpeed(self, rpm: int):
        """设定主轴转速"""
        self.cnc_command.setSpindleSpeed(rpm)

    @Slot(int)
    def setFeedOverride(self, percent: int):
        """设置进给倍率"""
        self.cnc_command.setFeedOverride(percent / 100.0)

    # ==================================================================
    # 自定义业务属性示例
    # ==================================================================
    @Property(int, notify=statusChanged)
    def customCounter(self):
        return self._my_counter

    @Slot()
    def incrementCounter(self):
        self._my_counter += 1
        self.statusChanged.emit()
