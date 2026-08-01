from PySide6.QtQuick3D import QQuick3DGeometry
from PySide6.QtCore import QByteArray, Property, Signal, Slot
from PySide6.QtGui import QVector3D
import struct

class AxesGeometry(QQuick3DGeometry):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._axis_length = 50.0
        self.updateData()

    def get_axis_length(self): return self._axis_length
    def set_axis_length(self, v):
        if self._axis_length != v:
            self._axis_length = v
            self.updateData()
    axisLength = Property(float, get_axis_length, set_axis_length)

    def updateData(self):
        self.clear()
        
        l = self._axis_length
        vertex_data = bytearray()
        # Format: x, y, z (3 floats), r, g, b, a (4 floats) -> 7 floats total per vertex (28 bytes)
        fmt = "<7f"

        def add_line(p1, p2, color):
            vertex_data.extend(struct.pack(fmt, p1[0], p1[1], p1[2], *color))
            vertex_data.extend(struct.pack(fmt, p2[0], p2[1], p2[2], *color))

        r_c = (1.0, 0.0, 0.0, 1.0)
        g_c = (0.0, 1.0, 0.0, 1.0)
        b_c = (0.0, 0.0, 1.0, 1.0)

        # --- 第一部分：画原始的 3 根主坐标轴 ---
        add_line((0.0, 0.0, 0.0), (l, 0.0, 0.0), r_c)      # 红色 X
        add_line((0.0, 0.0, 0.0), (0.0, 0.0, -l), g_c)     # 绿色 Y
        add_line((0.0, 0.0, 0.0), (0.0, l, 0.0), b_c)      # 蓝色 Z
        
        # --- 第二部分：纯线段勾勒的 XYZ 字母 (原汁原味的工业风) ---
        s = l * 0.1  # 字母线条的大小
        
        # 1. 勾勒 X 字母 (红) 平放于工作台 (3D X 和 -Z 面)
        cx, cy, cz = l + s * 1.5, 0.0, 0.0
        add_line((cx - s, cy, cz - s), (cx + s, cy, cz + s), r_c)
        add_line((cx + s, cy, cz - s), (cx - s, cy, cz + s), r_c)

        # 2. 勾勒 Y 字母 (绿) 同样平放于工作台
        cx, cy, cz = 0.0, 0.0, -l - s * 1.5
        add_line((cx - s, cy, cz - s), (cx, cy, cz), g_c)
        add_line((cx + s, cy, cz - s), (cx, cy, cz), g_c)
        add_line((cx, cy, cz), (cx, cy, cz + s), g_c)

        # 3. 勾勒 Z 字母 (蓝) 垂直立起，方便侧面观察
        cx, cy, cz = 0.0, l + s * 1.5, 0.0
        add_line((cx - s, cy + s, cz), (cx + s, cy + s, cz), b_c)
        add_line((cx + s, cy + s, cz), (cx - s, cy - s, cz), b_c)
        add_line((cx - s, cy - s, cz), (cx + s, cy - s, cz), b_c)        
        
        self.setVertexData(QByteArray(vertex_data))
        self.setStride(28)
        # 稍微放大包围盒防止末端的字母被引擎裁剪
        self.setBounds(QVector3D(-s*2, -s*2, -l - s*3), QVector3D(l + s*3, l + s*3, s*2))
        self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Lines)
        
        self.addAttribute(QQuick3DGeometry.Attribute.PositionSemantic, 0, QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.ColorSemantic, 12, QQuick3DGeometry.Attribute.F32Type)


