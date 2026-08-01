"""
QmlVcp Builder — CNC 界面可视化拼装工具

基于 PyQt5 (LinuxCNC 原生环境), 零额外依赖即可运行。
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
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
