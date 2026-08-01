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
qmlvcp OverrideManager —— 通用倍率管理器

封装进给/主轴倍率的增减/复位逻辑及 LED 状态计算。
"""
from PySide6.QtCore import QObject, Signal, Property, Slot


class OverrideManager(QObject):
    """通用倍率管理，连接 Status 信号自动通知 QML 刷新。"""

    overrideChanged = Signal()

    def __init__(self, command, status, parent=None):
        super().__init__(parent)
        self._cmd = command.cmd  # linuxcnc.command() 原生通道
        self._st  = status

        # 监听 LinuxCNC 状态变化，自动通知 QML
        self._st.feedChanged.connect(self.overrideChanged.emit)
        self._st.spindleChanged.connect(self.overrideChanged.emit)

    # ================================================================
    # Properties
    # ================================================================
    @Property(float, notify=overrideChanged)
    def feedPercent(self) -> float:
        return self._st.feedOverride * 100.0

    @Property(int, notify=overrideChanged)
    def spindlePercent(self) -> int:
        return int(self._st.spindleOverride * 100.0)

    @Property(int, notify=overrideChanged)
    def feedLedState(self) -> int:
        """0=off, 1=solid, 2=blinking"""
        if self._st.actualFeed <= 0:
            return 0
        ov = self._st.feedOverride
        if ov > 1.001 or ov < 0.999:
            return 2
        return 1

    @Property(int, notify=overrideChanged)
    def spindleLedState(self) -> int:
        """0=off, 1=solid, 2=blinking"""
        if self._st.spindleDir == 0:
            return 0
        ov = self._st.spindleOverride
        if ov > 1.001 or ov < 0.999:
            return 2
        return 1

    # ================================================================
    # Slots
    # ================================================================
    @Slot(int)
    def setFeed(self, percent: int) -> None:
        self._cmd.feedrate(percent / 100.0)

    @Slot()
    def incFeed(self) -> None:
        self._cmd.feedrate(self._st.feedOverride + 0.1)

    @Slot()
    def decFeed(self) -> None:
        self._cmd.feedrate(max(0.0, self._st.feedOverride - 0.1))

    @Slot()
    def resetFeed(self) -> None:
        self._cmd.feedrate(1.0)

    @Slot(int)
    def setSpindle(self, percent: int) -> None:
        self._cmd.spindleoverride(percent / 100.0)

    @Slot()
    def incSpindle(self) -> None:
        current = int(self._st.spindleOverride * 100)
        self._cmd.spindleoverride(min(200, current + 10) / 100.0)

    @Slot()
    def decSpindle(self) -> None:
        current = int(self._st.spindleOverride * 100)
        self._cmd.spindleoverride(max(10, current - 10) / 100.0)
