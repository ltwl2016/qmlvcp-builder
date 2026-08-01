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
qmlvcp 最小示例 — 复刻你的自定义 CNC 界面从这里开始。

目录结构:
    my-cnc/
    ├── main.py          ← 本文件
    ├── backend.py       ← 项目业务逻辑（坐标系/安全位/自定义功能）
    ├── qml/
    │   ├── Main.qml     ← 主界面
    │   └── qmldir        ← 只注册项目专属组件（Theme/页面等）
    └── assets/          ← 你的贴图素材

运行:
    python main.py                     # 独立运行
    python main.py -ini /path/to/ini   # 接 LinuxCNC
"""

from __future__ import annotations

import os, sys

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
sys.path.insert(0, parent_dir)

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QGuiApplication, QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine

from backend import Backend
from qmlvcp.core.config import Config
from qmlvcp.core.setup import init_qmlvcp


def main():
    # ── 可选：解析 LinuxCNC -ini 参数 ──
    ini_path = ""
    for i, arg in enumerate(sys.argv):
        if arg == "-ini" and i + 1 < len(sys.argv):
            ini_path = sys.argv[i + 1]
            break

    # ── 抗锯齿 ──
    fmt = QSurfaceFormat()
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # ── 创建后端（你的业务逻辑写在这里） ──
    config = Config(ini_path)
    backend = Backend(config)

    # ── 框架一键初始化（自动处理: import路径/上下文注入/Geometry注册/HAL管理） ──
    hal = init_qmlvcp(engine, parent_dir, backend, project_dir=base_dir)

    # ── （可选）键盘快捷键 ──
    # from qmlvcp.core.keyboard import GlobalKeyFilter
    # key_filter = GlobalKeyFilter(backend, "hotkeys.ini", app)
    # app.installEventFilter(key_filter)

    # ── 加载界面 ──
    qml_file = os.path.join(base_dir, "qml", "Main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    # ── 锁定 HAL 组件 ──
    QTimer.singleShot(500, lambda: hal.ready(ini_path))

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
