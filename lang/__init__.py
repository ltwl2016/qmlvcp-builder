"""
lang — QmlVcp Builder 多语言翻译模块

用法:
    from lang import Tr

    label = Tr.t("key", "Default text")       # 翻译单条（英文源）
    Tr.load("zh_CN")                          # 切换到中文
    print(Tr.available)                       # 列出可用语言

编译时调用 Tr.compile_to_py() 将翻译硬编码进上下文，避免运行时依赖 JSON 文件。
"""

import json, os
from pathlib import Path

_LANG_DIR = Path(__file__).resolve().parent


class _Translator:
    """单例翻译器，模块级 import lang; Tr = lang.Tr 直接使用。"""

    def __init__(self):
        self._current = "en"
        self._data: dict = {}  # 空字典=使用代码 fallback（英文）
        # 默认不加载翻译，英文源串直接使用

    # ── 公开属性 ──

    @property
    def current(self) -> str:
        """当前语言代码，如 'en' / 'zh_CN'"""
        return self._current

    @property
    def available(self) -> list:
        """扫描 lang/ 下所有 .json 文件，提取可用语言列表"""
        langs = []
        if _LANG_DIR.is_dir():
            for f in _LANG_DIR.glob("*.json"):
                langs.append(f.stem)
        return sorted(langs)

    # ── 加载 ──

    def load(self, lang: str) -> bool:
        """加载指定语言。成功返回 True，失败返回 False（不改变当前语言）。"""
        path = _LANG_DIR / f"{lang}.json"
        if not path.is_file():
            print(f"[lang] 语言文件不存在: {path}")
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            self._current = lang
            return True
        except Exception as e:
            print(f"[lang] 加载失败: {e}")
            return False

    # ── 翻译 ──

    def t(self, key: str, fallback: str = "") -> str:
        """获取翻译文本。key 不存在或翻译值为空时返回 fallback。"""
        val = self._data.get(key)
        if val:
            return val
        return fallback or key

    def __call__(self, key: str, fallback: str = "") -> str:
        """语法糖：Tr("key", "default") 等价于 Tr.t(...)"""
        return self.t(key, fallback)

    # ── 编译 ──

    def compile_to_py(self, lang: str, output_path: str = None) -> None:
        """将翻译文件编译为 Python 字典，用于打包发布（避免依赖 JSON 文件）。"""
        path = _LANG_DIR / f"{lang}.json"
        if not path.is_file():
            raise FileNotFoundError(f"语言文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if output_path is None:
            output_path = str(_LANG_DIR / f"{lang}.py")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Auto-generated from {lang}.json\n")
            f.write(f"_{lang} = ")
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[lang] 已编译: {output_path}")


# ── 全局单例 ──
Tr = _Translator()
del _Translator
