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
环境设置模块 — 创建 venv + 安装 PySide6。
所有操作在独立线程中执行，避免阻塞 UI。
"""

import os
import subprocess
import sys
import threading
from PyQt5.QtCore import QObject, pyqtSignal


class EnvManager(QObject):
    """管理 Python 虚拟环境和依赖安装。"""

    statusChanged = pyqtSignal(str)   # 状态消息
    finished = pyqtSignal(bool, str)  # 完成标志 + 消息

    def __init__(self, project_dir: str):
        super().__init__()
        self.project_dir = project_dir
        # venv 放在 qmlvcp-builder 的上层目录，与导出项目位置无关
        self._builder_parent = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.venv_dir = os.path.join(self._builder_parent, "venv")
        self.venv_python = (
            os.path.join(self.venv_dir, "Scripts", "python.exe")
            if sys.platform == "win32"
            else os.path.join(self.venv_dir, "bin", "python3")
        )

    def run_in_thread(self, func, *args):
        t = threading.Thread(target=func, args=args, daemon=True)
        t.start()

    # ── 状态检查 ──

    @property
    def venv_exists(self) -> bool:
        """扫描 builder 上层目录及项目目录，查找任意包含 pyvenv.cfg 的 venv。"""
        search_dirs = [self._builder_parent,
                       self.project_dir,
                       os.path.dirname(self.project_dir.rstrip("/\\"))]
        for base in search_dirs:
            if not os.path.isdir(base):
                continue
            for name in os.listdir(base):
                cfg = os.path.join(base, name, "pyvenv.cfg")
                if os.path.isfile(cfg):
                    # 更新 venv_dir 和 venv_python
                    self.venv_dir = os.path.join(base, name)
                    bindir = "Scripts" if sys.platform == "win32" else "bin"
                    pyexe = "python.exe" if sys.platform == "win32" else "python3"
                    self.venv_python = os.path.join(self.venv_dir, bindir, pyexe)
                    return os.path.exists(self.venv_python)
        return False

    @property
    def system_has_pyside6(self) -> bool:
        """系统 Python 是否已安装 PySide6（无需 venv）。"""
        return self._check_pyside6(sys.executable)

    @property
    def pyside6_installed(self) -> bool:
        """检测 PySide6：先查 venv，再查系统 Python。"""
        # 方法1: venv 内检查
        if self.venv_exists:
            if self._check_pyside6(self.venv_python):
                return True
        # 方法2: 系统全局 Python 检查
        if self._check_pyside6(sys.executable):
            return True
        return False

    @staticmethod
    def _check_pyside6(python_exe: str) -> bool:
        """用指定的 Python 解释器检测 PySide6 是否可导入。"""
        try:
            result = subprocess.run(
                [python_exe, "-c", "import PySide6"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    # ── 创建 venv ──

    def create_venv(self):
        self.run_in_thread(self._create_venv_thread)

    @staticmethod
    def _is_debian_like() -> bool:
        """是否为 Debian/Ubuntu 等 apt-based 发行版。"""
        return os.path.isfile("/etc/debian_version")

    @staticmethod
    def _venv_module_ok() -> bool:
        """venv 模块是否就绪（含 ensurepip）。"""
        try:
            subprocess.run(
                [sys.executable, "-c", "import venv, ensurepip"],
                capture_output=True, timeout=5
            )
            return True
        except Exception:
            return False

    def _install_system_venv(self):
        """Debian/Ubuntu 上安装 python3-venv 系统包。"""
        self.statusChanged.emit("正在安装系统包 python3-venv ...")
        try:
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "python3-venv"],
                check=True, capture_output=True, timeout=120
            )
            self.statusChanged.emit("python3-venv 系统包安装成功")
            return True
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode()[:300] if e.stderr else str(e)
            self.statusChanged.emit(f"系统包安装失败: {err}")
            return False
        except FileNotFoundError:
            self.statusChanged.emit("未找到 sudo 或 apt-get 命令")
            return False
        except Exception as e:
            self.statusChanged.emit(f"系统包安装异常: {e}")
            return False

    def _create_venv_thread(self):
        self.statusChanged.emit("正在创建虚拟环境...")

        # Debian/Ubuntu 可能缺少 python3-venv，先尝试安装
        if sys.platform != "win32" and not self._venv_module_ok():
            if self._is_debian_like():
                self.statusChanged.emit("检测到 Debian/Ubuntu，缺少 python3-venv 包")
                if not self._install_system_venv():
                    self.finished.emit(
                        False,
                        "请手动执行: sudo apt-get install -y python3-venv\n然后重试。",
                    )
                    return
                # 安装完成后重新验证
                if not self._venv_module_ok():
                    self.finished.emit(
                        False,
                        "python3-venv 已安装但 venv 模块仍不可用，请检查 Python 版本。",
                    )
                    return
            else:
                self.finished.emit(
                    False,
                    "缺少 venv 模块，请安装对应发行版的 python3-venv 包后重试。",
                )
                return

        try:
            subprocess.run(
                [sys.executable, "-m", "venv", self.venv_dir],
                check=True, capture_output=True, timeout=60
            )
            self.statusChanged.emit("虚拟环境创建成功")
            self.finished.emit(True, "venv 创建完成")
        except subprocess.CalledProcessError as e:
            hint = ""
            if sys.platform != "win32" and self._is_debian_like():
                hint = "\n(Debian/Ubuntu 请确保已安装: sudo apt-get install python3-venv)"
            err = e.stderr.decode()[:200] if e.stderr else str(e)
            msg = f"创建失败: {err}{hint}"
            self.statusChanged.emit(msg)
            self.finished.emit(False, msg)
        except Exception as e:
            self.statusChanged.emit(f"异常: {e}")
            self.finished.emit(False, str(e))

    # ── 安装 PySide6 ──

    def install_pyside6(self):
        self.run_in_thread(self._install_pyside6_thread)

    # ── 国内镜像源（按优先级排列）──
    _MIRRORS = [
        ("默认源", []),
        ("清华镜像", ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]),
        ("阿里镜像", ["-i", "https://mirrors.aliyun.com/pypi/simple"]),
    ]

    @staticmethod
    def _is_linuxcnc() -> bool:
        """是否为 LinuxCNC 环境（存在 /usr/bin/linuxcnc）。"""
        return os.path.isfile("/usr/bin/linuxcnc")

    @staticmethod
    def _cpu_arch() -> str:
        """当前 CPU 架构名：x86_64 / aarch64 / armv7l 等。"""
        import platform
        return platform.machine()

    @property
    def _offline_wheels_dir(self) -> str:
        """查找当前架构的 offline_wheels 子目录（项目内 > 项目父目录 > builder自身）。"""
        arch = self._cpu_arch()
        builder_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        search = [self.project_dir,
                  os.path.dirname(self.project_dir.rstrip("/\\")),
                  builder_root]
        for base in search:
            d = os.path.join(base, "offline_wheels", arch)
            if os.path.isdir(d):
                whl_files = [f for f in os.listdir(d) if f.endswith(".whl")]
                if whl_files:
                    return d
        return ""

    def _pip_install(self, args: list, timeout: int) -> bool:
        """执行 pip install，成功返回 True，失败时输出 stderr 到日志。"""
        try:
            result = subprocess.run(
                [self.venv_python, "-m", "pip", "install", "--break-system-packages"] + args,
                capture_output=True, timeout=timeout
            )
            if result.returncode == 0:
                return True
            err = result.stderr.decode("utf-8", errors="replace").strip()
            if not err:
                err = result.stdout.decode("utf-8", errors="replace").strip()
            self.statusChanged.emit(f"pip 错误: {err[-500:]}")  # 最后 500 字符
            return False
        except subprocess.TimeoutExpired:
            self.statusChanged.emit("pip 安装超时")
            return False
        except Exception as e:
            self.statusChanged.emit(f"pip 异常: {e}")
            return False

    def _install_pyside6_thread(self):
        if not self.venv_exists:
            self.finished.emit(False, "请先创建虚拟环境")
            return

        self.statusChanged.emit("正在安装 PySide6 (可能需要几分钟)...")

        # ---- 诊断输出（显示在 UI 日志） ----
        self.statusChanged.emit(
            f"[诊断] arch={self._cpu_arch()} python={sys.version_info.major}.{sys.version_info.minor}"
        )
        self.statusChanged.emit(
            f"[诊断] project_dir={self.project_dir}"
        )
        self.statusChanged.emit(
            f"[诊断] venv_dir={self.venv_dir}"
        )
        odir = self._offline_wheels_dir
        self.statusChanged.emit(
            f"[诊断] offline_wheels_dir={odir or '未找到'}"
        )
        if odir:
            files = [f for f in os.listdir(odir) if f.endswith(".whl")]
            self.statusChanged.emit(f"[诊断] whl 文件列表({len(files)}个): {files[:10]}")
        # ---------------------------------

        # 1. 升级 pip
        self.statusChanged.emit("升级 pip ...")
        if not self._pip_install(["--upgrade", "pip"], timeout=30):
            self.statusChanged.emit("pip 升级失败，尝试继续安装 PySide6 ...")

        # 2. 优先使用脱机 wheel 安装（任何平台，只要找到离线包）
        wheels = self._offline_wheels_dir
        if wheels:
            self.statusChanged.emit(f"脱机安装 — {wheels}")
            if self._pip_install(
                ["--no-index", f"--find-links={wheels}", "PySide6>=6.5"],
                timeout=120
            ):
                self.statusChanged.emit("PySide6 脱机安装成功")
                self.finished.emit(True, "PySide6 安装完成（脱机）")
                return
            self.statusChanged.emit("脱机安装失败，回退到在线安装...")
        else:
            self.statusChanged.emit("未找到 offline_wheels/ 目录，使用在线安装...")

        # 3. 在线安装 PySide6（重试 + 镜像回退）
        for mirror_name, mirror_args in self._MIRRORS:
            for attempt in range(1, 4):
                tag = f"{mirror_name} (第 {attempt} 次)"
                self.statusChanged.emit(f"安装 PySide6 — {tag}")
                if self._pip_install(mirror_args + ["PySide6>=6.5"], timeout=300):
                    self.statusChanged.emit("PySide6 安装成功")
                    self.finished.emit(True, "PySide6 安装完成")
                    return
                if attempt < 3:
                    self.statusChanged.emit(f"{tag} 失败，5 秒后重试...")
                    import time
                    time.sleep(5)

        # 4. 全部失败
        hint = (
            "所有源均安装失败。\n"
            "请检查网络连接后重试，或手动安装：\n"
            f'  {self.venv_python} -m pip install PySide6>=6.5'
        )
        if self._is_linuxcnc():
            arch = self._cpu_arch()
            pyver = sys.version_info
            hint += (
                f"\n\nLinuxCNC 环境（{arch} / Python {pyver.major}.{pyver.minor}）建议使用脱机安装：\n"
                f"  1. 在同架构的有网机器上下载（注意 Python 版本号）：\n"
                f'     pip download --only-binary=:all: PySide6 -d offline_wheels/{arch}/\n'
                f'     （跨架构下载需加 --platform manylinux_xxx_{arch} --python-version {pyver.major}{pyver.minor}）\n'
                f"  2. 将整个 offline_wheels/ 复制到项目目录下\n"
                f"  3. 重新打开环境设置并点击安装"
            )
        elif sys.platform != "win32" and self._is_debian_like():
            hint += (
                "\n\n如果是 Debian/Ubuntu，可能缺少系统依赖：\n"
                "  sudo apt-get install -y libxcb-cursor0 libegl1 libgl1"
            )
        self.statusChanged.emit("PySide6 安装失败")
        self.finished.emit(False, hint)
