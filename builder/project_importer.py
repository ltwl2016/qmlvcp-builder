"""
项目导入模块 — 读取导出的 project.json，还原 builder 的完整数据结构。
"""

import os
import json

# 控件字段中可能包含文件路径的键（与 project_exporter 保持一致）
_CONTROL_PATH_KEYS = {"src", "pressedSource", "pressedSrc", "bg"}


def _clean_controls(controls: list):
    """确保控件数值类型正确（JSON 保存后可能变成 int）。"""
    for ctrl in controls:
        for key in ("x", "y", "w", "h", "fontSize", "decimals",
                    "activeLine", "value", "from", "to",
                    "cameraZoom", "borderThickness", "shrinkAmount"):
            if key in ctrl and ctrl[key] is not None:
                try:
                    ctrl[key] = float(ctrl[key])
                    if ctrl[key] == int(ctrl[key]):
                        ctrl[key] = int(ctrl[key])
                except (TypeError, ValueError):
                    pass


def _restore_control_paths(controls: list, project_dir: str):
    """将控件中的路径字段从文件名还原为 assets 目录的绝对路径。"""
    assets_dir = os.path.join(project_dir, "assets")
    for ctrl in controls:
        for key in _CONTROL_PATH_KEYS:
            val = ctrl.get(key, "")
            if val and not os.path.isabs(val):
                ctrl[key] = os.path.join(assets_dir, val)


def _restore_zone(zone: dict, project_dir: str) -> dict:
    """还原区域的 bg 路径为 assets 目录的绝对路径。"""
    if not zone:
        return zone
    bg = zone.get("bg", "")
    if bg and not os.path.isabs(bg):
        zone["bg"] = os.path.join(project_dir, "assets", bg)
    controls = zone.get("controls", [])
    _clean_controls(controls)
    _restore_control_paths(controls, project_dir)
    return zone


def import_project(project_dir: str) -> dict:
    """从项目目录导入 project.json，返回完整数据结构。

    返回: {
        "pages": [...],
        "side_panel": { ... } or None,
        "topbar": { ... } or None,
        "bottombar": { ... } or None,
        "window_w": int,
        "window_h": int,
    }
    """
    # 优先读 qml/project.json
    json_path = os.path.join(project_dir, "qml", "project.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(project_dir, "project.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"找不到 project.json，请确保项目是通过 Builder 导出的。\n"
            f"查找路径: {json_path}"
        )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 兼容旧格式：旧版直接保存 pages 列表
    if isinstance(data, list):
        pages = data
        zones = {}
    else:
        pages = data.get("pages", [])
        zones = {
            "side_panel": data.get("side_panel"),
            "topbar": data.get("topbar"),
            "bottombar": data.get("bottombar"),
        }

    # 还原 bg 及控件路径
    for page in pages:
        bg = page.get("bg", "")
        if bg and not os.path.isabs(bg):
            page["bg"] = os.path.join(project_dir, "assets", bg)
        ctrls = page.get("controls", [])
        _clean_controls(ctrls)
        _restore_control_paths(ctrls, project_dir)

    result = {
        "pages": pages,
        "window_w": data.get("window_w", 1920),
        "window_h": data.get("window_h", 1080),
    }
    for key, zone in zones.items():
        result[key] = _restore_zone(zone, project_dir) if zone else None

    return result
