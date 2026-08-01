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
主窗口 — QmlVcp Builder 的主界面。
三个标签页: 环境设置 / 界面拼装 / 项目导出
"""

import copy
import os
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QComboBox, QSpinBox, QLineEdit, QFileDialog,
    QTextEdit, QGroupBox, QFormLayout, QMessageBox,
    QHeaderView, QProgressBar, QCheckBox, QScrollArea, QShortcut,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QKeySequence

from builder.env_setup import EnvManager
from builder.project_exporter import export_project
from builder.preview_canvas import PreviewCanvas, _setup_combo_search
from builder.properties_mixin import PropertiesMixin
from builder.controls import (
    ACTIONS, STATUS_BINDS, get_display_list, get_defaults, get_properties
)

WINDOW_TITLE = "QmlVcp Builder — CNC 界面拼装工具"
DEFAULT_W = 1280
DEFAULT_H = 800


class MainWindow(PropertiesMixin, QMainWindow):

    @staticmethod
    def _i(v, d=0):
        """安全转 int（字符串也能转）。"""
        if v is None or v == "":
            return d
        try:
            return int(v)
        except (TypeError, ValueError):
            return d

    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(DEFAULT_W, DEFAULT_H)

        self._project_dir = os.path.expanduser("~/my-cnc")

        # ═══ 新架构：分区模型 ═══
        # 页面列表 + 右侧面板 + 顶部导航 + 底部状态
        self._pages = [{"name": "mainwindow", "controls": [], "bg": "",
                        "x": 0, "y": 0, "width": 1375, "height": 1000}]
        self._side_panel = {"bg": "", "x": 1375, "y": 0,
                            "width": 545, "height": 1000, "controls": []}
        self._topbar = {"width": 1440, "height": 80, "controls": []}
        self._bottombar = {"controls": []}
        self._current_page = 0
        self._edit_mode = "page"  # "page" / "side_panel" / "topbar" / "bottombar"

        # 全局窗口尺寸（用户可改，导出时使用）
        self._window_w = 1920
        self._window_h = 1080
        self._canvas_original_w = None  # 取消"宽跟随窗口"时恢复用
        self._stack_current_index = 0  # StackLayout currentIndex: 0=主页0, 1=主页1
        self._zone_edit_focus = "page"  # 当前编辑哪个区域的基础属性: "page" / "side_panel"
        self._undo_stack = []   # [(pages_snapshot, side_panel_snapshot, current_page, sel_index, edit_mode), ...]
        self._redo_stack = []
        self._undo_needs_push = True  # 每次选中变化后首次属性修改才入栈
        self._clipboard = None  # 复制的控件数据 {dict}

        # ── 从 mainwindow.ui 加载骨架 ──
        from PyQt5 import uic as _uic
        _ui_path = os.path.join(os.path.dirname(__file__), "mainwindow.ui")
        _uic.loadUi(_ui_path, self)

        # 初始数据回填到 .ui 控件
        self.dirEdit.setText(self._project_dir)
        self.winWSpin.setValue(self._window_w)
        self.winHSpin.setValue(self._window_h)
        self.mainTabs.setCurrentIndex(1)
        self.envProgress.setRange(0, 0)
        self.envProgress.hide()

        # ═══ 信号连接 (.ui 静态控件) ═══
        self.btnBrowse.clicked.connect(self._browse_dir)
        self.btnExport.clicked.connect(self._do_export)
        self.btnOpenProject.clicked.connect(self._open_project)
        self.btnPreview.clicked.connect(self._open_project_dir)
        self.winWSpin.valueChanged.connect(self._on_window_size_changed)
        self.winHSpin.valueChanged.connect(self._on_window_size_changed)
        self.chkMatchWinW.toggled.connect(self._on_match_win_w_toggled)
        self.btnCreateVenv.clicked.connect(self._on_create_venv)
        self.btnInstallPySide6.clicked.connect(self._on_install_pyside6)
        self.chkStackIdx.toggled.connect(self._on_stack_idx_toggled)
        self.btnZoneToggle.clicked.connect(self._on_toggle_zone_focus)
        self.btnDelPage.clicked.connect(self._del_page)
        self.btnAddPage.clicked.connect(self._add_page)
        self.btnAddCanvas.clicked.connect(self._add_canvas)
        self.ctrlList.itemDoubleClicked.connect(self._add_control)
        self.btnAddControl.clicked.connect(self._add_control)
        self.btnDeleteControl.clicked.connect(self._delete_control)
        self.btnRefreshPreview.clicked.connect(self._refresh_preview)
        self.chkBundle.stateChanged.connect(self._refresh_preview)
        self.chkStandalone.stateChanged.connect(self._refresh_preview)
        self.btnZoomOut.clicked.connect(self._zoom_out)
        self.btnZoomReset.clicked.connect(self._zoom_reset)
        self.btnZoomIn.clicked.connect(self._zoom_in)
        self.dirEdit.textChanged.connect(lambda t: setattr(self, '_project_dir', t))

        # ═══ 组装动态控件 (从 _build_* 迁移) ═══
        self._setup_export_tab()
        self._setup_assembly_tab()

        self._update_env_status()
        self._on_window_size_changed()  # 初始化自动分配左右区域宽度（含 _apply_zoom + _refresh_canvas）
        self._canvas._page_offset = (0, 0, self._pages[0]["width"], self._pages[0]["height"])
        self._on_canvas_select(-1)  # 默认显示画布属性
        self._setup_shortcuts()
        self.showMaximized()

    @property
    def _active_controls(self):
        """当前编辑模式的控件列表 (setter 同步写回对应的数据区)。"""
        if self._edit_mode == "side_panel":
            return self._side_panel["controls"]
        elif self._edit_mode == "topbar":
            return self._topbar["controls"]
        elif self._edit_mode == "bottombar":
            return self._bottombar["controls"]
        return self._page["controls"]

    @property
    def _active_bg(self):
        """当前编辑模式的背景。"""
        if self._edit_mode == "side_panel":
            return self._side_panel.get("bg", "")
        return self._page.get("bg", "")

    @property
    def _page(self): return self._pages[self._current_page]

    def _on_window_size_changed(self):
        """全局窗口尺寸变化时更新数据。"""
        self._window_w = self.winWSpin.value()
        self._window_h = self.winHSpin.value()
        # 自动分配左右区域：主页宽 = 窗口宽 - 侧栏宽，侧栏 x = 主页宽
        sp_w = self._side_panel.get("width", 545)
        page = self._pages[0] if self._pages else {"x": 0, "y": 0, "height": self._window_h}
        page["width"] = max(200, self._window_w - sp_w)
        page["x"] = 0
        self._side_panel["x"] = page["width"]
        self._side_panel["y"] = page.get("y", 0)
        self._side_panel["height"] = page.get("height", self._window_h)
        # 若勾选了"宽跟随窗口"，同步改画布宽度
        if hasattr(self, '_chk_match_win_w') and self.chkMatchWinW.isChecked():
            zone = self._get_zone_data()
            zone["width"] = self._window_w
        # 更新属性栏显示（若当前正在看区域属性）
        if self._canvas._sel_index < 0:
            zone = self._get_zone_data()
            self._prop_w.blockSignals(True)
            self._prop_w.setValue(self._window_w if (hasattr(self, '_chk_match_win_w') and self.chkMatchWinW.isChecked()) else zone.get("width", 1024))
            self._prop_w.blockSignals(False)
        self._canvas._page_offset = (page["x"], page["y"], page["width"], page["height"])
        self._canvas._apply_zoom(page["width"], page["height"])
        self._refresh_canvas()

    def _on_match_win_w_toggled(self, checked: bool):
        """勾选/取消'宽跟随窗口'。"""
        page = self._pages[0] if self._pages else {"width": self._window_w}
        sp_w = self._side_panel.get("width", 545)
        if checked:
            self._canvas_original_w = page.get("width", self._prop_w.value())
            page["width"] = self._window_w
        else:
            if self._canvas_original_w is not None:
                page["width"] = self._canvas_original_w
            else:
                page["width"] = max(200, self._window_w - sp_w)
        self._side_panel["x"] = page["width"]
        self.chkMatchWinW.setText("编辑中禁止导出....." if checked else "已可以允许导出....")
        self._prop_w.blockSignals(True)
        self._prop_w.setValue(page["width"])
        self._prop_w.blockSignals(False)
        self._canvas._page_offset = (page.get("x", 0), page.get("y", 0), page["width"], page.get("height", self._window_h))
        self._canvas._apply_zoom(page["width"], page.get("height", self._window_h))
        self._refresh_canvas()

    def _update_chk_match_win_w_state(self):
        """只有主页面 (page 0) 才可用'宽跟随窗口'复选框。"""
        if hasattr(self, '_chk_match_win_w'):
            self.chkMatchWinW.setEnabled(self._current_page == 0)

    def _on_stack_idx_toggled(self, checked: bool):
        """StackLayout currentIndex 切换: 打勾=0(主页0), 取消=1(主页1)。"""
        self._stack_current_index = 0 if checked else 1
        self.chkStackIdx.setText("主页0" if checked else "主页1")

    def _on_toggle_zone_focus(self):
        """切换编辑左侧/右侧区域的基础属性。"""
        if self._zone_edit_focus == "page":
            self._zone_edit_focus = "side_panel"
            self._edit_mode = "side_panel"
            self.btnZoneToggle.setText("右侧")
        else:
            self._zone_edit_focus = "page"
            self._edit_mode = "page"
            self.btnZoneToggle.setText("左侧")
        # 取消控件选中，显示区域属性
        self._canvas._sel_index = -1
        self._show_page_props()

    # ═══════════════════════════════════════════
    #  快捷键
    # ═══════════════════════════════════════════

    def _setup_shortcuts(self):
        """注册全局快捷键。"""
        QShortcut(QKeySequence("Ctrl+S"), self, self._do_export)
        QShortcut(QKeySequence("Delete"), self, self._delete_control)
        QShortcut(QKeySequence("Ctrl+Z"), self, self._perform_undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self._perform_redo)
        QShortcut(QKeySequence("Ctrl+C"), self, self._copy_control)
        QShortcut(QKeySequence("Ctrl+V"), self, self._paste_control)

    # ═══════════════════════════════════════════
    #  撤销 / 重做
    # ═══════════════════════════════════════════

    def _snapshot_state(self):
        """返回当前编辑状态的深拷贝快照。"""
        return (
            copy.deepcopy(self._pages),
            copy.deepcopy(self._side_panel),
            self._current_page,
            self._canvas._sel_index,
            self._edit_mode,
        )

    def _restore_state(self, snapshot):
        """从快照恢复编辑状态。"""
        pages, side_panel, current_page, sel_index, edit_mode = snapshot
        self._pages = pages
        self._side_panel = side_panel
        self._current_page = current_page
        self._edit_mode = edit_mode
        self._canvas._sel_index = sel_index
        if sel_index >= 0:
            self._refresh_props(sel_index)
        else:
            self._show_page_props()
        self._refresh_canvas()

    def _push_undo_snapshot(self):
        """在修改前保存当前状态到撤销栈。"""
        self._undo_stack.append(self._snapshot_state())
        self._redo_stack.clear()  # 新操作清空重做栈
        self._undo_needs_push = False  # 本轮属性修改已入栈

    def _perform_undo(self):
        """Ctrl+Z: 撤销上一步。"""
        if not self._undo_stack:
            return
        self._redo_stack.append(self._snapshot_state())
        self._restore_state(self._undo_stack.pop())
        self._undo_needs_push = True  # 恢复后允许新的 push

    def _perform_redo(self):
        """Ctrl+Shift+Z: 重做。"""
        if not self._redo_stack:
            return
        self._undo_stack.append(self._snapshot_state())
        self._restore_state(self._redo_stack.pop())
        self._undo_needs_push = True

    def _get_zone_bg(self):
        """获取当前编辑区的背景图路径。"""
        if self._edit_mode == "side_panel":
            return self._side_panel.get("bg", "")
        elif self._edit_mode == "page":
            return self._page.get("bg", "")
        return ""

    def _switch_page(self, idx):
        """保存当前页状态，切换到第 idx 页。"""
        if idx == self._current_page or idx < 0 or idx >= len(self._pages):
            return
        self._page["controls"] = self._canvas._controls
        self._current_page = idx
        pg = self._pages[idx]
        bg = pg.get("bg", "")
        if bg and os.path.exists(bg):
            self._canvas._loaded_bg_path = bg
            self._canvas.loadBackground(bg, bgW=pg.get("bgW", 0), bgH=pg.get("bgH", 0))
            self.lblBg.setText(f"背景: {os.path.basename(bg)}")
        else:
            self._canvas._bg_pixmap = None
            self._canvas._loaded_bg_path = ""
            self._canvas.clear()
            self.lblBg.setText("未加载背景")
        self._canvas._page_offset = (pg.get("x", 0), pg.get("y", 0),
                                     pg.get("width", 1024), pg.get("height", 768))
        self._canvas._apply_zoom(pg.get("width", 1024), pg.get("height", 768))
        self._canvas.setControls(pg.get("controls", []))
        self._canvas._sel_index = -1
        self._refresh_page_tabs()
        self._update_chk_match_win_w_state()
        self._on_canvas_select(-1)

    def _add_canvas(self):
        """在当页新建画布 (Item)，与 StackLayout 平级。"""
        n = sum(1 for c in self._page["controls"] if c.get("canvas")) + 1
        canvas = {"type": "Rectangle", "canvas": True,
                  "x": 0, "y": 0, "w": 400, "h": 300,
                  "bgColor": "#2d3040", "opacity": 100,
                  "border": True, "borderW": 1, "borderC": "#666",
                  "container": True}
        canvas["x"] = len(self._page["controls"]) * 90
        canvas["y"] = 10
        self._page["controls"].append(canvas)
        self._refresh_canvas()

    def _add_page(self):
        n = len(self._pages)
        self._pages.append({"name": f"page{n}", "controls": [], "bg": "",
                            "x": 0, "y": 0, "width": 1024, "height": 768})
        self._rebuild_page_bar()
        self._switch_page(len(self._pages) - 1)

    def _del_page(self):
        if self._current_page == 0:
            return  # mainwindow 不可删除
        old = self._current_page
        self._switch_page(0)
        self._pages.pop(old)
        self._rebuild_page_bar()

    def _rebuild_page_bar(self):
        """重建页面标签按钮（新增/删除页面时调用）。"""
        self._rebuild_page_tabs()

    def _rename_page(self, idx):
        """双击标签改名。"""

    def _page_menu(self, pos, idx):
        """页面标签右键菜单。"""
        from PyQt5.QtWidgets import QMenu, QInputDialog
        menu = QMenu(self)
        act_rename = menu.addAction("重命名")
        action = menu.exec_(self._page_btns[idx].mapToGlobal(pos))
        if action == act_rename:
            old = self._pages[idx]["name"]
            new, ok = QInputDialog.getText(self, "重命名页面", "名称:", text=old)
            if ok and new.strip():
                self._pages[idx]["name"] = new.strip()
                self._page_btns[idx].setText(new.strip())

    def _refresh_page_tabs(self):
        """更新页签按钮的选中状态。"""
        if hasattr(self, '_page_btns'):
            for i, btn in enumerate(self._page_btns):
                btn.setChecked(i == self._current_page)
        if hasattr(self, '_btn_del_pg'):
            self.btnDelPage.setEnabled(self._current_page != 0)

    # ═══════════════════════════════════════════
    #  UI 构建
    # ═══════════════════════════════════════════

    # ═══════════════════════════════════════════
    #  ① 环境设置标签页
    # ═══════════════════════════════════════════

    # _build_env_tab 已删除 — .ui 文件提供完整骨架
    # envProgress/btnCreateVenv 等控件初始状态在 __init__ 中设置

    # ═══════════════════════════════════════════
    #  ② 界面拼装标签页
    # ═══════════════════════════════════════════

    def _setup_assembly_tab(self):
        """用 .ui 骨架组装界面拼装标签页的动态控件。"""

        # ── 左: 填充控件列表 ──
        self.ctrlList.clear()
        for entry in get_display_list():
            item = QListWidgetItem(entry["name"])
            item.setData(Qt.UserRole, entry["type"])
            if entry["type"] is None:
                item.setFlags(Qt.NoItemFlags)
            self.ctrlList.addItem(item)

        # ── 中: 页面按钮 ──
        self._rebuild_page_tabs()

        # ── 中: 画布 ──
        self._canvas = PreviewCanvas()
        self._canvas.controlSelected.connect(self._on_canvas_select)
        self._canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self._canvas.customContextMenuRequested.connect(self._canvas_menu)
        self._canvas.setParent(self.canvasViewport)
        self._canvas.show()

        # ── 右: 属性表单 ──
        self._build_property_form()

    def _rebuild_page_tabs(self):
        """在 pageBarLayout 中重建页面标签按钮 (动态)。"""
        from PyQt5.QtGui import QFont as _QF
        from PyQt5.QtWidgets import QPushButton as _QPB
        layout = self.canvasArea.layout().itemAt(0).layout()  # pageBarLayout
        # 移除旧的页面按钮 (保留 QLabel[0], btnDelPage, btnAddPage, spacer)
        cnt = layout.count()
        while cnt > 1:
            item = layout.itemAt(1)
            if not item:
                break
            w = item.widget()
            if w is self.btnDelPage:
                break
            if w:
                w.hide()
                w.deleteLater()
            layout.removeItem(item)
            cnt = layout.count()

        self._page_btns = []
        page_font = _QF("Arial", 10, _QF.Bold)
        for i in range(len(self._pages)):
            btn = _QPB(self._pages[i]["name"])
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setFixedSize(100, 30)
            btn.setFont(page_font)
            idx = i
            btn.clicked.connect(lambda checked, p=idx: self._switch_page(p))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, p=idx: self._page_menu(pos, p))
            self._page_btns.append(btn)
            layout.insertWidget(layout.count() - 3, btn)

    def _setup_export_tab(self):
        """初始化导出标签页 (.ui 已提供骨架)"""
        self.exportPreview.setFont(QFont("Courier New", 10))

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择项目目录", self._project_dir)
        if d:
            self._project_dir = d
            self.dirEdit.setText(d)
            self._update_env_status()

    def _open_project_dir(self):
        """运行导出的项目程序。"""
        import subprocess, sys
        from PyQt5.QtWidgets import QMessageBox
        path = self._project_dir
        if sys.platform == "win32":
            main_py = os.path.join(path, "main.py")
            if not os.path.isfile(main_py):
                QMessageBox.warning(self, "错误", f"未找到 main.py，请先导出项目。\n{main_py}")
                return
            try:
                subprocess.Popen(
                    [sys.executable, "main.py"],
                    cwd=path,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                self.statusLabel.setText("项目已启动")
            except Exception as e:
                QMessageBox.critical(self, "启动失败", str(e))
        else:
            # Linux / macOS
            start_sh = os.path.join(path, "start.sh")
            if os.path.isfile(start_sh):
                runner, entry = "bash", "start.sh"
            else:
                runner, entry = sys.executable, "main.py"
                if not os.path.isfile(os.path.join(path, entry)):
                    QMessageBox.warning(self, "错误",
                        f"未找到 {entry}，请先导出项目。\n{os.path.join(path, entry)}")
                    return
            try:
                subprocess.Popen(
                    [runner, entry],
                    cwd=path,
                )
                self.statusLabel.setText("项目已启动")
            except Exception as e:
                QMessageBox.critical(self, "启动失败", str(e))

    def _update_env_status(self):
        mgr = EnvManager(self._project_dir)
        ve = mgr.venv_exists
        sys_ps6 = mgr.system_has_pyside6
        if ve:
            self.lblVenv.setText("✅ 已创建")
            self.lblVenv.setToolTip(f"虚拟环境: {mgr.venv_dir}")
        elif sys_ps6:
            self.lblVenv.setText("⚡ 可选（系统已有 PySide6）")
            self.lblVenv.setToolTip("系统 Python 已自带 PySide6，可不创建 venv")
        else:
            self.lblVenv.setText("❌ 未创建")
            self.lblVenv.setToolTip("请点击「创建虚拟环境」在项目目录下创建 venv")
        has_ps6 = mgr.pyside6_installed
        self.lblPySide6.setText("✅ 已安装" if has_ps6 else "❌ 未安装")
        self.lblPySide6.setToolTip(
            "PySide6 已在 venv 或系统 Python 中检测到" if has_ps6
            else "请创建 venv 后点击「安装 PySide6」"
        )
        self.btnCreateVenv.setEnabled(not has_ps6)
        self.btnInstallPySide6.setEnabled(not has_ps6)

    def _on_create_venv(self):
        self.envLog.clear()
        self.envProgress.show()
        self.btnCreateVenv.setEnabled(False)

        mgr = EnvManager(self._project_dir)
        mgr.statusChanged.connect(self.envLog.append)
        mgr.finished.connect(self._on_venv_done)
        mgr.create_venv()

    def _on_venv_done(self, ok, msg):
        self.envProgress.hide()
        self.btnCreateVenv.setEnabled(True)
        self._update_env_status()

    def _on_install_pyside6(self):
        mgr = EnvManager(self._project_dir)
        if not mgr.venv_exists:
            QMessageBox.warning(self, "提示", "请先创建虚拟环境")
            return

        self.envLog.clear()
        self.envProgress.show()
        self.btnInstallPySide6.setEnabled(False)

        mgr.statusChanged.connect(self.envLog.append)
        mgr.finished.connect(self._on_pyside6_done)
        mgr.install_pyside6()

    def _on_pyside6_done(self, ok, msg):
        self.envProgress.hide()
        self.btnInstallPySide6.setEnabled(True)
        self._update_env_status()

    # ═══════════════════════════════════════════
    #  事件处理 — 界面拼装
    # ═══════════════════════════════════════════

    # _load_bg 已移除，背景图改为属性面板编辑

    def _add_control(self, item=None):
        try:
            if item is None:
                item = self.ctrlList.currentItem()
            if item is None:
                return
            ctype = item.data(Qt.UserRole) if isinstance(item, QListWidgetItem) else item
            if ctype is None:
                return  # 分隔符
            template = get_defaults(ctype)
            if template is None:
                return
            # 取当前页面同类型控件中的最大序号，+1 避免 QML id 重复
            _QML_PFX = {
                "ImageButton": "btn", "JOGButton": "jogBtn", "SpriteButton": "sprBtn", "LED": "led",
                "MachTextInput": "input", "GCodeGraphics": "gcode3d",
                "GCodeViewer": "gcodeViewer", "RunFromHereDialog": "runFromHere",
                "Text (DRO)": "dro", "Text (Label)": "label", "Image": "img",
                "TextField": "cmdInput", "Timer": "timer", "Rectangle": "rect",
                "FileDialog": "fileDlg",
                "EmergencyStop": "estop",
            }
            pfx = _QML_PFX.get(ctype, "ctrl")
            max_num = 0
            for c in self._active_controls:
                cid = c.get("id", "")
                no = cid[len(pfx):] if cid.startswith(pfx) else ""
                if no.isdigit():
                    max_num = max(max_num, int(no))
            template["id"] = f"{pfx}{max_num + 1}"
            # 将新控件放在当前视口中心（右区需减去面板偏移）
            zoom = self._canvas._zoom
            hbar = self.canvasScroll.horizontalScrollBar()
            vbar = self.canvasScroll.verticalScrollBar()
            vp = self.canvasScroll.viewport()
            center_x = (hbar.value() + vp.width() // 2) / zoom
            center_y = (vbar.value() + vp.height() // 2) / zoom
            if self._edit_mode == "side_panel":
                center_x -= self._canvas._sp_ox
                center_y -= self._canvas._sp_oy
            template["x"] = max(0, int(center_x - template.get("w", 80) / 2))
            template["y"] = max(0, int(center_y - template.get("h", 40) / 2))
            self._push_undo_snapshot()
            self._active_controls.append(template)

            self._refresh_canvas()
        except Exception as e:
            print(f"[Builder] _add_control error: {e}")

    def _refresh_canvas(self):
        """刷新画布：左右控件同步渲染 + 加载背景图。"""
        # 左侧
        pg = self._page
        self._canvas.setControls(pg.get("controls", []))
        left_bg = pg.get("bg", "")
        if left_bg and os.path.exists(left_bg):
            self._canvas._bg_pixmap = QPixmap(left_bg)
            self._canvas._bg_w = pg.get("bgW", 0)
            self._canvas._bg_h = pg.get("bgH", 0)
        else:
            self._canvas._bg_pixmap = None
            self._canvas._bg_w = 0
            self._canvas._bg_h = 0

        # 右侧
        self._canvas.setRightControls(self._side_panel.get("controls", []))
        sp_x = self._side_panel.get("x", 0)
        sp_y = self._side_panel.get("y", 0)
        self._canvas.setSidePanelOffset(sp_x, sp_y)
        right_bg = self._side_panel.get("bg", "")
        if right_bg and os.path.exists(right_bg):
            self._canvas._right_bg_pixmap = QPixmap(right_bg)
        else:
            self._canvas._right_bg_pixmap = None

        self._canvas.update()

    def _canvas_menu(self, pos: QPoint):
        """画布右键菜单。"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("选择贴图…", self._pick_image_for_control)
        # 放入容器：仅非容器控件可见
        si = self._canvas._sel_index
        if si >= 0:
            ctrls = self._active_controls
            c = ctrls[si]
            if not (c.get("type") == "Rectangle" and c.get("container")):
                containers = [(i, cc) for i, cc in enumerate(ctrls)
                              if cc.get("type") == "Rectangle" and cc.get("container")]
                if containers:
                    sub = menu.addMenu("放入容器")
                    sub.addAction("(取消/独立)", lambda: self._assign_container(-1))
                    for ci, cc in containers:
                        name = cc.get("text", "") or f"容器#{ci}"
                        sub.addAction(name, lambda p=ci: self._assign_container(p))
            menu.addSeparator()
            menu.addAction("复制", self._copy_control)
            menu.addAction("删除", self._delete_control)
        if self._clipboard is not None:
            menu.addAction("粘贴", self._paste_control)
        menu.exec_(self._canvas.mapToGlobal(pos))

    def _assign_container(self, idx: int):
        """将选中控件分配给第 idx 个容器，-1 取消并还原为原始绝对坐标。"""
        si = self._canvas._sel_index
        if si < 0:
            return
        controls = self._active_controls
        old_pid = controls[si].get("_parent_id")
        if idx >= 0:
            container = controls[idx]
            if old_pid and old_pid != str(idx):
                # 从旧容器移出还原绝对坐标
                old_cont = controls[int(old_pid)]
                controls[si]["x"] += old_cont.get("x", 0)
                controls[si]["y"] += old_cont.get("y", 0)
            controls[si]["_parent_id"] = str(idx)
            # 转为相对于新容器的坐标
            controls[si]["x"] -= container.get("x", 0)
            controls[si]["y"] -= container.get("y", 0)
        else:
            if old_pid:
                # 还原绝对坐标
                container = controls[int(old_pid)]
                controls[si]["x"] += container.get("x", 0)
                controls[si]["y"] += container.get("y", 0)
            controls[si].pop("_parent_id", None)
        self._refresh_canvas()

    def _zoom_in(self):
        self._canvas.zoomIn()
        self.lblZoom.setText(f"{int(self._canvas.zoom * 100)}%")

    def _zoom_out(self):
        self._canvas.zoomOut()
        self.lblZoom.setText(f"{int(self._canvas.zoom * 100)}%")

    def _zoom_reset(self):
        self._canvas.zoomReset()
        self.lblZoom.setText("100%")

    def _get_zone_data(self):
        """返回当前编辑区的数据 dict（用于读写尺寸/背景等属性）。"""
        if self._edit_mode == "side_panel":
            return self._side_panel
        elif self._edit_mode == "topbar":
            return self._topbar
        elif self._edit_mode == "bottombar":
            return self._bottombar
        return self._page

    def _get_zone_name(self):
        """返回当前编辑区的显示名称。"""
        names = {"page": "页面", "side_panel": "右侧面板",
                 "topbar": "顶部导航", "bottombar": "底部状态"}
        return names.get(self._edit_mode, "页面")

    def _delete_control(self):
        idx = self._canvas._sel_index
        if idx >= 0:
            self._push_undo_snapshot()
            del self._active_controls[idx]
            self._canvas._sel_index = -1
            self._refresh_canvas()
            self._show_page_props()  # 清空属性面板，避免显示已删除控件的信息

    def _copy_control(self):
        """复制当前选中的控件到剪贴板。"""
        idx = self._canvas._sel_index
        if idx >= 0:
            self._clipboard = copy.deepcopy(self._active_controls[idx])

    def _paste_control(self):
        """粘贴剪贴板中的控件到当前页面，偏移 20px 避免重叠。"""
        if self._clipboard is None:
            return
        self._push_undo_snapshot()
        new_ctrl = copy.deepcopy(self._clipboard)
        # 生成新的 id（后缀 +1）
        import re
        base = re.sub(r'\d+$', '', new_ctrl.get("id", "ctrl"))
        nums = [int(re.search(r'(\d+)$', c.get("id", "")).group(1))
                for c in self._active_controls if c.get("id", "").startswith(base) and re.search(r'(\d+)$', c.get("id", ""))]
        new_num = max(nums, default=0) + 1
        new_ctrl["id"] = f"{base}{new_num}"
        # 偏移位置
        new_ctrl["x"] = new_ctrl.get("x", 0) + 20
        new_ctrl["y"] = new_ctrl.get("y", 0) + 20
        self._active_controls.append(new_ctrl)
        self._canvas._sel_index = len(self._active_controls) - 1
        self._refresh_props(self._canvas._sel_index)
        self._undo_needs_push = True
        self._refresh_canvas()

    # ═══════════════════════════════════════════
    #  事件处理 — 导出
    # ═══════════════════════════════════════════

    def _open_project(self):
        """从已导出的项目目录导入完整数据（页面 + 区域）。"""
        d = QFileDialog.getExistingDirectory(self, "打开项目目录", self._project_dir)
        if not d:
            return
        try:
            from builder.project_importer import import_project
            result = import_project(d)
            pages = result.get("pages", [])
            if not pages:
                QMessageBox.warning(self, "提示", "未找到可导入的页面")
                return

            self._pages = pages
            self._current_page = 0
            self._project_dir = d
            self.dirEdit.setText(d)

            # 还原窗口尺寸（先关信号避免 setValue 交叉触发覆盖）
            self.winWSpin.blockSignals(True)
            self.winHSpin.blockSignals(True)
            self._window_w = result.get("window_w", self._window_w)
            self._window_h = result.get("window_h", self._window_h)
            self.winWSpin.setValue(self._window_w)
            self.winHSpin.setValue(self._window_h)
            self.winWSpin.blockSignals(False)
            self.winHSpin.blockSignals(False)

            # 还原区域数据
            if result.get("side_panel"):
                self._side_panel = result["side_panel"]
            if result.get("topbar"):
                self._topbar = result["topbar"]
            if result.get("bottombar"):
                self._bottombar = result["bottombar"]

            # 重建页面标签和画布
            self._rebuild_page_tabs()
            self._canvas._apply_zoom(self._window_w, self._window_h)
            self._canvas._page_offset = (0, 0, self._window_w, self._window_h)
            self._refresh_canvas()
            self._on_canvas_select(-1)
            self._update_env_status()

            # 提示信息
            msg = f"已导入 {len(pages)} 个页面\n主页: {pages[0]['name']}"
            if self._side_panel.get("controls"):
                msg += f"\n右侧面板: {len(self._side_panel['controls'])} 控件"
            if self._topbar.get("controls"):
                msg += f"\n顶部导航: {len(self._topbar['controls'])} 控件"
            if self._bottombar.get("controls"):
                msg += f"\n底部状态: {len(self._bottombar['controls'])} 控件"
            QMessageBox.information(self, "完成", msg)
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _refresh_preview(self):
        from builder.project_exporter import generate_main_qml_multi, generate_page_qml
        self._page["controls"] = self._canvas._controls
        standalone = self.chkStandalone.isChecked()
        parts = ["// ======== Main.qml ========",
                 generate_main_qml_multi(self._pages, self._topbar,
                                         self._bottombar, self._side_panel,
                                         standalone,
                                         self._window_w, self._window_h,
                                         self._stack_current_index)]
        for page in self._pages[1:]:
            parts.append(f"\n// ======== pages/{page['name']}.qml ========")
            parts.append(generate_page_qml(page))
        self.exportPreview.setPlainText('\n'.join(parts))

    def _do_export(self):
        if not self._page["controls"] and len(self._pages) == 1:
            QMessageBox.warning(self, "提示", "请先添加至少一个控件")
            return

        bundle = self.chkBundle.isChecked()
        standalone = self.chkStandalone.isChecked()

        # 不 bundle 时确认用户知道需要手动放置 qmlvcp
        if not bundle:
            reply = QMessageBox.question(
                self, "确认",
                "未勾选「框架复制到项目」模式。\n\n"
                "导出的项目需要 qmlvcp 框架放在其上级目录才能运行：\n"
                f"  {os.path.dirname(self._project_dir)}/qmlvcp/\n\n"
                "建议勾选该选项以获得开箱即用的项目。\n"
                "是否继续导出（不复制框架）？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        if bundle:
            self.statusLabel.setText("正在复制 qmlvcp 框架...")
        # 保存当前页
        self._page["controls"] = self._canvas._controls
        files = export_project(
            self._project_dir, self._pages,
            project_name=os.path.basename(self._project_dir),
            bundle_qmlvcp=bundle,
            qmlvcp_src=os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "qmlvcp"
            ),
            topbar=self._topbar,
            bottombar=self._bottombar,
            side_panel=self._side_panel,
            standalone=standalone,
            window_w=self._window_w,
            window_h=self._window_h,
            stack_current_index=self._stack_current_index,
        )
        QMessageBox.information(
            self, "导出完成",
            f"项目已生成到:\n{self._project_dir}\n"
            f"模式: {'自带 qmlvcp' if bundle else '引用外部 qmlvcp'}\n\n"
            + "\n".join(os.path.basename(f) for f in files)
        )
        self.statusLabel.setText("导出完成 ✅")
