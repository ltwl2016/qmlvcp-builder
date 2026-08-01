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
