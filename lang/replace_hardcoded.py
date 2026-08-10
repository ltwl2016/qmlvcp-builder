#!/usr/bin/env python3
"""
硬编码字符串 → Tr.t() 替换脚本 v2
使用 AST 识别字符串字面量，按行从右到左替换，彻底解决偏移问题。
"""
import re, ast, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG_DIR = ROOT / "lang"

with open(LANG_DIR / "zh_CN.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

VAL2KEY = {}
for k, v in TRANSLATIONS.items():
    if len(v) >= 2:
        VAL2KEY[v] = k


def replace_file(filepath: Path) -> int:
    src = filepath.read_text(encoding='utf-8')
    lines = src.splitlines(True)

    try:
        tree = ast.parse(src)
    except SyntaxError:
        print(f"  SKIP {filepath.name}: syntax error")
        return 0

    # 收集替换: (行号, 列偏移, 原字符串字面量, 替换为代码)
    # 列偏移是 AST 的字节偏移 → 对纯 ASCII 行等同于字符偏移
    # 对于含中文的行，需要将字节偏移转换为字符偏移
    replacements = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        if not isinstance(node.value, str):
            continue
        if node.value not in VAL2KEY:
            continue
        text = node.value
        key = VAL2KEY[text]
        old_raw = ast.get_source_segment(src, node)
        if old_raw is None:
            continue
        # old_raw: "文字" 或 '文字'
        if len(old_raw) < len(text) + 2:
            continue
        quote = old_raw[0]
        new_code = f'Tr.t("{key}", {quote}{text}{quote})'
        lineno = node.lineno - 1
        replacements.append((lineno, old_raw, new_code))

    if not replacements:
        return 0

    # 按行列分组，同行的从右到左替换
    from collections import defaultdict
    line_groups = defaultdict(list)
    for (lineno, old_raw, new_code) in replacements:
        line_groups[lineno].append((old_raw, new_code))

    # 按行号倒序处理
    for lineno in sorted(line_groups.keys(), reverse=True):
        line = lines[lineno]
        items = line_groups[lineno]
        # 同行的按旧字符串长度倒序 (从右往左确保位置不漂移)
        # 找每个 old_raw 在行中的最后出现位置
        replacements_on_line = []
        for old_raw, new_code in items:
            pos = line.rfind(old_raw)
            if pos != -1:
                replacements_on_line.append((pos, len(old_raw), new_code))
        if not replacements_on_line:
            continue
        # 从右往左替换
        replacements_on_line.sort(key=lambda x: -x[0])
        for pos, length, new_code in replacements_on_line:
            line = line[:pos] + new_code + line[pos + length:]
        lines[lineno] = line

    mod_src = ''.join(lines)

    # 添加 import
    need_import = 'from lang import Tr' not in mod_src
    if need_import:
        lines2 = mod_src.splitlines(True)
        insert_idx = 0
        in_import_block = False
        in_docstring = False
        for i, line in enumerate(lines2):
            stripped = line.strip()
            if in_docstring:
                if stripped.endswith('"""') or stripped.endswith("'''"):
                    in_docstring = False
                continue
            if stripped.startswith('"""') and not (stripped.endswith('"""') and len(stripped) > 3):
                in_docstring = True
                continue
            if stripped.startswith("'''") and not (stripped.endswith("'''") and len(stripped) > 3):
                in_docstring = True
                continue
            if in_import_block:
                if stripped == ')' or (stripped and not line.startswith((' ', '\t'))):
                    in_import_block = False
                    insert_idx = i + 1 if stripped == ')' else i
            elif not stripped or line[0] in (' ', '\t'):
                continue
            elif line.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            elif stripped.startswith('import ') or stripped.startswith('from '):
                if stripped.endswith('('):
                    in_import_block = True
                else:
                    insert_idx = i + 1
            else:
                break
        lines2.insert(insert_idx, 'from lang import Tr\n')
        mod_src = ''.join(lines2)

    if mod_src != src:
        filepath.write_text(mod_src, encoding='utf-8')
        return len(replacements)
    return 0


def main():
    targets = [
        ROOT / "builder" / "controls.py",
        ROOT / "builder" / "main_window.py",
        ROOT / "builder" / "env_setup.py",
        ROOT / "builder" / "properties_mixin.py",
        ROOT / "builder" / "preview_canvas.py",
        ROOT / "builder" / "project_exporter.py",
        ROOT / "builder" / "project_importer.py",
        ROOT / "builder" / "field_registry.py",
        ROOT / "builder" / "templates" / "control_defs.py",
        ROOT / "qmlvcp" / "core" / "command.py",
        ROOT / "qmlvcp" / "core" / "config.py",
        ROOT / "qmlvcp" / "core" / "file_manager.py",
        ROOT / "qmlvcp" / "core" / "hal_manager.py",
        ROOT / "qmlvcp" / "core" / "hal_show.py",
        ROOT / "qmlvcp" / "core" / "runtime_tracker.py",
        ROOT / "qmlvcp" / "core" / "status.py",
        ROOT / "qmlvcp" / "core" / "gcode_graphics.py",
        ROOT / "qmlvcp" / "core" / "gcode_parser.py",
        ROOT / "qmlvcp" / "core" / "jog_controller.py",
        ROOT / "qmlvcp" / "core" / "keyboard.py",
        ROOT / "qmlvcp" / "core" / "override_manager.py",
        ROOT / "qmlvcp" / "core" / "setup.py",
        ROOT / "backend_actions_binds.py",
        ROOT / "main.py",
    ]

    total = 0
    for fp in targets:
        if not fp.exists():
            continue
        n = replace_file(fp)
        if n > 0:
            print(f"  OK {fp.relative_to(ROOT)}: {n} strings")
        total += n

    print(f"\nTotal: {total} replacements across {len(targets)} files")

if __name__ == "__main__":
    main()