class BoundsGeometry(QQuick3DGeometry):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._min_x = 0.0
        self._max_x = 500.0
        self._min_y = 0.0
        self._max_y = 500.0
        self._min_z = 0.0
        self._max_z = 100.0
        self.updateData()

    def get_min_x(self): return self._min_x
    def set_min_x(self, v): 
        if self._min_x != v:
            self._min_x = v
            self.updateData()
    minX = Property(float, get_min_x, set_min_x)

    def get_max_x(self): return self._max_x
    def set_max_x(self, v): 
        if self._max_x != v:
            self._max_x = v
            self.updateData()
    maxX = Property(float, get_max_x, set_max_x)

    def get_min_y(self): return self._min_y
    def set_min_y(self, v): 
        if self._min_y != v:
            self._min_y = v
            self.updateData()
    minY = Property(float, get_min_y, set_min_y)

    def get_max_y(self): return self._max_y
    def set_max_y(self, v): 
        if self._max_y != v:
            self._max_y = v
            self.updateData()
    maxY = Property(float, get_max_y, set_max_y)

    def get_min_z(self): return self._min_z
    def set_min_z(self, v): 
        if self._min_z != v:
            self._min_z = v
            self.updateData()
    minZ = Property(float, get_min_z, set_min_z)

    def get_max_z(self): return self._max_z
    def set_max_z(self, v): 
        if self._max_z != v:
            self._max_z = v
            self.updateData()
    maxZ = Property(float, get_max_z, set_max_z)

    def updateData(self):
        self.clear()
        
        # CNC coords mapping: X->X, Y->-Z, Z->Y
        x0, x1 = self._min_x, self._max_x
        z0, z1 = -self._min_y, -self._max_y
        y0, y1 = self._min_z, self._max_z
        
        fmt = "<3f"
        vertex_data = bytearray()
        
        def add_line(p1, p2):
            vertex_data.extend(struct.pack(fmt, *p1))
            vertex_data.extend(struct.pack(fmt, *p2))
            
        # Bottom 4 lines
        add_line((x0, y0, z0), (x1, y0, z0))
        add_line((x1, y0, z0), (x1, y0, z1))
        add_line((x1, y0, z1), (x0, y0, z1))
        add_line((x0, y0, z1), (x0, y0, z0))
        
        # Top 4 lines
        add_line((x0, y1, z0), (x1, y1, z0))
        add_line((x1, y1, z0), (x1, y1, z1))
        add_line((x1, y1, z1), (x0, y1, z1))
        add_line((x0, y1, z1), (x0, y1, z0))
        
        # 4 vertical lines
        add_line((x0, y0, z0), (x0, y1, z0))
        add_line((x1, y0, z0), (x1, y1, z0))
        add_line((x1, y0, z1), (x1, y1, z1))
        add_line((x0, y0, z1), (x0, y1, z1))
        
        self.setVertexData(QByteArray(vertex_data))
        self.setStride(12)
        self.setBounds(QVector3D(x0, y0, z1), QVector3D(x1, y1, z0))
        self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Lines)
        
        self.addAttribute(QQuick3DGeometry.Attribute.PositionSemantic, 0, QQuick3DGeometry.Attribute.F32Type)


