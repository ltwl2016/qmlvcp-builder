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
Demo CNC - QmlVcp Builder 导出项目示例

使用方法:
    python main.py                     # 独立预览（无机床连接）
    python main.py -ini linuxcnc.ini   # 连接 LinuxCNC 运行
"""

from __future__ import annotations

import os, sys

base_dir = os.path.dirname(os.path.abspath(__file__))
# 上溯两级到项目根目录（demo_cnc → examples → 项目根），才能找到 qmlvcp 包
root_dir = os.path.dirname(os.path.dirname(base_dir))
sys.path.insert(0, root_dir)

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QGuiApplication, QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine

from backend import Backend
from qmlvcp.core.config import Config
from qmlvcp.core.setup import init_qmlvcp


def main():
    ini_path = ""
    for i, arg in enumerate(sys.argv):
        if arg == "-ini" and i + 1 < len(sys.argv):
            ini_path = sys.argv[i + 1]
            break

    fmt = QSurfaceFormat()
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    config = Config(ini_path)
    backend = Backend(config)

    hal = init_qmlvcp(engine, parent_dir, backend, project_dir=base_dir)

    qml_file = os.path.join(base_dir, "qml", "Main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    QTimer.singleShot(500, lambda: hal.ready(ini_path))

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
