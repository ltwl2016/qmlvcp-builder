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
qmlvcp 框架一键初始化
=====================
用户只需创建 Backend 实例，调用 init_qmlvcp() 即可完成所有框架层的初始化。
"""

import os
from PySide6.QtCore import QTimer
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

from qmlvcp.core.hal_manager import HalManager
from qmlvcp.core.gcode_graphics import AxesGeometry, BoundsGeometry, TrajectoryGeometry, LiveTrajectoryGeometry


def init_qmlvcp(
    engine: QQmlApplicationEngine,
    parent_dir: str,
    backend,
    project_dir: str = "",
    hal_comp_name: str = "qmlvcp",
) -> HalManager:
    """
    一键初始化 qmlvcp 框架的所有运行时依赖：
      1. 注册 QML 导入路径
      2. 注入 status / command / jog / hal / assetsDir 到 QML 上下文
      3. 注册 4 个 C++ Geometry 类型（GCodeGraphics 依赖）
      4. 创建并返回 HalManager

    参数:
        engine:         QQmlApplicationEngine 实例
        parent_dir:     qmlvcp 的父目录（例如 /media/cnc/mydisk）
        backend:        项目 Backend 实例（必须含 cnc_status / cnc_command / jog_controller）
        project_dir:    项目根目录（含 assets/ 和 qml/，默认自动推断）
        hal_comp_name:  HAL 组件名，默认 "qmlvcp"

    返回:
        HalManager 实例（调用方负责后续 .ready(ini_path) 调用）
    """
    # ── 1. QML 导入路径 ──
    qml_import_path = os.path.join(parent_dir, "qmlvcp", "qml")
    engine.addImportPath(qml_import_path)

    # ── 2. 上下文属性注入 ──
    ctx = engine.rootContext()
    ctx.setContextProperty("backend", backend)
    ctx.setContextProperty("status",  backend.cnc_status)
    ctx.setContextProperty("command", backend.cnc_command)
    ctx.setContextProperty("jog",     backend.jog_controller)

    # HAL 管理器
    hal_manager = HalManager(comp_name=hal_comp_name)
    ctx.setContextProperty("hal", hal_manager)

    # 资源目录（供 QML 中 assetsDir 引用）
    from PySide6.QtCore import QUrl
    if not project_dir:
        # 自动推断：取 backend 模块文件所在目录
        import inspect
        backend_file = inspect.getfile(type(backend))
        project_dir = os.path.dirname(os.path.abspath(backend_file))
    ctx.setContextProperty("assetsDir", QUrl.fromLocalFile(project_dir))

    # ── 3. 注册 C++ Geometry 类型（GCodeGraphics 依赖） ──
    qmlRegisterType(AxesGeometry, "QmlVcp", 1, 0, "AxesGeometry")
    qmlRegisterType(BoundsGeometry, "QmlVcp", 1, 0, "BoundsGeometry")
    qmlRegisterType(TrajectoryGeometry, "QmlVcp", 1, 0, "TrajectoryGeometry")
    qmlRegisterType(LiveTrajectoryGeometry, "QmlVcp", 1, 0, "LiveTrajectoryGeometry")

    return hal_manager
