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
QmlVcp Builder — CNC 界面可视化拼装工具

基于 PyQt5 (LinuxCNC 原生环境), 零额外依赖即可运行。
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from lang import Tr

# 默认英文（代码 fallback 即英文），如需中文请改为 Tr.load("zh_CN")
Tr.load("zh_CN")

from builder.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft YaHei", 14))

    # 加载全局样式表
    qss_path = os.path.join(os.path.dirname(__file__), "builder", "mainwindow.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    win = MainWindow()
    win.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
