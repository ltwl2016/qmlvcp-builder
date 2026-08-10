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

"""PreviewCanvas - canvas control preview area."""
import os
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPoint, QRect
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPen, QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel, QComboBox, QCompleter, QWidget
from lang import Tr

class SelectionRect:
    """画布上选中的控件框。"""
    def __init__(self, x=0, y=0, w=50, h=30, color=Qt.green):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def rect(self):
        return QRect(self.x, self.y, self.w, self.h)

class PreviewCanvas(QLabel):
    """双区域预览画布 — 同时渲染左右控区。"""
    controlSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setStyleSheet("background: #d0d0d0; border: 1px solid #bbb;")
        self.setMouseTracking(True)
        self._bg_pixmap = None       # 左侧背景
        self._bg_w = 0               # 背景渲染宽度（0=自然尺寸）
        self._bg_h = 0               # 背景渲染高度
        self._right_bg_pixmap = None # 右侧背景
        self._controls = []          # 左侧控件
        self._right_controls = []    # 右侧控件
        self._sel_index = -1
        self._sel_zone = "left"      # 选中控件所在区域
        self._pixmap_cache = {}
        self._can_drag = False
        self._drag_start = QPoint()
        self._zoom = 1.0
        self._sp_ox = 0             # 右侧 X 偏移
        self._sp_oy = 0             # 右侧 Y 偏移
        self._zoom_anchor = None     # 缩放焦点（画布坐标，点击空白处设定）

    @property
    def zoom(self): return self._zoom

    def zoomIn(self):
        self._zoom = min(4.0, round(self._zoom + 0.25, 2))
        self._apply_zoom()

    def zoomOut(self):
        self._zoom = max(0.25, round(self._zoom - 0.25, 2))
        self._apply_zoom()

    def zoomReset(self):
        self._zoom = 1.0
        self._apply_zoom()

    def _apply_zoom(self, w=None, h=None):
        # 优先用当前页面尺寸，避免 zoomIn/Out 传空时 fallback 到 1024×768
        if hasattr(self, '_page_offset') and self._page_offset:
            w = w or self._page_offset[2]
            h = h or self._page_offset[3]
        w = w or 1024
        h = h or 768
        self.clear()
        old_z = getattr(self, '_last_z', 1.0)
        z = self._zoom
        self.setFixedSize(int(w * z), int(h * z))
        cx = cy = 0
        if hasattr(self, '_page_offset'):
            cx = int(self._page_offset[0] * z)
            cy = int(self._page_offset[1] * z)
            self.move(cx, cy)
        # 扩展 viewport 使滚动条生效
        if self.parent():
            self.parent().setFixedSize(cx + int(w * z) + 50, cy + int(h * z) + 50)
        self.update()
        # 缩放锚点：保持锚点在视口中的位置不变
        self._adjust_scroll_after_zoom(old_z, z)
        self._last_z = z

    def _adjust_scroll_after_zoom(self, old_z: float, new_z: float):
        """缩放后调整滚动条，使锚点位置在视口中保持不变。"""
        if not hasattr(self, '_zoom_anchor') or self._zoom_anchor is None:
            return
        # 找到 QScrollArea 父级
        scroll_area = None
        p = self.parent()
        if p and hasattr(p, 'parent') and p.parent():
            from PyQt5.QtWidgets import QScrollArea
            if isinstance(p.parent(), QScrollArea):
                scroll_area = p.parent()
        if scroll_area is None:
            return
        # 锚点原始画布坐标
        Px, Py = self._zoom_anchor
        # 滚动条调整量 = (canvas_x + page_x) * (new_z - old_z)
        dx = (Px + self._page_offset[0]) * (new_z - old_z)
        dy = (Py + self._page_offset[1]) * (new_z - old_z)
        hbar = scroll_area.horizontalScrollBar()
        vbar = scroll_area.verticalScrollBar()
        hbar.setValue(int(hbar.value() + dx))
        vbar.setValue(int(vbar.value() + dy))

    def loadBackground(self, path: str, w=1024, h=768, bgW=0, bgH=0):
        """加载左侧背景图。bgW/bgH 控制贴图渲染尺寸，0=使用像素自然尺寸。"""
        self._bg_pixmap = QPixmap(path) if path and os.path.exists(path) else None
        self._bg_w = bgW
        self._bg_h = bgH
        if w <= 1: w = self._bg_pixmap.width() if self._bg_pixmap else 1024
        if h <= 1: h = self._bg_pixmap.height() if self._bg_pixmap else 768
        self._apply_zoom(w, h)

    def loadRightBackground(self, path: str):
        """加载右侧背景图。"""
        if path and os.path.exists(path):
            self._right_bg_pixmap = QPixmap(path)
        else:
            self._right_bg_pixmap = None
        self.update()

    def setSidePanelOffset(self, ox: int, oy: int):
        """设置右侧控件坐标偏移。"""
        self._sp_ox = ox
        self._sp_oy = oy
        self.update()

    def setRightControls(self, controls: list):
        """设置右侧面板控件列表。"""
        self._right_controls = controls[:]
        for c in self._right_controls:
            src = c.get("src", "")
            if src and os.path.exists(src) and src not in self._pixmap_cache:
                self._pixmap_cache[src] = QPixmap(src)
        self.update()

    def setControls(self, controls: list):
        """设置左侧控件列表。"""
        self._controls = controls
        for c in controls:
            src = c.get("src", "")
            if src and os.path.exists(src) and src not in self._pixmap_cache:
                self._pixmap_cache[src] = QPixmap(src)
        self.update()

    def _get_pixmap(self, ctrl: dict):
        """获取控件的贴图（缓存优先）。"""
        src = ctrl.get("src", "")
        if src and os.path.exists(src):
            if src not in self._pixmap_cache:
                self._pixmap_cache[src] = QPixmap(src)
            return self._pixmap_cache[src]
        return None

    def _control_rect(self, i: int, zone: str = "left"):
        """返回控件缩放后的 QRect，右侧控件自动加面板偏移。"""
        clist = self._right_controls if zone == "right" else self._controls
        ox = self._sp_ox if zone == "right" else 0
        oy = self._sp_oy if zone == "right" else 0
        if i < 0 or i >= len(clist):
            return QRect()
        c = clist[i]
        pid = c.get("_parent_id", "")
        if pid:
            try:
                p = clist[int(pid)]
                ox += int(p.get("x", 0))
                oy += int(p.get("y", 0))
            except (ValueError, IndexError):
                pass
        return QRect(int((int(c.get("x", 0)) + ox) * self._zoom),
                     int((int(c.get("y", 0)) + oy) * self._zoom),
                     int(int(c.get("w", 80)) * self._zoom),
                     int(int(c.get("h", 40)) * self._zoom))

    def _active_controls(self):
        """返回当前选中区域的控件列表。"""
        return self._right_controls if self._sel_zone == "right" else self._controls

    def _control_at(self, pos: QPoint):
        """返回 (zone, index)，zone="left"/"right"，index=-1 表示无控件。"""
        # 右侧控件优先（z 序更高）
        for i in range(len(self._right_controls) - 1, -1, -1):
            if self._control_rect(i, "right").contains(pos):
                return ("right", i)
        for i in range(len(self._controls) - 1, -1, -1):
            if self._control_rect(i, "left").contains(pos):
                ctrl = self._controls[i]
                if ctrl.get("container"):
                    for j in range(len(self._controls) - 1, -1, -1):
                        if str(self._controls[j].get("_parent_id", "")) == str(i):
                            if self._control_rect(j, "left").contains(pos):
                                return ("left", j)
                return ("left", i)
        return ("left", -1)

    def _to_orig(self, p: QPoint) -> QPoint:
        """画布坐标 → 原始坐标（除以缩放）。"""
        return QPoint(int(p.x() / self._zoom), int(p.y() / self._zoom))

    def paintEvent(self, event):
        """渲染：左背景 → 右背景 → 左控件 → 右控件(偏移) → 选中框。"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("Arial", 10))
        z = self._zoom

        # 左侧背景（bgW/bgH 控制渲染尺寸，0 则取贴图自然尺寸）
        if self._bg_pixmap and not self._bg_pixmap.isNull():
            bw = self._bg_w or self._bg_pixmap.width()
            bh = self._bg_h or self._bg_pixmap.height()
            pw, ph = int(bw * z), int(bh * z)
            painter.drawPixmap(0, 0, self._bg_pixmap.scaled(pw, ph, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

        # 右侧背景（偏移渲染）
        if self._right_bg_pixmap and not self._right_bg_pixmap.isNull():
            rx, ry = int(self._sp_ox * z), int(self._sp_oy * z)
            pw, ph = int(self._right_bg_pixmap.width() * z), int(self._right_bg_pixmap.height() * z)
            painter.drawPixmap(rx, ry, self._right_bg_pixmap.scaled(pw, ph, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 区域分隔线
        if self._sp_ox > 0:
            sx = int(self._sp_ox * z)
            painter.setPen(QPen(QColor(80, 80, 100), 1, Qt.DashLine))
            painter.drawLine(sx, 0, sx, self.height())

        # 渲染控件（左侧和右侧）
        self._paint_controls(painter, self._controls, 0, 0, z)
        self._paint_controls(painter, self._right_controls, self._sp_ox, self._sp_oy, z)

        # 选中框
        if self._sel_index >= 0:
            clist = self._active_controls()
            if self._sel_index < len(clist):
                r = self._control_rect(self._sel_index, self._sel_zone)
                painter.setPen(QPen(QColor(0, 200, 255), 3))
                painter.drawRect(r)
                s = 6
                for pt in [r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight()]:
                    painter.fillRect(pt.x()-s, pt.y()-s, s*2, s*2, QColor(0, 200, 255))
                c = clist[self._sel_index]
                lbl = f"{c.get('type','?')}#{self._sel_index} ({self._sel_zone})"
                painter.drawText(r.x() + 4, r.y() - 4, lbl)

        painter.end()

    def _paint_controls(self, painter, controls, ox, oy, z):
        """渲染一组控件，ox/oy 为画布偏移。"""
        def _sort_key(idx_c):
            i, ctrl = idx_c
            if ctrl.get("type") == "Rectangle" and ctrl.get("container"):
                return (0, i)
            if ctrl.get("_parent_id"):
                return (1, i)
            return (2, i)

        for i, c in sorted(enumerate(controls), key=_sort_key):
            ctype = c.get("type", "ImageButton")
            rect = QRect(int((int(c.get("x",0)) + ox) * z),
                         int((int(c.get("y",0)) + oy) * z),
                         int(int(c.get("w", 80)) * z),
                         int(int(c.get("h", 40)) * z))
            pm = self._get_pixmap(c)
            if pm and not pm.isNull():
                hw = c.get("half_w_dir", "")
                hh = c.get("half_h_dir", "")
                pw, ph = int(pm.width() * z), int(pm.height() * z)
                pm_z = pm.scaled(pw, ph, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                eff_w, eff_h = pw // 2 if hw else pw, ph // 2 if hh else ph
                eff_rect = QRect(rect.x(), rect.y(), eff_w, eff_h)
                x_off = rect.x() - (pw // 2 if hw == "right" else 0)
                y_off = rect.y() - (ph // 2 if hh == "bottom" else 0)
                painter.save()
                painter.setClipRect(eff_rect)
                painter.drawPixmap(x_off, y_off, pm_z)
                painter.restore()
            elif ctype == "Text (Label)":
                bg = c.get("bgColor","") or "#1e1e1e"
                op = c.get("opacity",100)/100.0
                col = QColor(bg) if QColor.isValidColor(bg) else QColor("#1e1e1e")
                col.setAlphaF(op)
                painter.fillRect(rect, col)
                painter.setPen(QPen(QColor(c.get("color","#fff"))))
                painter.drawText(rect.x()+4, rect.y()+int(rect.height()*0.7), c.get("text","Label"))
            elif ctype == "GCodeViewer":
                painter.fillRect(rect, QColor(20,25,20))
                painter.setPen(QPen(QColor(60,100,60), 1))
                painter.drawRect(rect)
                painter.drawText(rect.x()+5, rect.y()+25, "GCodeViewer")
            elif ctype in ("Text (DRO)","DRO"):
                bg = c.get("bgColor","") or "#001400"
                op = c.get("opacity",100)/100.0
                col = QColor(bg) if QColor.isValidColor(bg) else QColor("#001400")
                col.setAlphaF(op)
                painter.fillRect(rect, col)
                painter.setPen(QPen(QColor(0,255,0), 1))
                painter.drawRect(rect)
                painter.drawText(rect.x()+4, rect.y()+14, c.get("bind","0.0000"))
            elif ctype in ("MachTextInput","TextField"):
                bg = c.get("bgColor","") or "#323232"
                op = c.get("opacity",100)/100.0
                col = QColor(bg) if QColor.isValidColor(bg) else QColor("#323232")
                col.setAlphaF(op)
                painter.fillRect(rect, col)
                painter.setPen(QPen(QColor(200,200,200), 1))
                painter.drawRect(rect)
                painter.drawText(rect.x()+5, rect.y()+22, Tr.t("control_defs.s21_9b6425", "Input") if ctype=="MachTextInput" else "MDI")
            elif ctype == "Rectangle" and c.get("canvas"):
                bg = c.get("bgColor","") or "#2d3040"
                op = c.get("opacity",100)/100.0
                col = QColor(bg) if QColor.isValidColor(bg) else QColor("#2d3040")
                col.setAlphaF(op)
                painter.fillRect(rect, col)
                painter.setPen(QPen(QColor("#666"), 1, Qt.DashLine))
                painter.drawRect(rect)
                painter.drawText(rect.x()+8, rect.y()+22, Tr.t("_sort_key.s10_4d7f93", "Canvas"))
            elif ctype == "Rectangle":
                bg = c.get("bgColor","") or "#282d32"
                op = c.get("opacity",100)/100.0
                col = QColor(bg) if QColor.isValidColor(bg) else QColor("#282d32")
                col.setAlphaF(op)
                painter.fillRect(rect, col)
                if c.get("border", True):
                    bc, bw = c.get("borderC","") or "#555", c.get("borderW",1)
                    bcol = QColor(bc) if QColor.isValidColor(bc) else QColor("#555")
                    painter.setPen(QPen(bcol, bw))
                    painter.drawRect(rect)
                label = Tr.t("controls.s39_22c799", "Container") if c.get("container") else Tr.t("_sort_key.s12_cd6f79", "Panel")
                painter.setPen(QPen(QColor(150,150,160), 1))
                painter.drawText(rect.x()+5, rect.y()+20, label)
            elif ctype == "GCodeGraphics":
                bg = c.get("bgColor","") or "#0a0a0f"
                op = c.get("opacity",100)/100.0
                col = QColor(bg) if QColor.isValidColor(bg) else QColor("#0a0a0f")
                col.setAlphaF(op)
                painter.fillRect(rect, col)
                painter.setPen(QPen(QColor(80,80,100), 1))
                painter.drawRect(rect)
                painter.drawText(rect.x()+5, rect.y()+25, Tr.t("_sort_key.s13_e2f4b1", "3D Toolpath"))
            elif ctype == "Image":
                if pm and not pm.isNull():
                    painter.drawPixmap(rect.x(), rect.y(), pm.scaled(rect.width(), rect.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    painter.fillRect(rect, QColor(40,40,60))
                    painter.setPen(QPen(QColor(150,150,180), 1))
                    painter.drawRect(rect)
                    painter.drawText(rect.x()+4, rect.y()+14, Tr.t("_sort_key.s14_8d2d98", "Static image"))
            else:
                bg = c.get("bgColor","") or "#3c3c3c"
                op = c.get("opacity",100)/100.0
                col = QColor(bg) if QColor.isValidColor(bg) else QColor("#3c3c3c")
                col.setAlphaF(op)
                painter.fillRect(rect, col)
                painter.setPen(QPen(QColor(150,150,150), 1))
                painter.drawRect(rect)
                painter.drawText(rect.x()+4, rect.y()+14, f"{ctype}#{i}")

    def mousePressEvent(self, event):
        pos = event.pos()
        self._resize_corner = -1
        corner = self._corner_hit(pos)
        if corner >= 0:
            self._resize_corner = corner
            self._resize_start = pos
            clist = self._active_controls()
            if self._sel_index >= 0 and self._sel_index < len(clist):
                self._resize_orig = dict(clist[self._sel_index])
        else:
            zone, idx = self._control_at(pos)
            if idx >= 0:
                self._sel_zone = zone
                self._sel_index = idx
                self.update()
                self.controlSelected.emit(idx)
                self._can_drag = True
                self._drag_start = pos
            else:
                self._sel_index = -1
                self.controlSelected.emit(-1)
                # 设定缩放锚点（画布空白处点击）
                self._zoom_anchor = (pos.x() / self._zoom, pos.y() / self._zoom)
                self.update()

    def mouseMoveEvent(self, event):
        # 光标提示
        if self._corner_hit(event.pos()) >= 0:
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        # 拖角缩放
        if hasattr(self, '_resize_corner') and self._resize_corner >= 0:
            delta = event.pos() - self._resize_start
            if delta.manhattanLength() > 2:
                dx = int(delta.x() / self._zoom)
                dy = int(delta.y() / self._zoom)
                clist = self._active_controls()
                if self._sel_index >= 0 and self._sel_index < len(clist):
                    c = clist[self._sel_index]
                    orig = self._resize_orig
                    cn = self._resize_corner
                    if cn in (1, 3): c["w"] = max(10, orig.get("w", 80) + dx)
                    else:
                        c["x"] = orig.get("x", 0) + dx
                        c["w"] = max(10, orig.get("w", 80) - dx)
                    if cn in (2, 3): c["h"] = max(10, orig.get("h", 40) + dy)
                    else:
                        c["y"] = orig.get("y", 0) + dy
                        c["h"] = max(10, orig.get("h", 40) - dy)
                self.update()
        # 拖拽移动
        elif self._can_drag and self._sel_index >= 0:
            delta = event.pos() - self._drag_start
            if delta.manhattanLength() > 3:
                dx = int(delta.x() / self._zoom)
                dy = int(delta.y() / self._zoom)
                clist = self._active_controls()
                if self._sel_index >= 0 and self._sel_index < len(clist):
                    c = clist[self._sel_index]
                    c["x"] = max(0, c.get("x", 0) + dx)
                c["y"] = max(0, c.get("y", 0) + dy)
                self._drag_start = event.pos()
                self.update()

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_resize_corner') and self._resize_corner >= 0:
            self._resize_corner = -1
            self.controlSelected.emit(self._sel_index)
        if self._can_drag and self._sel_index >= 0:
            self.controlSelected.emit(self._sel_index)
        self._can_drag = False

    def _corner_hit(self, pos: QPoint) -> int:
        """检测 pos 在选中控件哪个角。-1=不中。"""
        if self._sel_index < 0:
            return -1
        r = self._control_rect(self._sel_index, self._sel_zone)
        s = 6
        for i, pt in enumerate([r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight()]):
            if QRect(pt.x()-s, pt.y()-s, s*2, s*2).contains(pos):
                return i
        return -1

    def addControl(self, template: dict, zone: str = "left", select: bool = True):
        """往指定区域添加控件。"""
        if zone == "right":
            self._right_controls.append(template)
        else:
            self._controls.append(template)
        if select:
            self._sel_zone = zone
            clist = self._active_controls()
            self._sel_index = len(clist) - 1
            self.controlSelected.emit(self._sel_index)
        self.update()

    def _set_page_controls(self, controls: list, right_controls: list = None):
        """一次性设置左右控件列表。"""
        self._controls = controls[:]
        if right_controls is not None:
            self._right_controls = right_controls[:]
        self._sel_index = -1
        self.update()


def _setup_combo_search(combo: QComboBox):
    """为下拉框添加大小写无关的子串搜索。"""
    from PyQt5.QtWidgets import QCompleter
    completer = QCompleter(combo.model(), combo)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)
    combo.setCompleter(completer)


