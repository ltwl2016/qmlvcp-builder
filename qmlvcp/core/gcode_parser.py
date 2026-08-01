from PySide6.QtCore import QThread, Signal, QByteArray
import struct
import math
import os
import re
import ctypes

class ParseResult(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_float)),
        ("vertex_count", ctypes.c_int),
        ("min_x", ctypes.c_float), ("max_x", ctypes.c_float),
        ("min_y", ctypes.c_float), ("max_y", ctypes.c_float),
        ("min_z", ctypes.c_float), ("max_z", ctypes.c_float),
    ]

# 探测并加载 C++ 极限加速插件
ACTIVATE_FAST_PARSER = False
fast_lib = None
try:
    # 智能识别 Windows 和 树莓派 (Linux) 环境
    plugin_name = 'fast_gcode_parser.dll' if os.name == 'nt' else 'fast_gcode_parser.so'
    _plugin_path = os.path.join(os.path.dirname(__file__), plugin_name)
    if os.path.exists(_plugin_path):
        fast_lib = ctypes.CDLL(_plugin_path)
        fast_lib.parse_gcode.restype = ParseResult
        fast_lib.parse_gcode.argtypes = [
            ctypes.c_char_p, 
            ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float
        ]
        fast_lib.free_result.argtypes = [ParseResult]
        ACTIVATE_FAST_PARSER = True
except Exception as e:
    print(f"[Parser Worker] C++ 插件加载失败，稍后默认切回 Python 引擎: {e}")

