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
qmlvcp RuntimeTracker —— 加工计时器

每秒更新日期/时间/加工用时/总运行用时，自动监听 Status.interpState。
"""
from datetime import datetime
from PySide6.QtCore import QObject, QTimer, Property, Signal


class RuntimeTracker(QObject):
    """通用加工计时器。"""

    timeChanged = Signal()

    def __init__(self, status, parent=None):
        super().__init__(parent)
        self._st = status
        self._run_seconds = 0
        self._total_seconds = 0
        self._last_interp = 1
        self._date_str = ""
        self._time_str = ""

        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self._tick)
        self._clock.start()
        self._tick()  # 立即初始化

    # ================================================================
    # 内部逻辑
    # ================================================================
    def _tick(self) -> None:
        now = datetime.now()
        wd = ["一", "二", "三", "四", "五", "六", "日"]
        self._date_str = f"{now:%Y-%m-%d} 星期{wd[now.weekday()]}"
        self._time_str = f"{now:%H:%M:%S}"

        self._total_seconds += 1
        current = getattr(self._st, 'interpState', 1)
        # 从空闲转入运行或等待 → 重置加工用时
        if current in (2, 4) and self._last_interp == 1:
            self._run_seconds = 0
        if current in (2, 4):
            self._run_seconds += 1
        self._last_interp = current

        self.timeChanged.emit()

    # ================================================================
    # Properties
    # ================================================================
    @Property(str, notify=timeChanged)
    def processingTimeStr(self) -> str:
        m = self._run_seconds // 60
        s = self._run_seconds % 60
        return f"{m:02d}:{s:02d}"

    @Property(str, notify=timeChanged)
    def totalTimeStr(self) -> str:
        h = self._total_seconds // 3600
        m = (self._total_seconds % 3600) // 60
        s = self._total_seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @Property(str, notify=timeChanged)
    def dateStr(self) -> str:
        return self._date_str

    @Property(str, notify=timeChanged)
    def timeStr(self) -> str:
        return self._time_str
