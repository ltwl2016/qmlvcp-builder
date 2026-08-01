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
程序文件管理器 — 文件浏览、加载、关闭、编辑。
每一个 CNC 界面都需要的通用功能，从项目 Backend 下沉到 qmlvcp 框架。
"""

from __future__ import annotations

import os
import sys
import subprocess
import tempfile

from PySide6.QtCore import QObject, Property, Signal, Slot


# 默认过滤扩展名
DEFAULT_EXTENSIONS = (".nc", ".ngc", ".txt", ".tap")


class FileManager(QObject):
    """管理 G 代码文件的浏览、加载、关闭、编辑。"""

    fileBrowserChanged = Signal()
    programChanged = Signal()

    def __init__(
        self,
        command,
        status,
        start_dir: str = "/home/cnc/linuxcnc/nc_files",
        extensions: tuple = DEFAULT_EXTENSIONS,
        parent=None,
    ):
        super().__init__(parent)
        self._cmd        = command      # qmlvcp Command 对象
        self._st         = status       # qmlvcp Status 对象
        self._start_dir  = start_dir
        self._extensions = extensions

        self._current_dir   = start_dir
        self._file_list     = []
        self._program_lines = []
        self._last_file     = ""

        # 监听 G 代码文件变化（加载/关闭程序时触发）
        self._st.programFileChanged.connect(self._on_program_file_changed)

        # 启动时扫描一次
        self._refresh_file_list()

    # ── 属性 ──────────────────────────────────────────────────────

    @Property("QVariantList", notify=fileBrowserChanged)
    def fileList(self):
        return self._file_list

    @Property(str, notify=fileBrowserChanged)
    def currentDir(self):
        return self._current_dir

    @Property(str, notify=programChanged)
    def programFile(self):
        pfile = self._st.programFile
        if pfile and not pfile.endswith("empty.ngc"):
            return pfile
        return ""

    @Property(str, notify=programChanged)
    def programName(self):
        pfile = self._st.programFile
        if pfile and not pfile.endswith("empty.ngc"):
            return os.path.basename(pfile)
        return ""

    @Property("QVariantList", notify=programChanged)
    def programLines(self):
        return self._program_lines

    # ── Slot ──────────────────────────────────────────────────────

    @Slot(str)
    def changeDir(self, path: str):
        """切换到指定目录并刷新文件列表。"""
        if not os.path.exists(path) or not os.path.isdir(path):
            return
        self._current_dir = os.path.abspath(path)
        self._refresh_file_list()

    @Slot(str)
    def loadProgram(self, filepath: str):
        """加载指定 G 代码文件到 LinuxCNC。"""
        self._cmd.programOpen(filepath, is_idle=self._st.interpIdle)

    @Slot()
    def reloadProgram(self):
        """重新加载当前程序。"""
        if self._st.programFile:
            self._cmd.programOpen(self._st.programFile, is_idle=self._st.interpIdle)
            self._last_file = ""
            self._on_program_file_changed()

    @Slot()
    def rewindProgram(self):
        """回到程序开头。"""
        if self._st.interpIdle:
            self._cmd.programRewind()

    @Slot()
    def closeProgram(self):
        """关闭当前程序（加载空文件）。"""
        empty_file = os.path.join(tempfile.gettempdir(), "empty.ngc")
        if not os.path.exists(empty_file):
            try:
                with open(empty_file, "w", encoding="utf-8") as f:
                    f.write("M2\n%\n")
            except Exception:
                pass
        self._cmd.programOpen(empty_file, is_idle=self._st.interpIdle)

    @Slot()
    def editProgram(self):
        """用系统默认编辑器打开当前 G 代码文件。"""
        pfile = self._st.programFile
        if not pfile or os.path.basename(pfile) == "empty.ngc":
            return
        try:
            if sys.platform == "win32":
                subprocess.Popen(["notepad.exe", pfile])
            else:
                for editor in ("mousepad", "gedit", "leafpad"):
                    try:
                        subprocess.Popen([editor, pfile])
                        return
                    except FileNotFoundError:
                        continue
                # 最后尝试终端 nano
                subprocess.Popen(["x-terminal-emulator", "-e", "nano", pfile])
        except Exception as e:
            print(f"[FileManager] 编辑器启动失败: {e}")

    # ── 内部 ──────────────────────────────────────────────────────

    def _refresh_file_list(self):
        """重建当前目录的文件列表。"""
        new_list = []
        if self._current_dir != "/":
            new_list.append({
                "name": "..", "isDir": True, "size": "",
                "path": os.path.dirname(self._current_dir),
            })
        try:
            for f in os.listdir(self._current_dir):
                if f.startswith("."):
                    continue
                full = os.path.join(self._current_dir, f)
                is_dir = os.path.isdir(full)
                if not is_dir and not f.lower().endswith(self._extensions):
                    continue
                sz = "" if is_dir else f"{os.path.getsize(full)/1024:.1f} KB"
                new_list.append({
                    "name": f, "isDir": is_dir, "size": sz, "path": full,
                })
        except Exception as e:
            print(f"[FileManager] 读取目录失败: {e}")

        new_list.sort(key=lambda x: (
            0 if x["name"] == ".." else (1 if not x["isDir"] else 0),
            x["name"].lower(),
        ))
        self._file_list = new_list
        self.fileBrowserChanged.emit()

    def _on_program_file_changed(self):
        """LinuxCNC 加载/关闭程序时，重新读取文件内容。"""
        pfile = self._st.programFile
        self._last_file = pfile
        if not pfile or os.path.basename(pfile) == "empty.ngc":
            self._program_lines = []
        else:
            try:
                with open(pfile, "r", encoding="utf-8") as f:
                    self._program_lines = f.readlines()
            except Exception:
                self._program_lines = ["[Error loading file]"]
        self.programChanged.emit()

    # motionLineChanged 的处理保留在 backend.py 中(lineChanged → lineNumber),
    # 不应触发 programChanged(programLines), 否则每行 G 代码都导致 QML 重读整个列表, 性能崩盘
