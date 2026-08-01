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
qmlvcp JogController —— 通用 JOG 控制器

封装连续(CONTINUOUS) / 步进(STEP) / 手轮(MPG) 三种点动模式，
速度百分比、步距选择等全部逻辑下沉至此，供任何 QML 界面复用。
"""
from PySide6.QtCore import QObject, Signal, Property, Slot

DEFAULT_MAX_VELOCITY = 60.0       # mm/s, 默认最大点动速度
DEFAULT_STEP_SIZES   = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]


class JogController(QObject):
    """通用 JOG 控制器，负责向 LinuxCNC Command 下发点动指令。"""

    jogChanged = Signal()

    def __init__(self, command, status, config=None, parent=None):
        super().__init__(parent)
        self._cmd    = command
        self._status = status
        self._max_velocity = (
            getattr(config, 'default_jog_velocity', DEFAULT_MAX_VELOCITY)
            if config else DEFAULT_MAX_VELOCITY
        )
        self._increments = (
            list(getattr(config, 'increments', DEFAULT_STEP_SIZES))
            if config else list(DEFAULT_STEP_SIZES)
        )
        self._percent    = 100.0
        self._mode       = 0    # 0: continuous, 1: step, 2: MPG
        self._step_idx   = 2    # 默认 0.1 mm

    # ================================================================
    # Properties (QML 可直接绑定)
    # ================================================================
    @Property(float, notify=jogChanged)
    def jogPercent(self) -> float:
        return self._percent

    @jogPercent.setter
    def jogPercent(self, value: float) -> None:
        value = max(1.0, min(100.0, float(value)))
        if value != self._percent:
            self._percent = value
            self.jogChanged.emit()

    @Property(int, notify=jogChanged)
    def jogMode(self) -> int:
        return self._mode

    @Property(int, notify=jogChanged)
    def jogStepIndex(self) -> int:
        return self._step_idx

    @Property(float, notify=jogChanged)
    def currentJogStep(self) -> float:
        if 0 <= self._step_idx < len(self._increments):
            return self._increments[self._step_idx]
        return 0.0

    # ================================================================
    # Slots
    # ================================================================
    @Slot(int, int)
    def jog(self, axis_index: int, direction: int) -> None:
        """执行一次点动（按下方向键/按钮时调用）。"""
        if not hasattr(self._cmd, 'jog'):
            return

        speed = self._max_velocity * (self._percent / 100.0) * direction
        if speed == 0:
            speed = 10.0 * direction

        distance = 0.0
        if self._mode == 1:
            distance = self.currentJogStep
        elif self._mode == 2:
            return

        is_teleop = self._status.isTeleop
        self._cmd.jog(axis_index, speed, distance=distance, is_teleop=is_teleop)

    @Slot(int)
    def jogStop(self, axis_index: int) -> None:
        """停止指定轴的点动（松开方向键/按钮时调用）。"""
        is_teleop = self._status.isTeleop
        if hasattr(self._cmd, 'stopJog'):
            self._cmd.stopJog(axis_index, is_teleop=is_teleop)
        else:
            self._cmd.jog(axis_index, 0.0, distance=0.0, is_teleop=is_teleop)

    @Slot()
    def incSpeed(self) -> None:
        self._percent = min(100.0, self._percent + 5.0)
        self.jogChanged.emit()

    @Slot()
    def decSpeed(self) -> None:
        self._percent = max(1.0, self._percent - 5.0)
        self.jogChanged.emit()

    @Slot(int)
    def setMode(self, mode: int) -> None:
        self._mode = mode
        self.jogChanged.emit()

    @Slot(int)
    def setSpeed(self, percent: int) -> None:
        self._percent = max(1.0, min(100.0, float(percent)))
        self.jogChanged.emit()

    @Slot(int)
    def setStepIndex(self, index: int) -> None:
        if 0 <= index < len(self._increments):
            self._step_idx = index
            self.jogChanged.emit()
