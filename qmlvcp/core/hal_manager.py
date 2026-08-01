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
qmlVCP HAL Manager
动态硬件抽象层管理桥接器
允许 QML 前端在加载时按需生成对应的 HAL 引脚。
"""
from __future__ import annotations
from PySide6.QtCore import QObject, Slot, Signal, QTimer, Property

try:
    import hal
    HAS_HAL = True
except Exception as e:
    print(f"[qmlVCP HalManager] import hal 失败: {e}")
    HAS_HAL = False


class HalManager(QObject):
    # 当 IN 引脚的值在底层发生改变时，通知 QML
    pinChanged = Signal(str, "QVariant")
    # 当跨组件的全局 System 引脚改变时，通知 QML (防止前端自己 import hal)
    sysPinChanged = Signal(str, "QVariant")

    def __init__(self, comp_name: str = "qmlvcp", parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.comp_name = comp_name
        
        self.h = None
        self._ready = False
        
        if HAS_HAL:
            try:
                self.h = hal.component(self.comp_name)
            except Exception as e:
                print(f"[qmlVCP HalManager] 创建组件失败: {e}")
                self.h = None

        # 用于存储我们创建的引脚
        self._pins = {}
        # 用于存储用户请求监控的全局独立引脚 (不属于我们创建的)
        self._watched_sys_pins = {}
        
        # 轮询定时器，用于检测 IN 引脚变化
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(50)
        self.poll_timer.timeout.connect(self._poll_in_pins)

    @Slot(str, str, str)
    def addPin(self, name: str, hal_type: str, direction: str) -> None:
        """
        供 QML 调用的注册引脚方法
        :param name: 引脚名称 (如 "btn-x-jog")
        :param hal_type: "bit", "float", "s32", "u32"
        :param direction: "in", "out"
        """
        if self.h is None:
            print(f"[qmlVCP HalManager] (模拟) 请求注册引脚: {name} ({hal_type} {direction})")
            self._pins[name] = {"type": hal_type, "dir": direction, "value": 0}
            return

        if self._ready:
            print(f"[qmlVCP HalManager] 错误: HAL 组件已就绪，无法动态添加引脚 {name}")
            return

        if name in self._pins:
            return  # 已经注册过

        type_map = {
            "bit": hal.HAL_BIT,
            "float": hal.HAL_FLOAT,
            "s32": hal.HAL_S32,
            "u32": hal.HAL_U32
        }
        dir_map = {
            "in": hal.HAL_IN,
            "out": hal.HAL_OUT
        }
        
        t = type_map.get(hal_type.lower())
        d = dir_map.get(direction.lower())
        
        if t is not None and d is not None:
            try:
                self.h.newpin(name, t, d)
                self._pins[name] = {"type": hal_type, "dir": direction, "value": 0}
                print(f"[qmlVCP HalManager] 成功注册引脚: {self.comp_name}.{name}")
            except Exception as e:
                print(f"[qmlVCP HalManager] 注册引脚 {name} 失败: {e}")

    @Slot(str, "QVariant")
    def setPin(self, name: str, value: any) -> None:
        """设置 OUT 引脚的值"""
        if self.h is None:
            # 模拟模式下只是记录
            if name in self._pins:
                self._pins[name]["value"] = value
                print(f"[qmlVCP HalManager] (模拟) 设置引脚 {name} = {value}")
            return
            
        if name in self._pins and self._pins[name]["dir"].lower() == "out":
            try:
                self.h[name] = value
                self._pins[name]["value"] = value
            except Exception as e:
                print(f"[qmlVCP HalManager] 设置引脚 {name} 失败: {e}")

    @Slot(str, result="QVariant")
    def getPin(self, name: str) -> any:
        """读取引脚的值"""
        if self.h is None:
            return self._pins.get(name, {}).get("value", 0)
            
        if name in self._pins:
            try:
                return self.h[name]
            except Exception:
                return 0
        return 0

    @Slot(str)
    def watchSysPin(self, name: str) -> None:
        """注册一个非本组件生成的外部全局引脚进行高频轮询监听，结果发送至 sysPinChanged"""
        if name not in self._watched_sys_pins:
            self._watched_sys_pins[name] = {"value": None}
            print(f"[qmlVCP HalManager] 已开启对全局底层引脚的监控: {name}")

    def ready(self, ini_path: str = "") -> None:
        """组件锁死，声明就绪; 并同步拉起对应外接配置文件"""
        if self.h is not None and not self._ready:
            try:
                self.h.ready()
                self._ready = True
                self.poll_timer.start()
                print(f"[qmlVCP HalManager] HAL 组件 '{self.comp_name}' 成功就绪！")
                
                # 绝对路径 + 铁血崩溃模式：任何一行接线错误都瞬间闪退，不带病运行
                if ini_path:
                    import subprocess
                    import os
                    import sys
                    if os.path.exists(ini_path):
                        import linuxcnc
                        inifile = linuxcnc.ini(ini_path)
                        ini_dir = os.path.dirname(os.path.abspath(ini_path))
                        for f in inifile.findall("HAL", "POSTGUI_HALFILE"):
                            hal_file_path = os.path.join(ini_dir, f)
                            try:
                                subprocess.run(['halcmd', '-f', hal_file_path], capture_output=True, text=True, check=True)
                                print(f"[qmlVCP HalManager] 同步连线: 已成功加载 PostGUI - {hal_file_path}")
                            except subprocess.CalledProcessError as pe:
                                error_msg = f"PostGUI ({hal_file_path}) 挂载失败！底层详细报错排查：\n\n{pe.stderr}\n\n请修改 .hal 文件内的语法或连线后，重新启动系统！"
                                
                                # 将详细的底层报错打印到终端，以防非图形环境
                                print(f"[致命错误] {error_msg}")

                                # 使用底层的 Tkinter 发出唯一弹窗
                                import tkinter as tk
                                from tkinter import messagebox
                                try:
                                    tk_root = tk.Tk()
                                    tk_root.withdraw()
                                    tk_root.attributes('-topmost', True)
                                    messagebox.showerror("HAL 接线或语法致命错误", error_msg)
                                    tk_root.destroy()
                                except:
                                    pas
                                import sys
                                sys.exit(0)
            except Exception as e:
                print(f"[qmlVCP HalManager] 就绪过程抛出异常: {e}")

    def _poll_in_pins(self) -> None:
        """轮询所有 IN 引脚，有变化则触发信号"""
        if self.h is None or not self._ready:
            return
            
        for name, p in self._pins.items():
            if p["dir"].lower() == "in":
                try:
                    current_val = self.h[name]
                    if current_val != p["value"]:
                        p["value"] = current_val
                        self.pinChanged.emit(name, current_val)
                except:
                    pass
                    
        # 补充：轮询被跨组件挂载监控的 System 游离引脚
        if getattr(self, '_watched_sys_pins', None):
            for sys_name, sys_p in self._watched_sys_pins.items():
                try:
                    sys_val = hal.get_value(sys_name)
                    if sys_val != sys_p["value"]:
                        sys_p["value"] = sys_val
                        self.sysPinChanged.emit(sys_name, sys_val)
                except:
                    pass
