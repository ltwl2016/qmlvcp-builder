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