class TrajectoryGeometry(QQuick3DGeometry):
    gcodeFileChanged = Signal()
    pathBoundsParsed = Signal(float, float, float, float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._gcode_file = ""
        self._g0_color = [0.05, 0.25, 0.33, 1.0] # 青色代表G0快速移动
        self._g1_color = [0.8, 0.8, 0.8, 1.0] # 灰白色代表G1/G2/G3切削
        self._worker = None

    def get_gcode_file(self): return self._gcode_file
    def set_gcode_file(self, v): 
        if self._gcode_file != v:
            print(f"[3D Engine] QML 触发加载刀路文件: {v}")
            self._gcode_file = v
            self.gcodeFileChanged.emit()
            self._start_parsing(v)
    gcodeFile = Property(str, get_gcode_file, set_gcode_file, notify=gcodeFileChanged)

    def _start_parsing(self, file_path):
        if not file_path:
            self.clear()
            self.update()
            return
            
        # 导入刚才写的独立后台解析器
        from qmlvcp.core.gcode_parser import GCodeParserWorker
        
        # 启动后台多线程，防止主界面卡死
        self._worker = GCodeParserWorker(file_path, self._g0_color, self._g1_color, self)
        self._worker.parsingFinished.connect(self._on_parsing_finished)
        self._worker.start()

    def _on_parsing_finished(self, vertex_data, count, minX, maxX, minY, maxY, minZ, maxZ):
        print(f"[3D Engine] 刀路解析完成，顶点数量: {count}")
        
        # --- 完全采用纯 3D 线段进行长宽尺寸标注 (极客工业风) ---
        if count > 0:
            raw_bytes = bytearray(vertex_data) if not isinstance(vertex_data, bytearray) else vertex_data
            try:
                fmt = "<7f"
                def add_line_cnc(c1, c2, color):
                    # 映射到引擎的 3D 坐标: CNC X->3D X, CNC Y->3D -Z, CNC Z->3D Y
                    raw_bytes.extend(struct.pack(fmt, c1[0], c1[2], -c1[1], *color))
                    raw_bytes.extend(struct.pack(fmt, c2[0], c2[2], -c2[1], *color))

                dim_color = (0.7, 0.0, 0.0, 1.0) # 浅灰红色标注
                max_span = max((maxX - minX), (maxY - minY))
                sc = max(1.0, min(max_span * 0.03, 80.0)) # 字体高度，按工件长宽比例自适应缩放
                offset = sc * 1.5 # 尺寸包围盒往外偏移的距离
                
                # 画底边界线 (标注机床 X 长度) 
                add_line_cnc((minX, minY - offset, minZ), (maxX, minY - offset, minZ), dim_color)
                # 两侧垂直刻度线 (跨越上下，使底边界线精确处于它们正中间)
                add_line_cnc((minX, minY - offset + sc*0.8, minZ), (minX, minY - offset - sc*0.8, minZ), dim_color)
                add_line_cnc((maxX, minY - offset + sc*0.8, minZ), (maxX, minY - offset - sc*0.8, minZ), dim_color)
                
                # 画左侧界线 (标注机床 Y 宽度) 
                add_line_cnc((minX - offset, minY, minZ), (minX - offset, maxY, minZ), dim_color)
                # 两侧水平刻度线 (跨越左右，使其精确处于正中间)
                add_line_cnc((minX - offset + sc*0.8, minY, minZ), (minX - offset - sc*0.8, minY, minZ), dim_color)
                add_line_cnc((minX - offset + sc*0.8, maxY, minZ), (minX - offset - sc*0.8, maxY, minZ), dim_color)

                # 将所有的数字用经典的 7 段断码来表示
                segs = {
                    '0':(0,1,2,3,4,5), '1':(1,2), '2':(0,1,6,4,3), '3':(0,1,6,2,3), '4':(5,6,1,2),
                    '5':(0,5,6,2,3), '6':(0,5,6,4,3,2), '7':(0,1,2), '8':(0,1,2,3,4,5,6), '9':(0,1,2,3,5,6),
                    '-':(6,)
                }
                
                def draw_text_cnc(val_str, sx, sy, sz, sc, color, vertical=False):
                    curr_pos = sy if vertical else sx
                    w, h = sc * 0.6, sc * 0.5
                    
                    def get_pt(dx, dy):
                        if vertical:
                            # 逆时针旋转 90 度：X 偏移顺着 Y 轴走，Y 偏移逆着 X 轴走
                            # 这样文字从下往上排布，底部朝向工件
                            return (sx - dy, curr_pos + dx, sz)
                        else:
                            return (curr_pos + dx, sy + dy, sz)
                            
                    for char in val_str:
                        if char == '.':
                            # 画小数点的星号/十字
                            add_line_cnc(get_pt(w*0.5, -h*1.8), get_pt(w*0.5, -h*2.0), color)
                            add_line_cnc(get_pt(w*0.4, -h*1.9), get_pt(w*0.6, -h*1.9), color)
                            curr_pos += sc * 0.6
                            continue
                        
                        pts = [
                            get_pt(0, 0),     get_pt(w, 0),
                            get_pt(0, -h),    get_pt(w, -h),
                            get_pt(0, -2*h),  get_pt(w, -2*h)
                        ]
                        if char == 'X':
                            add_line_cnc(pts[0], pts[5], color)
                            add_line_cnc(pts[1], pts[4], color)
                        elif char == 'Y':
                            mid = get_pt(w/2, -h)
                            add_line_cnc(pts[0], mid, color)
                            add_line_cnc(pts[1], mid, color)
                            add_line_cnc(mid, get_pt(w/2, -2*h), color)
                        elif char == ':':
                            add_line_cnc(get_pt(w/2, -h*0.5+sc*0.05), get_pt(w/2, -h*0.5-sc*0.05), color)
                            add_line_cnc(get_pt(w/2, -h*1.5+sc*0.05), get_pt(w/2, -h*1.5-sc*0.05), color)
                        elif char in segs:
                            lines_map = [(0,1), (1,3), (3,5), (4,5), (2,4), (0,2), (2,3)]
                            for idx in segs[char]:
                                add_line_cnc(pts[lines_map[idx][0]], pts[lines_map[idx][1]], color)
                        curr_pos += sc * 0.9

                val_x = f"X:{maxX - minX:.2f}"
                len_x = len(val_x)*sc*0.9 - sc*0.3
                draw_text_cnc(val_x, (minX+maxX)/2 - len_x/2, minY - offset - sc*0.5, minZ, sc, dim_color)
                
                val_y = f"Y:{maxY - minY:.2f}"
                len_y = len(val_y)*sc*0.9 - sc*0.3
                # 垂直居中，靠在刻度线左侧
                draw_text_cnc(val_y, minX - offset - sc*1.5, (minY+maxY)/2 - len_y/2, minZ, sc, dim_color, vertical=True)
                
            except Exception as e:
                print("Dimension error:", e)
                
            vertex_data = raw_bytes
            
        self.clear()
        if count > 0:
            self.setVertexData(vertex_data)
            self.setStride(28)
            # 设定超大边界防止视角移动时被引擎误剔除
            self.setBounds(QVector3D(-10000, -10000, -10000), QVector3D(10000, 10000, 10000))
            self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Lines)
            
            self.addAttribute(QQuick3DGeometry.Attribute.PositionSemantic, 0, QQuick3DGeometry.Attribute.F32Type)
            self.addAttribute(QQuick3DGeometry.Attribute.ColorSemantic, 12, QQuick3DGeometry.Attribute.F32Type)
            self.update()
            
        self.pathBoundsParsed.emit(minX, maxX, minY, maxY, minZ, maxZ)