class GCodeParserWorker(QThread):
    """
    后台 G 代码正则解析引擎（已去除 LinuxCNC 原生解析依赖，恢复纯净版）
    增加：K坐标支持、G18/G19 三维平面的全量圆弧数学模型支持。
    """
    parsingProgress = Signal(float)
    parsingFinished = Signal(QByteArray, int, float, float, float, float, float, float)

    def __init__(self, file_path, g0_color, g1_color, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.g0_color = g0_color
        self.g1_color = g1_color

    def run(self):
        print(f"[Parser Worker] 开始解析后台文件: {self.file_path}")
        if not os.path.exists(self.file_path):
            print("[Parser Worker] 错误: 文件不存在!")
            self.parsingFinished.emit(QByteArray(), 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            return

        use_fast = False
        if ACTIVATE_FAST_PARSER:
            use_fast = True
            print("[Parser Worker] 正在进行毫秒级文件特征预扫描...")
            try:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # 极限榨干性能：仅抽查文件头部的 50 行片段 (耗时无限趋近于 0 毫秒)
                    for _ in range(50):
                        line = f.readline()
                        if not line:
                            break
                        if '#' in line or '[' in line:
                            use_fast = False
                            print("[Parser Worker] 文件头部探测到复杂的宏变量或计算式！自动安全切回 Python 兼容解析引擎")
                            break
            except Exception as e:
                print(f"[Parser Worker] 预扫描异常: {e}")

        if use_fast:
            print("[Parser Worker] ✨ 纯净 CAM 轨迹确认: 进入 C++ 物理极速核心解析模式 ✨")
            try:
                res = fast_lib.parse_gcode(
                    self.file_path.encode('utf-8'),
                    self.g0_color[0], self.g0_color[1], self.g0_color[2], self.g0_color[3],
                    self.g1_color[0], self.g1_color[1], self.g1_color[2], self.g1_color[3]
                )
                if res.vertex_count > 0:
                    byte_size = res.vertex_count * 7 * 4 
                    # ctypes直接映射底层内存到 Qt ，期间绝对【零拷贝】！！
                    q_bytes = QByteArray(ctypes.string_at(res.data, byte_size))
                else:
                    q_bytes = QByteArray()
                
                print(f"[Parser Worker] C++ 解析完毕，瞬发生成 3D 轨迹顶点数: {res.vertex_count}")
                self.parsingFinished.emit(q_bytes, res.vertex_count, 
                                          res.min_x, res.max_x, res.min_y, res.max_y, res.min_z, res.max_z)
                fast_lib.free_result(res)
                return  # C++任务完美完成，结束现线程
            except Exception as e:
                print(f"[Parser Worker] C++ 模块发生偶发错误，自动跌回低速 Python 引擎保底: {e}")

        # 以下为原版 Python 解析回退逻辑（防崩保底）
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        total_lines = len(lines)
        if total_lines == 0:
            print("[Parser Worker] 错误: 文件内容为空!")
            self.parsingFinished.emit(QByteArray(), 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            return

        vertex_data = bytearray()
        fmt = "<7f"
        
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        min_z, max_z = float('inf'), float('-inf')

        def add_line(x1, y1, z1, x2, y2, z2, color):
            nonlocal min_x, max_x, min_y, max_y, min_z, max_z
            min_x = min(min_x, x1, x2)
            max_x = max(max_x, x1, x2)
            min_y = min(min_y, y1, y2)
            max_y = max(max_y, y1, y2)
            min_z = min(min_z, z1, z2)
            max_z = max(max_z, z1, z2)
            vertex_data.extend(struct.pack(fmt, x1, z1, -y1, color[0], color[1], color[2], color[3]))
            vertex_data.extend(struct.pack(fmt, x2, z2, -y2, color[0], color[1], color[2], color[3]))

        cur_x, cur_y, cur_z = 0.0, 0.0, 0.0
        motion_mode = 0  # 0=G0, 1=G1, 2=G2, 3=G3
        plane = 17       # 17=XY, 18=ZX, 19=YZ
        scale = 1.0      # 1.0=G21(mm), 25.4=G20(inch)
        variables = {}   # 保存宏变量 #<var> 或 #1

        for i, line in enumerate(lines):
            if self.isInterruptionRequested():
                break

            line = re.sub(r'\(.*?\)', '', line)
            line = line.split(';')[0].upper().replace(' ', '').replace('\t', '').strip()
            
            # 1. 预处理变量定义: #<VAR> = VALUE 或 #1 = VALUE
            var_def_match = re.search(r'#(?:<([A-Z0-9_]+)>|(\d+))=([+\-]?\d*\.?\d+)', line)
            if var_def_match:
                var_name = var_def_match.group(1) or var_def_match.group(2)
                variables[var_name] = float(var_def_match.group(3))
                continue

            # 2. 替换变量调用
            def replace_var(m):
                v_name = m.group(1) or m.group(2)
                return str(variables.get(v_name, 0.0))
            line = re.sub(r'#(?:<([A-Z0-9_]+)>|(\d+))', replace_var, line)

            # 3. 预处理方括号数学表达式: [EXPR]
            def eval_expr(m):
                try:
                    safe_expr = re.sub(r'[^0-9\.\+\-\*/\(\)]', '', m.group(1))
                    return str(eval(safe_expr))
                except:
                    return "0"
            while '[' in line and ']' in line:
                line, count = re.subn(r'\[([^\[\]]+)\]', eval_expr, line)
                if count == 0: break

            if not line:
                continue

            words = re.findall(r'[A-Z][+\-]?\d*\.?\d+', line)
            
            new_x, new_y, new_z = cur_x, cur_y, cur_z
            i_val, j_val, k_val = 0.0, 0.0, 0.0
            r_val = 0.0
            
            has_move = False
            has_i = False
            has_j = False
            has_k = False
            has_r = False

            for w in words:
                cmd = w[0]
                try:
                    val = float(w[1:])
                except ValueError:
                    continue

                if cmd == 'G':
                    if val in (0, 1, 2, 3):
                        motion_mode = int(val)
                    elif val in (17, 18, 19):
                        plane = int(val)
                    elif val == 20:
                        scale = 25.4
                    elif val == 21:
                        scale = 1.0
                elif cmd == 'X':
                    new_x = val * scale
                    has_move = True
                elif cmd == 'Y':
                    new_y = val * scale
                    has_move = True
                elif cmd == 'Z':
                    new_z = val * scale
                    has_move = True
                elif cmd == 'I':
                    i_val = val * scale
                    has_i = True
                elif cmd == 'J':
                    j_val = val * scale
                    has_j = True
                elif cmd == 'K':
                    k_val = val * scale
                    has_k = True
                elif cmd == 'R':
                    r_val = val * scale
                    has_r = True

            if has_move or has_i or has_j or has_k or has_r:
                if motion_mode == 0 or motion_mode == 1:
                    color = self.g0_color if motion_mode == 0 else self.g1_color
                    add_line(cur_x, cur_y, cur_z, new_x, new_y, new_z, color)
                    
                elif motion_mode == 2 or motion_mode == 3:
                    if not (has_i or has_j or has_k or has_r):
                        add_line(cur_x, cur_y, cur_z, new_x, new_y, new_z, self.g1_color)
                    else:
                        # 基于右手定则的平面循环映射
                        if plane == 17: # XY 平面
                            u, v = cur_x, cur_y
                            nu, nv = new_x, new_y
                            ou, ov = i_val, j_val
                        elif plane == 18: # ZX 平面
                            u, v = cur_z, cur_x
                            nu, nv = new_z, new_x
                            ou, ov = k_val, i_val
                        elif plane == 19: # YZ 平面
                            u, v = cur_y, cur_z
                            nu, nv = new_y, new_z
                            ou, ov = j_val, k_val
                            
                        cu, cv = u, v
                        radius = 0
                        
                        if has_i or has_j or has_k:
                            cu = u + ou
                            cv = v + ov
                            radius = math.hypot(u - cu, v - cv)
                        elif has_r:
                            du = nu - u
                            dv = nv - v
                            d = math.hypot(du, dv)
                            if d > 0 and abs(r_val) > d / 2.0:
                                h = math.sqrt(r_val**2 - (d/2.0)**2)
                                if r_val < 0: h = -h
                                mu, mv = (u + nu) / 2.0, (v + nv) / 2.0
                                n_u, n_v = -dv / d, du / d
                                if motion_mode == 2: # CW
                                    cu, cv = mu + h * n_u, mv + h * n_v
                                else: # CCW
                                    cu, cv = mu - h * n_u, mv - h * n_v
                                radius = abs(r_val)
                            else:
                                radius = 0

                        if radius > 0.001:
                            start_angle = math.atan2(v - cv, u - cu)
                            end_angle = math.atan2(nv - cv, nu - cu)
                            
                            if abs(nu - u) < 0.0001 and abs(nv - v) < 0.0001:
                                end_angle = start_angle + (-2 * math.pi if motion_mode == 2 else 2 * math.pi)
                            else:
                                if motion_mode == 2: 
                                    if end_angle >= start_angle: end_angle -= 2 * math.pi
                                else: 
                                    if end_angle <= start_angle: end_angle += 2 * math.pi
                                    
                            arc_length = abs(end_angle - start_angle) * radius
                            steps = max(8, int(arc_length / 0.5))
                            
                            px, py, pz = cur_x, cur_y, cur_z
                            for step in range(1, steps + 1):
                                t = step / steps
                                angle = start_angle + (end_angle - start_angle) * t
                                tu = cu + radius * math.cos(angle)
                                tv = cv + radius * math.sin(angle)
                                
                                if plane == 17:
                                    nx, ny = tu, tv
                                    nz = cur_z + (new_z - cur_z) * t
                                elif plane == 18:
                                    nz, nx = tu, tv
                                    ny = cur_y + (new_y - cur_y) * t
                                elif plane == 19:
                                    ny, nz = tu, tv
                                    nx = cur_x + (new_x - cur_x) * t
                                    
                                add_line(px, py, pz, nx, ny, nz, self.g1_color)
                                px, py, pz = nx, ny, nz
                        else:
                            add_line(cur_x, cur_y, cur_z, new_x, new_y, new_z, self.g1_color)
                            
                cur_x, cur_y, cur_z = new_x, new_y, new_z

            if i % 2000 == 0:
                self.parsingProgress.emit(i / total_lines)

        self.parsingProgress.emit(1.0)
        point_count = len(vertex_data) // 28 
        print(f"[Parser Worker] 解析完毕，生成顶点数: {point_count}")
        if point_count == 0:
            min_x = max_x = min_y = max_y = min_z = max_z = 0.0
        self.parsingFinished.emit(QByteArray(vertex_data), point_count, min_x, max_x, min_y, max_y, min_z, max_z)
