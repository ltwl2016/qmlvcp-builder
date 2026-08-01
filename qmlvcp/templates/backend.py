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
qmlvcp 项目 Backend — 所有项目专属业务逻辑写在这里。

框架已自动注入以下 QML 上下文属性:
    status   — 机床实时状态 (位置/速度/模式/报警...)
    command  — 指令下发 (JOG/MDI/程序控制...)
    jog      — JOG 控制器 (速度/步距/模式)
    hal      — HAL 引脚管理
    backend  — 本类实例 (你的自定义属性/Slot)
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from qmlvcp.core.status import Status
from qmlvcp.core.command import Command
from qmlvcp.core.jog_controller import JogController
from qmlvcp.core.override_manager import OverrideManager
from qmlvcp.core.runtime_tracker import RuntimeTracker


class Backend(QObject):
    """项目 Backend — 继承 QObject，暴露 Property/Slot 供 QML 绑定。"""

    # ── 信号 ──
    systemsChanged = Signal()
    machineChanged = Signal()
    feedChanged = Signal()
    spindleChanged = Signal()
    toolChanged = Signal()
    timeChanged = Signal()

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self._config = config
        self._machine_name = config.machine_name if config else "未命名"

        # ── 框架核心组件（自动创建，自动注入 QML） ──
        self.cnc_status    = Status(config=config, parent=self)
        self.cnc_command   = Command(self)
        self.jog_controller   = JogController(self.cnc_command, self.cnc_status, config)
        self.override_mgr     = OverrideManager(self.cnc_command, self.cnc_status)
        self.runtime_tracker  = RuntimeTracker(self.cnc_status)

        # ── 信号中继 ──
        self.cnc_status.positionChanged.connect(self.systemsChanged.emit)
        self.cnc_status.homedChanged.connect(self.systemsChanged.emit)
        self.jog_controller.jogChanged.connect(self.machineChanged.emit)
        self.runtime_tracker.timeChanged.connect(self.timeChanged.emit)

        # ── 你的自定义初始化 ──
        self._my_custom_value = 0

    # ==================================================================
    # 以下是示例：展示如何添加自定义 Property 和 Slot
    # ==================================================================

    # ── 坐标属性（框架 Status 已内置 machineX / absoluteX 等，直接委托） ──
    @Property(float, notify=systemsChanged)
    def displayToolX(self): return self.cnc_status.machineX

    @Property(float, notify=systemsChanged)
    def displayToolY(self): return self.cnc_status.machineY

    @Property(float, notify=systemsChanged)
    def displayToolZ(self): return self.cnc_status.machineZ

    # ── 自定义业务 Slot ──
    @Slot(int, int)
    def jogAxis(self, axis_index, direction):
        """QML 方向键 → JOG 控制器"""
        self.jog_controller.jog(axis_index, direction)

    @Slot()
    def togglePowerState(self):
        """急停/上电时序 — 你的机床特有逻辑写这里"""
        pass

    # ── 只读属性（QML 直接绑定） ──
    @Property(str, constant=True)
    def machineName(self): return self._machine_name

    @Property(float, notify=machineChanged)
    def jogPercent(self): return self.jog_controller.jogPercent

    @Property(str, notify=timeChanged)
    def processingTimeStr(self): return self.runtime_tracker.processingTimeStr
