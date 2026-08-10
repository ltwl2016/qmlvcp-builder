#!/usr/bin/env python3
"""
i18n UI 字符串提取工具 — 只提取用户可见的界面字符串，自动跳过 docstring/日志/内部标记。
用法: python lang/extract_i18n.py
输出: lang/zh_CN.json (覆盖写入)
"""
import os, re, json, hashlib
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SRC_DIRS = [ROOT / "builder", ROOT / "qmlvcp", ROOT]
OUTPUT = ROOT / "lang" / "zh_CN.json"

# ── 跳过 ──
SKIP_DIRS = {"__pycache__", ".git", "venv", "offline_wheels", "lang", "i18n"}
SKIP_FILES = {"__init__.py"}

def has_chinese(s: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', s))

# 函数描述开头模式：这些动词开头的长句通常是代码文档，不是 UI
_DESC_START = re.compile(
    r'^(返回|设置|获取|创建|停止|计算|检测|确保|管理|负责|通用|接收|执行|递归|切换|全量|同|将|用于|在|从|根据|按|为|向|用)'
)

def is_non_ui(s: str) -> bool:
    """判断是否为非 UI 字符串 (docstring / log / section header / format string / 函数描述)"""
    s = s.strip()
    # 无中文字符 -> 跳过
    if not has_chinese(s):
        return True
    # docstring: 多行且较长
    if '\n' in s and len(s) > 60:
        return True
    # 日志前缀 [xxx]
    if s.startswith('['):
        return True
    # section header: --- xxx ---
    if re.match(r'^---.*---$', s):
        return True
    # f-string / logging format
    if re.search(r'\{.*\}', s):
        return True
    # 纯 GPL 许可证
    if 'GNU General Public License' in s:
        return True
    # 函数描述：动词开头 + 以句号结尾 + 超过8个字
    if _DESC_START.match(s) and s.endswith('。') and len(s) > 8:
        return True
    # 函数描述：中英文混合的参数说明 → 包含引号+参数名
    if re.search(r'["\']\w+["\']', s) and len(s) > 15:
        return True
    return False

def short_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:6]

# ────────────────────────────────────────────────────────
#  1. 提取 Python 文件
# ────────────────────────────────────────────────────────

PY_STRING_RE = re.compile(
    r"'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\""
    r"|'[^'\\]*(?:\\.[^'\\]*)*'"
    r'|"[^"\\]*(?:\\.[^"\\]*)*"'
)

def extract_py(filepath: Path) -> dict:
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return {}

    rel = str(filepath.relative_to(ROOT))
    stem = filepath.stem
    entries = {}

    # 找每个字符串出现位置的上下文（函数/类名 或 控件变量名）
    contexts = []
    for m in re.finditer(r'(?:def|class)\s+(\w+)', content):
        contexts.append((m.start(), m.group(1)))
    # 找控件属性赋值：self.lblXxx = xxxx 或 self.btnXxx = xxxx
    for m in re.finditer(r'self\.(\w+)\s*=', content):
        contexts.append((m.start(), m.group(1)))

    contexts.sort(key=lambda x: x[0])

    def find_context(pos: int) -> str:
        ctx = stem
        for cpos, cname in reversed(contexts):
            if cpos < pos:
                ctx = cname
                break
        return ctx

    idx = 0
    for match in PY_STRING_RE.finditer(content):
        raw = match.group(0)
        if raw.startswith("'''") or raw.startswith('"""'):
            inner = raw[3:-3]
        else:
            inner = raw[1:-1]

        if is_non_ui(inner):
            continue

        ctx = find_context(match.start())
        idx += 1
        h = short_hash(inner)
        key = f"{ctx}.s{idx}_{h}"
        entries[key] = inner.strip()

    return entries

# ────────────────────────────────────────────────────────
#  2. 提取 .ui 文件 (使用 widget name 命名)
# ────────────────────────────────────────────────────────

def extract_ui(filepath: Path) -> dict:
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return {}
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return {}

    entries = {}

    def find_widget_names(elem, prefix=""):
        """递归找所有 widget，名字最近的 widget 作为 context"""
        name = elem.get('name', '')
        if name:
            prefix = name

        for child in elem:
            class_type = child.tag if '}' not in child.tag else child.tag.split('}')[1]

            if class_type in ('property', 'attribute'):
                prop_name = child.get('name', '')
                for sub in child:
                    if sub.tag.endswith('string') and sub.text:
                        text = sub.text.strip()
                        if not is_non_ui(text):
                            if prefix:
                                key = f"ui.{prefix}.{prop_name}"
                            else:
                                key = f"ui.{prop_name}.{short_hash(text)}"
                            entries[key] = text
            elif class_type == 'string' and child.text:
                text = child.text.strip()
                if not is_non_ui(text) and prefix:
                    key = f"ui.{prefix}.label"
                    entries[key] = text

            find_widget_names(child, prefix)

    find_widget_names(root)
    return entries

# ────────────────────────────────────────────────────────
#  3. 提取 .qml 模板文件
# ────────────────────────────────────────────────────────

def extract_qml(filepath: Path) -> dict:
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return {}

    rel = str(filepath.relative_to(ROOT))
    stem = filepath.stem
    entries = {}

    for match in re.finditer(r'"((?:\\.|[^"\\])*)"', content):
        text = match.group(1).strip()
        if is_non_ui(text) or len(text) < 2:
            continue
        if text.startswith('$'):
            continue  # 变量占位符

        h = short_hash(text)
        key = f"qml.{stem}.{h}"
        entries[key] = text

    return entries

# ────────────────────────────────────────────────────────
#  主流程
# ────────────────────────────────────────────────────────

def main():
    all_entries = {}
    stats = {}

    for src_dir in SRC_DIRS:
        if not src_dir.exists():
            continue
        for filepath in src_dir.rglob("*"):
            if filepath.is_dir():
                continue
            if filepath.name in SKIP_FILES:
                continue
            if set(filepath.parts) & SKIP_DIRS:
                continue

            suffix = filepath.suffix.lower()
            if suffix == ".py":
                entries = extract_py(filepath)
            elif suffix == ".ui":
                entries = extract_ui(filepath)
            elif suffix == ".qml":
                entries = extract_qml(filepath)
            else:
                continue

            if entries:
                stats[filepath.name] = len(entries)
                for k, v in entries.items():
                    all_entries[k] = v

    # 按 key 排序输出
    sorted_entries = dict(sorted(all_entries.items()))

    print(f"UI 字符串提取完成: {len(sorted_entries)} 条, 来自 {len(stats)} 个文件")
    for fname, cnt in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {cnt:>4}  {fname}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
    print(f"\n输出: {OUTPUT}")

if __name__ == "__main__":
    main()
