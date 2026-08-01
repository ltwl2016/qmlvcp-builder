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

import os

class Config:
    """
    qmlVCP 配置读取器。
    负责读取 LinuxCNC 的 .ini 文件，将其封装为面向对象的配置项。
    严格执行 qmlVCP 核心业务逻辑分离的原则。
    """
    def __init__(self, ini_path=None):
        self.ini_path = ini_path
        
        # 提取全局基础绝对路径，作为未来全系统所有文件读写的统一锚点接口
        if ini_path and os.path.exists(ini_path):
            self.base_dir = os.path.abspath(os.path.dirname(ini_path))
        else:
            self.base_dir = os.path.abspath(os.getcwd())
        
        # 默认回退配置
        self.machine_name = "脱机模拟机床"
        self.max_velocity = 0.0
        self.linear_units = "mm"
        self.axes = ['X', 'Y', 'Z']
        self.default_jog_velocity = 10.0
        self.log_file = None
        
        # 默认机床行程边界
        self.min_limit_x = 0.0
        self.max_limit_x = 500.0
        self.min_limit_y = 0.0
        self.max_limit_y = 500.0
        self.min_limit_z = 0.0
        self.max_limit_z = 300.0
        
        if ini_path and os.path.exists(ini_path):
            try:
                import linuxcnc
                inifile = linuxcnc.ini(ini_path)
                
                name = inifile.find("EMC", "MACHINE")
                if name: self.machine_name = name
                
                # 1. 尝试读取 DISPLAY 里的点动默认速度
                jog_vel = inifile.find("DISPLAY", "DEFAULT_LINEAR_VELOCITY")
                if jog_vel: 
                    self.default_jog_velocity = float(jog_vel)
                else:
                    self.default_jog_velocity = 0.0

                # 2. 提取系统物理极速 (严格的查找顺序：DISPLAY -> TRAJ -> AXIS_X)
                vel = inifile.find("DISPLAY", "MAX_LINEAR_VELOCITY")
                if not vel:
                    vel = inifile.find("TRAJ", "MAX_LINEAR_VELOCITY")
                if not vel:
                    vel = inifile.find("TRAJ", "MAX_VELOCITY")
                if not vel:
                    vel = inifile.find("AXIS_X", "MAX_VELOCITY")
                
                if vel: 
                    self.max_velocity = float(vel)
                    
                units = inifile.find("TRAJ", "LINEAR_UNITS")
                if units: self.linear_units = units
                
                coords = inifile.find("TRAJ", "COORDINATES")
                if coords:
                    self.axes = [char for char in coords.upper() if char.isalpha()]
                    
                log_path = inifile.find("DISPLAY", "LOG_FILE")
                if log_path:
                    # 在配置器层面就把原生路径彻底“洗”成不受系统限制的绝对真实路径，作为标准对外接口
                    self.log_file = os.path.abspath(os.path.expanduser(log_path))
                    
                # 3. 读取行程边界 (MIN_LIMIT, MAX_LIMIT)
                for axes_sec, prefix in [("AXIS_X", "x"), ("AXIS_Y", "y"), ("AXIS_Z", "z")]:
                    min_val = inifile.find(axes_sec, "MIN_LIMIT")
                    max_val = inifile.find(axes_sec, "MAX_LIMIT")
                    if min_val is not None:
                        setattr(self, f"min_limit_{prefix}", float(min_val))
                    if max_val is not None:
                        setattr(self, f"max_limit_{prefix}", float(max_val))
                    
                # 读取点动步距列表
                self.increments = [1.0, 0.1, 0.01] # 默认值
                increments_str = inifile.find("DISPLAY", "INCREMENTS")
                if increments_str:
                    import re
                    # 匹配可能是 ".1" 或 "1.0" 的数字
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", increments_str)
                    if nums:
                        parsed_incs = []
                        for n in nums:
                            val = float(n)
                            if val > 0 and val not in parsed_incs:
                                parsed_incs.append(val)
                        if parsed_incs:
                            # 补齐或截断到3个供界面使用
                            self.increments = (parsed_incs + self.increments)[:3]
                            
                # 3. 如果没找到默认点动速度，则默认使用极速的 100% (满速)
                if self.default_jog_velocity <= 0.0:
                    self.default_jog_velocity = self.max_velocity if self.max_velocity > 0 else 10.0
                    
                print(f"[qmlvcp] 成功解析 INI 配置: {ini_path}")
            except ImportError:
                print("[qmlvcp] 警告: 找不到 linuxcnc 模块，正处于脱机开发模式。")
            except Exception as e:
                print(f"[qmlvcp] 读取 INI 配置失败: {e}")