class LiveTrajectoryGeometry(QQuick3DGeometry):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._vertex_data = bytearray()
        self._last_point = None
        self._color = [0.0, 1.0, 1.0, 1.0] # 青色轨迹
        self._fmt = "<7f"
        
        self.setStride(28)
        self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Lines)
        self.addAttribute(QQuick3DGeometry.Attribute.PositionSemantic, 0, QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.ColorSemantic, 12, QQuick3DGeometry.Attribute.F32Type)
        self.setBounds(QVector3D(-10000, -10000, -10000), QVector3D(10000, 10000, 10000))
        self.updateData()

    @Slot()
    def clearPath(self):
        self._vertex_data.clear()
        self._last_point = None
        self.updateData()

    @Slot(float, float, float, int)
    def appendPoint(self, x, y, z, motionType):
        # 映射到 3D 空间: X->X, Y->-Z, Z->Y
        px = x
        py = z
        pz = -y
        
        if self._last_point is None:
            self._last_point = (px, py, pz)
            return
            
        lx, ly, lz = self._last_point
        
        # 防抖，如果移动距离小于 0.1 毫米就不记录，防止停在一个点原地添加无数个点
        dist_sq = (px - lx)**2 + (py - ly)**2 + (pz - lz)**2
        if dist_sq < 0.01:
            return
            
        # 根据 LinuxCNC 的运动类型改变颜色
        # 0: None/Jog, 1: Traverse(G0), 2: Feed(G1), 3: Arc(G2/G3)
        if motionType == 1:
            self._color = [0.05, 0.25, 0.33, 1.0] # G0 青色
        elif motionType == 2 or motionType == 3:
            self._color = [0.5, 0.0, 0.2, 1.0] # G1/G2/G3 红色
        else:
            self._color = [1.0, 1.0, 0.0, 1.0] # 未知/Jog 用黄色区分

        r, g, b, a = self._color
        self._vertex_data.extend(struct.pack(self._fmt, lx, ly, lz, r, g, b, a))
        self._vertex_data.extend(struct.pack(self._fmt, px, py, pz, r, g, b, a))
        self._last_point = (px, py, pz)
        
        # 防止无限增长撑爆内存，限制 50,000 个线段顶点 (约 1.4 MB)
        MAX_BYTES = 50000 * 28
        if len(self._vertex_data) > MAX_BYTES:
            self._vertex_data = self._vertex_data[MAX_BYTES//2:]
            
        self.updateData()

    def updateData(self):
        self.clear()
        if len(self._vertex_data) > 0:
            self.setVertexData(QByteArray(self._vertex_data))
            self.setStride(28)
            self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Lines)
            self.addAttribute(QQuick3DGeometry.Attribute.PositionSemantic, 0, QQuick3DGeometry.Attribute.F32Type)
            self.addAttribute(QQuick3DGeometry.Attribute.ColorSemantic, 12, QQuick3DGeometry.Attribute.F32Type)
            # 因为是动态追踪，包围盒直接给个超级大的极限值，防止移动视角时被引擎自动剔除
            self.setBounds(QVector3D(-10000, -10000, -10000), QVector3D(10000, 10000, 10000))
        self.update()
