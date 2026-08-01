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
qmlVCP HalShow Provider
提供系统级别 HAL 状态的反射能力，类似于 QtVCP 中的 halshow。
"""
from __future__ import annotations
import subprocess
from PySide6.QtCore import QObject, Slot

class HalShowProvider(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
    
    @Slot(result="QVariantList")
    def getPins(self) -> list:
        return self._run_halcmd("pin")
        
    @Slot(result="QVariantList")
    def getSignals(self) -> list:
        return self._run_halcmd("sig")

    def _run_halcmd(self, kind: str) -> list:
        try:
            result = subprocess.run(["halcmd", "show", kind], capture_output=True, text=True)
            lines = result.stdout.splitlines()
        except Exception as e:
            print(f"[HalShowProvider] halcmd 运行失败: {e}")
            return []

        data = []
        started = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 开始解析表头下方的真正数据
            if line.startswith("Owner") or (kind == "sig" and line.startswith("Type")):
                started = True
                continue
                
            if not started:
                continue
                
            parts = line.split()
            
            if kind == "pin" and len(parts) >= 5:
                # 典型的 pin 输出: 83  float OUT             1  qmlvcp.feed-override
                data.append({
                    "owner": parts[0],
                    "type": parts[1],
                    "dir": parts[2],
                    "value": parts[3],
                    "name": parts[4],
                    "linked": " ".join(parts[5:]) if len(parts) > 5 else ""
                })
            elif kind == "sig" and len(parts) >= 3:
                # 典型的 sig 输出: bit          FALSE  estop-loop
                data.append({
                    "owner": "-",
                    "type": parts[0],
                    "dir": "-",
                    "value": parts[1],
                    "name": parts[2],
                    "linked": " ".join(parts[3:]) if len(parts) > 3 else ""
                })
        return data

    @Slot(str, str)
    def setPin(self, name: str, value: str) -> None:
        """通过 halcmd setp 命令强制修改底层引脚"""
        try:
            subprocess.run(["halcmd", "setp", name, value], check=True)
            print(f"[HalShowProvider] 成功设置 {name} = {value}")
        except Exception as e:
            print(f"[HalShowProvider] 设置引脚 {name} 失败: {e}")
