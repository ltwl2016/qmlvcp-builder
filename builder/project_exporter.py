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
项目导出模块 — 根据拼装结果生成完整 qmlvcp 项目文件。

模板基于 qmlvcp/template/ 目录，占位符 {{var}} 替换。
控件定义统一来自 builder/controls.py。
"""

import os
import sys

from builder.controls import fill_template, export_controls_qml


def _export_leaves(ctrls: list) -> str:
    """输出控件列表的 QML（每个控件独立，不解父子关系）。"""
    if not ctrls:
        return ""
    lines = []
    for c in ctrls:
        lines.append(fill_template(c).rstrip())
    return "\n".join(lines)


def generate_main_qml(controls: list, bg_image: str, width: int, height: int) -> str:
    """根据控件列表生成 Main.qml。"""
    lines = [
        'import QtQuick',
        'import QtQuick.Controls.Basic',
        'import QtQuick3D',
        'import QmlVcp.Controls 1.0',
        '',
        'Window {',
        '    id: mainWindow',
        f'    width: {width}',
        f'    height: {height}',
        '    visible: true',
        '',
    ]
    if bg_image:
        lines.extend([
            '    // 背景图',
            '    Image {',
            '        anchors.fill: parent',
            f'        source: assetsDir + "/assets/{os.path.basename(bg_image)}"',
            '        z: -1',
            '    }',
            '',
        ])

    lines.append('    // ===== 控件区 =====')
    lines.append(export_controls_qml(controls))
    lines.append('}')
    return '\n'.join(lines)


def generate_main_py(project_name: str, bundle_qmlvcp: bool = False,
                     qmlvcp_parent: str = "/media/cnc/mydisk") -> str:
    """生成 main.py 入口文件。"""
    _ = qmlvcp_parent  # 保留参数兼容

    if bundle_qmlvcp:
        # 框架在项目内部: project/qmlvcp/
        path_setup = (
            'base_dir = os.path.dirname(os.path.abspath(__file__))\n'
            'qmlvcp_parent = base_dir  # 框架已打包在项目内\n'
            'sys.path.insert(0, base_dir)'
        )
    else:
        # 框架在项目外部: parent/qmlvcp/ (与项目目录同级)
        path_setup = (
            'base_dir = os.path.dirname(os.path.abspath(__file__))\n'
            'qmlvcp_parent = os.path.dirname(base_dir)  # 框架在项目上级目录\n'
            'sys.path.insert(0, qmlvcp_parent)'
        )

    from builder.templates.pfile import load_main_py
    tmpl = load_main_py()
    return tmpl.format(project_name=project_name, path_setup=path_setup)


def generate_backend_py() -> str:
    """生成模板 backend.py (用户可在此基础上修改)。"""
    from builder.templates.pfile import load_backend_py
    return load_backend_py()


def generate_main_qml_multi(pages: list, topbar: dict = None,
                           bottombar: dict = None,
                           side_panel: dict = None,
                           standalone: bool = False,
                           window_w: int = 1920,
                           window_h: int = 1080,
                           stack_current_index: int = 0) -> str:
    """生成 Main.qml：mainwindow 内容内联，子页通过 Loader 引用 pages/pageN.qml。
    
    参数:
        pages:      页面列表
        topbar:     顶部导航栏数据 {"width","height","controls",...}
        bottombar:  底部状态栏数据 {"controls",...}
        side_panel: 右侧面板数据 {"x","y","width","height","bg","controls",...}
        standalone: True=生成 Window 根元素(独立调试), False=生成 Item(嵌入式)
        window_w:   全局窗口宽度（用户设定，直接用于导出）
        window_h:   全局窗口高度
    """
    lines = [
        'import QtQuick',
        'import QtQuick.Controls.Basic',
    ]
    # 仅在有 GCodeGraphics 时才导入 QtQuick3D（该模块可能未安装）
    has_3d = _has_control(pages, "GCodeGraphics")
    if has_3d:
        lines.append('import QtQuick3D')
    if _has_control(pages, "FileDialog"):
        lines.append('import QtQuick.Dialogs')
    lines += [
        'import QmlVcp.Controls 1.0',
    ]
    if len(pages) > 1:
        lines.append('import QtQuick.Layouts')
    lines.append('')
    # mainwindow (pages[0]) → Window/Item 容器
    main = pages[0] if pages else {"name": "mainwindow", "x": 0, "y": 0, "width": 1024, "height": 768,
                                   "bg": "", "controls": []}

    # 容器尺寸 = 用户设定的全局窗口尺寸
    if standalone:
        lines.append('Window {')
        lines.append(f'    id: mainWindow')
        lines.append(f'    x: 0')
        lines.append(f'    y: 0')
        lines.append(f'    width: {window_w}')
        lines.append(f'    height: {window_h}')
        lines.append(f'    visible: true')
    else:
        lines.append('Item {')
        lines.append(f'    id: mainWindow')
        lines.append(f'    width: {window_w}')
        lines.append(f'    height: {window_h}')
    lines.append('')

    # ═══ 扁平绝对坐标布局（对齐模板风格） ═══
    # mainwindow 坐标固定为 0,0
    page_x = 0
    page_y = 0
    page_w = main.get("width", 1024)
    page_h = main.get("height", 768)

    # StackLayout 坐标取自第一个子页面，若无子页面则默认 0,0
    if len(pages) > 1:
        child = pages[1]
        stack_x = child.get("x", 0)
        stack_y = child.get("y", 0)
        stack_w = child.get("width", page_w)
        stack_h = child.get("height", page_h)
    else:
        stack_x, stack_y, stack_w, stack_h = 0, 0, page_w, page_h

    # 左侧背景图（显式 x/y/w/h，bgW/bgH 控制贴图渲染尺寸，0 则跟随页面尺寸）
    bg = main.get("bg", "")
    if bg:
        bgW_val = main.get("bgW", 0) or page_w
        bgH_val = main.get("bgH", 0) or page_h
        lines.append('')
        lines.append(f'    // 左侧背景')
        lines.append(f'    Image {{')
        lines.append(f'        x: {page_x}; y: {page_y}')
        lines.append(f'        width: {bgW_val}; height: {bgH_val}')
        lines.append(f'        source: assetsDir + "/assets/{os.path.basename(bg)}"')
        lines.append(f'    }}')

    # 右侧背景图
    if side_panel and side_panel.get("bg"):
        sp_x = side_panel.get("x", page_w)
        sp_y = side_panel.get("y", 0)
        sp_w = side_panel.get("width", 0)
        sp_h = side_panel.get("height", page_h)
        lines.append('')
        lines.append(f'    // 右侧背景')
        lines.append(f'    Image {{')
        lines.append(f'        x: {sp_x}; y: {sp_y}')
        lines.append(f'        width: {sp_w}; height: {sp_h}')
        lines.append(f'        source: assetsDir + "/assets/{os.path.basename(side_panel["bg"])}"')
        lines.append(f'    }}')

    # ── 子页浮层（StackLayout 在背景之下、主页控件之上） ──
    if len(pages) > 1:
        lines.append('')
        lines.append('    // ===== 子页浮层（覆盖主页）=====')
        lines.append('    StackLayout {')
        lines.append('        id: stack')
        lines.append(f'        x: {stack_x}; y: {stack_y}')
        lines.append(f'        width: {stack_w}; height: {stack_h}')
        lines.append(f'        currentIndex: {stack_current_index}')
        lines.append('        z: 10')
        lines.append('')
        lines.append('        // page0 空的 — 不遮挡主页控件')
        lines.append('        Item { }')
        for pp, page in enumerate(pages[1:], 1):
            name = page.get("name", f"page{pp}")
            lines.append('')
            lines.append(f'        // ----- {name} -----')
            lines.append(f'        Loader {{')
            lines.append(f'            Layout.fillWidth: true')
            lines.append(f'            Layout.fillHeight: true')
            lines.append(f'            source: "pages/{name}.qml"')
            lines.append(f'        }}')
        lines.append('    }')
    main_ctrls = main.get("controls", [])
    canvases = [(i, c) for i, c in enumerate(main_ctrls) if c.get("canvas")]
    skip_idxs = set()
    for i, c in canvases:
        skip_idxs.add(i)
    for i, c in enumerate(main_ctrls):
        if c.get("z", 0) > 0 and not c.get("canvas") and not c.get("_parent_id"):
            skip_idxs.add(i)

    def _push_indent(text: str, spaces: int) -> str:
        shift = spaces - 12
        lines_out = []
        for line in text.split('\n'):
            stripped = line.lstrip()
            if stripped:
                curr = len(line) - len(line.lstrip())
                lines_out.append(' ' * max(0, curr + shift) + stripped)
            else:
                lines_out.append('')
        return '\n'.join(lines_out)

    # ── 主页控件（永远可见，StackLayout 外） ──
    all_main = [c for i, c in enumerate(main_ctrls) if i not in skip_idxs and not c.get("_parent_id")]
    if all_main:
        lines.append('')
        lines.append('    // ===== 主页控件 =====')
        for ctrl in all_main:
            lines.append(_push_indent(fill_template(ctrl), 4))

    # ── 画布 ──
    extra_tops = []
    for ci, (orig_idx, canvas_ctrl) in enumerate(canvases):
        cx, cy = canvas_ctrl.get("x", 0), canvas_ctrl.get("y", 0)
        cw, ch = canvas_ctrl.get("w", 400), canvas_ctrl.get("h", 300)
        bg_src = canvas_ctrl.get("src", "")
        all_kids = _canvas_kids(main_ctrls, orig_idx, skip_idxs)
        if ci == 0:
            kids = [k for k in all_kids if k.get("z", 0) <= 0]
            extra_tops.extend(k for k in all_kids if k.get("z", 0) > 0)
        else:
            kids = all_kids
        lines.append('')
        lines.append(f'    // ===== 画布{ci + 1} =====')
        lines.append(f'    Rectangle {{')
        lines.append(f'        x: {cx}; y: {cy}')
        lines.append(f'        width: {cw}; height: {ch}')
        lines.append(f'        color: "transparent"')
        if bg_src:
            lines.append(f'        Image {{')
            lines.append(f'            anchors.fill: parent')
            lines.append(f'            source: assetsDir + "/assets/{os.path.basename(bg_src)}"')
            lines.append(f'        }}')
        if kids:
            lines.append(_push_indent(_export_leaves(kids), 8))
        lines.append(f'    }}')

    # ── 悬浮控件 ──
    top_ctrls = [c for i, c in enumerate(main_ctrls)
                 if i in skip_idxs and not c.get("canvas") and not c.get("_parent_id")]
    top_ctrls.extend(extra_tops)
    if top_ctrls:
        lines.append('')
        lines.append('    // ===== 悬浮控件 =====')
        lines.append('    Item {')
        lines.append('        z: 99')
        for ctrl in top_ctrls:
            lines.append(_push_indent(fill_template(ctrl), 8))
        lines.append('    }')

    # ── 右侧面板控件 ──
    if side_panel and side_panel.get("controls"):
        lines.append('')
        lines.append('    // ===== 右侧控件 =====')
        sp_ox = side_panel.get("x", 0)
        sp_oy = side_panel.get("y", 0)
        for ctrl in side_panel["controls"]:
            adj = dict(ctrl)
            adj["x"] = adj.get("x", 0) + sp_ox
            adj["y"] = adj.get("y", 0) + sp_oy
            lines.append(_push_indent(fill_template(adj), 4))

    # ── 顶部导航栏 (topbar) ──
    if topbar and topbar.get("controls"):
        lines.append('')
        lines.append('    // ===== 顶部导航栏 =====')
        lines.append('    Item {')
        lines.append('        id: topNavigation')
        tw = topbar.get("width", 1920)
        th = topbar.get("height", 80)
        lines.append(f'        x: 0')
        lines.append(f'        y: 0')
        lines.append(f'        width: {tw}')
        lines.append(f'        height: {th}')
        lines.append(f'        z: 200')
        for ctrl in topbar["controls"]:
            lines.append(_push_indent(fill_template(ctrl), 8))
        lines.append('    }')

    # ── 底部状态栏 (bottombar) ──
    if bottombar and bottombar.get("controls"):
        main_h = main.get("height", 1000)
        bb_h = bottombar.get("height", 40)
        bb_w = bottombar.get("width", main.get("width", 1024))
        lines.append('')
        lines.append('    // ===== 底部状态栏 =====')
        lines.append('    Item {')
        lines.append('        id: bottomStatus')
        lines.append(f'        x: 0')
        lines.append(f'        y: {main_h - bb_h}')
        lines.append(f'        width: {bb_w}')
        lines.append(f'        height: {bb_h}')
        lines.append(f'        z: 200')
        for ctrl in bottombar["controls"]:
            lines.append(_push_indent(fill_template(ctrl), 8))
        lines.append('    }')

    lines.append('}')
    return '\n'.join(lines)


def generate_page_qml(page: dict) -> str:
    """生成单个子页面的 qml/pages/pageN.qml 内容。"""
    name = page.get("name", "page")
    w = page.get("width", 1024)
    h = page.get("height", 768)
    bg = page.get("bg", "")

    lines = [
        'import QtQuick',
        'import QtQuick.Controls.Basic',
    ]
    has_3d = _has_control_page(page, "GCodeGraphics")
    if has_3d:
        lines.append('import QtQuick3D')
    lines += [
        'import QmlVcp.Controls 1.0',
        '',
    ]
    lines.append(f'// {name}')
    lines.append('Item {')
    lines.append(f'    width: {w}')
    lines.append(f'    height: {h}')
    if bg:
        lines.append(f'    Image {{')
        lines.append(f'        anchors.fill: parent')
        lines.append(f'        source: assetsDir + "/assets/{os.path.basename(bg)}"')
        lines.append(f'        z: -1')
        lines.append(f'    }}')
    lines.append(export_controls_qml(page.get("controls", [])))
    lines.append('}')
    return '\n'.join(lines)


def export_project(project_dir: str, pages: list,
                   project_name: str = "my-cnc",
                   bundle_qmlvcp: bool = False,
                   qmlvcp_src: str = "",
                   qmlvcp_parent: str = "/media/cnc/mydisk",
                   topbar: dict = None,
                   bottombar: dict = None,
                   side_panel: dict = None,
                   standalone: bool = False,
                   window_w: int = 1920,
                   window_h: int = 1080,
                   stack_current_index: int = 0) -> list:
    """导出完整项目到指定目录。

    参数:
        pages:          页面列表 [{"name","controls","bg","width","height"},...]
        bundle_qmlvcp:  是否将 qmlvcp 框架复制到项目中
        qmlvcp_src:     qmlvcp 框架源路径（bundle 时使用）
        qmlvcp_parent:  外部 qmlvcp 的父目录（引用模式时使用）
        topbar:         顶部导航栏（可选）
        bottombar:      底部状态栏（可选）
        side_panel:     右侧面板（可选）
        window_w/h:     全局窗口尺寸

    返回: 创建的文件路径列表
    """
    os.makedirs(os.path.join(project_dir, "qml"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "qml", "pages"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "assets"), exist_ok=True)

    files = []

    # 复制 qmlvcp（如果勾选）
    if bundle_qmlvcp and qmlvcp_src and os.path.isdir(qmlvcp_src):
        dst = os.path.join(project_dir, "qmlvcp")
        _copy_dir(qmlvcp_src, dst, skip_pycache=True)
        files.append(f"{dst}/ (框架已内嵌)")

    # 子页面文件 (page1.qml, page2.qml...)
    for page in pages[1:]:
        name = page.get("name", "page")
        page_path = os.path.join(project_dir, "qml", "pages", f"{name}.qml")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(generate_page_qml(page))
        files.append(page_path)

    # Main.qml (多页，引用 pages/*.qml)
    qml_path = os.path.join(project_dir, "qml", "Main.qml")
    with open(qml_path, "w", encoding="utf-8") as f:
        f.write(generate_main_qml_multi(pages, topbar, bottombar, side_panel, standalone, window_w, window_h, stack_current_index))
    files.append(qml_path)

    # project.json — 保存完整数据（页面+区域），供 Builder 重新导入
    json_path = os.path.join(project_dir, "qml", "project.json")
    _save_project_json(json_path, pages, side_panel, topbar, bottombar, window_w, window_h)
    files.append(json_path)

    # qmldir
    qmldir_path = os.path.join(project_dir, "qml", "qmldir")
    with open(qmldir_path, "w") as f:
        f.write(f"module {project_name}\n")
    files.append(qmldir_path)

    # main.py
    main_path = os.path.join(project_dir, "main.py")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(generate_main_py(project_name, bundle_qmlvcp, qmlvcp_parent))
    files.append(main_path)

    # backend.py
    backend_path = os.path.join(project_dir, "backend.py")
    with open(backend_path, "w", encoding="utf-8") as f:
        f.write(generate_backend_py())
    files.append(backend_path)

    # requirements.txt
    req_path = os.path.join(project_dir, "requirements.txt")
    with open(req_path, "w") as f:
        from builder.templates.pfile import load_requirements
        f.write(load_requirements())
    files.append(req_path)

    # start.sh (Linux) / start.bat (Windows)
    if sys.platform != "win32":
        start_path = os.path.join(project_dir, "start.sh")
        from builder.templates.pfile import load_start_sh
        with open(start_path, "w") as f:
            f.write(load_start_sh())
        import stat
        os.chmod(start_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        files.append(start_path)
    else:
        start_path = os.path.join(project_dir, "start.bat")
        from builder.templates.pfile import load_start_bat
        with open(start_path, "w") as f:
            f.write(load_start_bat())
        files.append(start_path)

    return files


def _copy_dir(src: str, dst: str, skip_pycache: bool = True):
    """递归复制目录，跳过 __pycache__ 和 .pyc。"""
    import shutil
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(
        src, dst,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", "*.cpp"
        ) if skip_pycache else None,
    )


# 控件字段中可能包含文件路径的键
_CONTROL_PATH_KEYS = {"src", "pressedSource", "pressedSrc", "bg"}


def _clean_control_paths(controls: list):
    """将控件中的路径字段转为文件名（与 bg 处理一致）。"""
    for ctrl in controls:
        for key in _CONTROL_PATH_KEYS:
            val = ctrl.get(key, "")
            if val:
                ctrl[key] = os.path.basename(val)


def _restore_control_paths(controls: list, project_dir: str):
    """将控件中的路径字段从文件名还原为 assets 目录的绝对路径。"""
    assets_dir = os.path.join(project_dir, "assets")
    for ctrl in controls:
        for key in _CONTROL_PATH_KEYS:
            val = ctrl.get(key, "")
            if val and not os.path.isabs(val):
                ctrl[key] = os.path.join(assets_dir, val)


def _save_project_json(path: str, pages: list,
                       side_panel: dict = None,
                       topbar: dict = None,
                       bottombar: dict = None,
                       window_w: int = 1920,
                       window_h: int = 1080):
    """导出完整数据到 JSON（页面+区域，供 Builder 重新导入）。"""
    import json

    def _clean_zone(zone):
        """复制区域数据，bg 及控件内路径仅保留文件名。"""
        if not zone:
            return None
        z = dict(zone)
        if z.get("bg"):
            z["bg"] = os.path.basename(z["bg"])
        z["controls"] = [dict(c) for c in z.get("controls", [])]
        _clean_control_paths(z["controls"])
        return z

    clean_pages = []
    for p in pages:
        cp = dict(p)
        if cp.get("bg"):
            cp["bg"] = os.path.basename(cp["bg"])
        cp["controls"] = [dict(c) for c in cp.get("controls", [])]
        _clean_control_paths(cp["controls"])
        clean_pages.append(cp)

    data = {
        "pages": clean_pages,
        "side_panel": _clean_zone(side_panel),
        "topbar": _clean_zone(topbar),
        "bottombar": _clean_zone(bottombar),
        "window_w": window_w,
        "window_h": window_h,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _has_control(pages: list, ctype: str) -> bool:
    """检查多页结构中是否包含指定类型的控件。"""
    for page in pages:
        for ctrl in page.get("controls", []):
            if ctrl.get("type") == ctype:
                return True
    return False


def _has_control_page(page: dict, ctype: str) -> bool:
    """检查单个页面中是否包含指定类型的控件。"""
    return _has_control([page], ctype)


def _canvas_kids(all_ctrls: list, canvas_idx: int, skip_idxs: set = None) -> list:
    """返回画布的所有子控件（不受 z 影响）。
    skip_idxs: 需要跳过的索引集合（画布、置顶控件等）。"""
    skip = skip_idxs or set()
    return [c for i, c in enumerate(all_ctrls)
            if i not in skip
            and c.get("_parent_id") is not None
            and str(c.get("_parent_id", "")) == str(canvas_idx)]
