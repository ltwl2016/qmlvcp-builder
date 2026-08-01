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

"""项目文件模板 — main.py, backend.py, start.sh, start.bat 等。"""
import os

_DIR = os.path.dirname(__file__)

def _load(name: str) -> str:
    with open(os.path.join(_DIR, name), "r", encoding="utf-8") as f:
        return f.read()

def load_main_py() -> str:
    return _load("main.py.tmpl")

def load_backend_py() -> str:
    return _load("backend.py.tmpl")

def load_start_sh() -> str:
    return _load("start.sh.tmpl")

def load_start_bat() -> str:
    return _load("start.bat.tmpl")

def load_requirements() -> str:
    return _load("requirements.txt")
