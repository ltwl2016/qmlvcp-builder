#!/usr/bin/env python3
"""修复脚本：将误替换的裸 Tr.t() 表达式（原 docstring）还原为三重引号字符串。"""
import ast, re, io, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
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

# ── 正则：匹配 Tr.t("key", "text") 或 Tr.t("key", 'text')
TR_T_RE = re.compile(r'Tr\.t\s*\(\s*"(?:[^"\\]|\\.)*"\s*,\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')\s*\)')

def fix_file(filepath: Path) -> int:
    src = filepath.read_text(encoding='utf-8')
    lines = src.splitlines(True)

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"  SKIP {filepath.name}: {e}")
        return 0

    # 收集需要修复的位置: (lineno-1, old_expr)
    fixes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Expr):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        call = node.value
        if not isinstance(call.func, ast.Attribute):
            continue
        if not isinstance(call.func.value, ast.Name):
            continue
        if call.func.value.id != 'Tr':
            continue
        if call.func.attr != 't':
            continue
        old_raw = ast.get_source_segment(src, node)
        if old_raw is None:
            continue
        fixes.append((node.lineno - 1, old_raw, call))

    if not fixes:
        return 0

    # 从右到左按行处理
    from collections import defaultdict
    line_groups = defaultdict(list)
    for (lineno, old_raw, call_node) in fixes:
        # 提取 fallback 字符串
        if len(call_node.args) >= 2:
            fallback_node = call_node.args[1]
            fallback_text = ast.literal_eval(fallback_node)
        else:
            continue
        # 构建 docstring
        new_str = f'"""{fallback_text}"""'
        line_groups[lineno].append((old_raw, new_str))

    for lineno in sorted(line_groups.keys(), reverse=True):
        line_num = lineno
        items = line_groups[lineno]
        mods = []
        for old_raw, new_str in items:
            pos = lines[line_num].rfind(old_raw)
            if pos != -1:
                mods.append((pos, len(old_raw), new_str))
        if not mods:
            continue
        mods.sort(key=lambda x: -x[0])
        line = lines[line_num]
        for pos, length, new_str in mods:
            line = line[:pos] + new_str + line[pos + length:]
        lines[line_num] = line

    mod_src = ''.join(lines)
    if mod_src != src:
        filepath.write_text(mod_src, encoding='utf-8')
        return len(fixes)
    return 0


def main():
    total = 0
    for fp in TARGETS:
        if not fp.exists():
            continue
        n = fix_file(fp)
        if n > 0:
            print(f"  OK {fp.relative_to(ROOT)}: {n} docstrings restored")
        total += n
    print(f"\nTotal: {total} docstrings restored")

if __name__ == "__main__":
    main()
