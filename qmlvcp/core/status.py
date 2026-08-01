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
qmlVCP Status Core
提供对 linuxcnc.stat() 的面向对象封装，支持跨平台 (Windows 模拟与 Linux 实机)。
"""
from __future__ import annotations

import random
import datetime
import os
from PySide6.QtCore import QObject, QTimer, Property, Signal
try:
    import linuxcnc
    HAS_LINUXCNC = True
except ImportError:
    HAS_LINUXCNC = False


class Status(QObject):
    # 定义状态改变信号
    positionChanged = Signal()
    modeChanged = Signal()
    stateChanged = Signal()
    errorChanged = Signal()
    messageChanged = Signal()
    spindleChanged = Signal()
    feedChanged = Signal()
    toolChanged = Signal()
    coolantChanged = Signal()
    programStateChanged = Signal()
    programFileChanged = Signal()
    motionLineChanged = Signal()
    homedChanged = Signal()
    motionModeChanged = Signal()   # Teleop/Free/Coord 切换
    interpStateChanged = Signal()  # 解释器状态变化
    blockDeleteChanged = Signal()

    def __init__(self, config=None, parent: QObject | None = None, poll_interval_ms: int = 100) -> None:
        super().__init__(parent)
        self.config = config
        
        # 默认备胎路径：抛弃以前乱定位的写法，直接锚定在系统的全局基础路径 (也就是你的 INI 存放文件夹)
        if config and hasattr(config, 'base_dir'):
            default_log = os.path.join(config.base_dir, "linuxcnc_debug.log")
        else:
            default_log = os.path.abspath(os.path.join(os.getcwd(), "linuxcnc_debug.log"))
        custom_log = getattr(config, 'log_file', None)
        
        def _try_init_log(filepath):
            try:
                # [关键补丁] 专门针对 Linux 系统，把带 ~ 的原生 INI 路径翻译成真正的系统绝对家目录
                real_path = os.path.expanduser(filepath)
                # 只有翻译过后的真实路径才能执行后续检测和创建
                parent_dir = os.path.dirname(os.path.abspath(real_path))
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                with open(real_path, "w", encoding="utf-8") as f:
                    f.write(f"--- QMLVCP 诊断日志启动: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                return real_path # 返回翻译且成功的真实绝对路径
            except Exception as e:
                print(f"[Status] 警告: 无法在目标位置初始化日志文件 {filepath} -> {e}")
                return None

        self.log_file = None
        if custom_log:
            # 尝试通过一层沙盒试跑用户自定义路径
            self.log_file = _try_init_log(custom_log)
            if not self.log_file:
                print(f"[Status] 用户自定义日志路径校验失败，已自动退回系统默认的备胎记录器: {default_log}")
        
        # 如果从头到尾都没传自定义字典、或者刚才那一步跌落失败，统一靠这段兜底
        if not self.log_file:
            self.log_file = _try_init_log(default_log)

        if HAS_LINUXCNC:
            self.stat = linuxcnc.stat()
            self.err = linuxcnc.error_channel()
        else:
            self.stat = None
            self.err = None

        # 缓存状态
        self._actual_position = (0.0,) * 9
        self._g5x_offset = (0.0,) * 9
        self._g92_offset = (0.0,) * 9
        self._dtg = (0.0,) * 9
        self._homed = (False,) * 9
        self._is_all_homed = False
        
        self._task_mode = "未知"
        self._task_state = "关闭"
        self._error_text = ""
        self._has_error = False
        self._message_text = ""
        self._has_message = False
        
        # MPG (手轮) 状态
        self._mpg_active_axis = -1
        self._mpg_scale_text = "x10"
        
        self._feed = 0
        self._actual_feed = 0
        self._spindle_speed = 0.0
        self._spindle_base = 0
        self._spindle_override = 1.0
        self._spindle_dir = 0
        
        self._flood = False
        self._mist = False
        self._tool_in_spindle = 0
        self._tool_offset_z = 0.0
        self._tool_diameter = 0.0
        
        self._feed_override = 1.0
        self._programmed_feed = 0.0
        
        self._program_file = ""
        self._motion_line = 0
        self._read_line = 0
        self._exec_state = 0
        self._block_delete = False

        self._motion_mode = 0  # TRAJ_MODE_FREE=1 / COORD=2 / TELEOP=3
        self._motion_type = 0  # 1=Traverse(G0), 2=Feed(G1), 3=Arc(G2/G3)
        self._interp_state = 0 # INTERP_IDLE / READING / PAUSED / WAITING

        # Windows 模拟使用的内部计时器，使其能轻微浮动
        self._sim_counter = 0

        # 定时轮询
        self.timer = QTimer(self)
        self.timer.setInterval(poll_interval_ms)
        self.timer.timeout.connect(self.poll)
        self.timer.start()

    def record_cnc_log(self, level, msg):
        """追加写入本地日志文件，用于溯源查错"""
        try:
            with open(self.log_file, "a+", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                f.write(f"[{timestamp}] {level}: {msg}\n")
        except Exception:
            pass

    def poll(self) -> None:
        """主轮询函数，每周期调用"""
        if HAS_LINUXCNC:
            self._poll_linuxcnc()
        else:
            self._poll_mock()

    def _poll_linuxcnc(self) -> None:
        try:
            self.stat.poll()
        except Exception:
            return

        # 更新坐标 - 未回零时 actual_position 无法反映真实位置，降级到 joint_actual_position
        pos = getattr(self.stat, "actual_position", self._actual_position)
        if not self._is_all_homed and hasattr(self.stat, "joint_actual_position"):
            jap = getattr(self.stat, "joint_actual_position", None)
            if jap and len(jap) > 0:
                pos = tuple(jap[:len(jap)]) + pos[len(jap):]
        g5x = getattr(self.stat, "g5x_offset", self._g5x_offset)
        g92 = getattr(self.stat, "g92_offset", self._g92_offset)
        dtg = getattr(self.stat, "dtg", self._dtg)
        
        if pos != self._actual_position or g5x != self._g5x_offset or g92 != self._g92_offset or dtg != self._dtg:
            self._actual_position = pos
            self._g5x_offset = g5x
            self._g92_offset = g92
            self._dtg = dtg
            self.positionChanged.emit()

        # 更新回零状态 (兼容 LinuxCNC 2.7 和 2.8+)
        new_homed = [False] * 9
        is_machine_on = (getattr(self.stat, "task_state", 0) == linuxcnc.STATE_ON)
        
        all_homed = True
        has_joints = False
        
        if hasattr(self.stat, 'joint'):
            joints = self.stat.joint
            num_active_joints = getattr(self.stat, 'joints', len(joints))
            if num_active_joints > 0:
                has_joints = True
            for i in range(min(num_active_joints, len(joints))):
                j = joints[i]
                raw_homed = bool(j.get('homed', False)) if isinstance(j, dict) else bool(getattr(j, 'homed', False))
                h = raw_homed and is_machine_on
                if i < 9:
                    new_homed[i] = h
                if not h:
                    all_homed = False
        elif hasattr(self.stat, 'homed'):
            homed_list = self.stat.homed
            if len(homed_list) > 0:
                has_joints = True
            for i in range(len(homed_list)):
                h = bool(homed_list[i]) and is_machine_on
                if i < 9:
                    new_homed[i] = h
                if not h:
                    all_homed = False
                    
        if not has_joints:
            all_homed = False
            
        self._is_all_homed = all_homed
        
        new_homed_tuple = tuple(new_homed)
        if new_homed_tuple != self._homed:
            self._homed = new_homed_tuple
            self.homedChanged.emit()

        # 更新任务模式 (手动/自动/MDI)
        mode_map = {
            linuxcnc.MODE_MANUAL: "手动",
            linuxcnc.MODE_AUTO: "自动",
            linuxcnc.MODE_MDI: "MDI"
        }
        new_mode = mode_map.get(self.stat.task_mode, "未知")
        if new_mode != self._task_mode:
            self._task_mode = new_mode
            self.modeChanged.emit()

        # 更新运动控制器模式 (Free/Coord/Teleop)
        new_motion_mode = getattr(self.stat, 'motion_mode', 0)
        
        # 兼容所有版本的 LinuxCNC: 通过活跃的 G 代码组判定当前运动类型
        new_motion_type = 0
        # 1=FREE(Jog), 2=COORD(Auto/MDI), 3=TELEOP
        if new_motion_mode == 2:
            gcodes = getattr(self.stat, 'gcodes', tuple())
            if len(gcodes) > 1:
                g_motion = gcodes[1]
                if g_motion == 0:
                    new_motion_type = 1 # G0
                elif g_motion in (10, 20, 30):
                    new_motion_type = 2 # G1/G2/G3
        
        if new_motion_mode != self._motion_mode or new_motion_type != self._motion_type:
            self._motion_mode = new_motion_mode
            self._motion_type = new_motion_type
            self.motionModeChanged.emit()

        # 更新解释器状态 (Idle/Reading/Paused/Waiting)
        new_interp = getattr(self.stat, 'interp_state', 0)
        if new_interp != self._interp_state:
            self._interp_state = new_interp
            self.interpStateChanged.emit()

        # 更新状态
        state_map = {
            linuxcnc.STATE_ESTOP: "急停",
            linuxcnc.STATE_ESTOP_RESET: "未准备",
            linuxcnc.STATE_OFF: "关闭",
            linuxcnc.STATE_ON: "就绪"
        }
        new_state = state_map.get(self.stat.task_state, "未知")
        if new_state != self._task_state:
            self._task_state = new_state
            self.stateChanged.emit()

        # 冷却与主轴刀具状态
        flood = getattr(self.stat, "flood", False)
        mist = getattr(self.stat, "mist", False)
        if flood != self._flood or mist != self._mist:
            self._flood = flood
            self._mist = mist
            self.coolantChanged.emit()
            
        tool = getattr(self.stat, "tool_in_spindle", 0)
        tool_offset = getattr(self.stat, "tool_offset", (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        z_offset = tool_offset[2] if isinstance(tool_offset, (list, tuple)) and len(tool_offset) > 2 else getattr(tool_offset, 'z', 0.0)
        
        diameter = 0.0
        tool_table = getattr(self.stat, "tool_table", [])
        if tool_table and tool < len(tool_table):
            tool_data = tool_table[tool]
            if isinstance(tool_data, tuple) and len(tool_data) > 10:
                diameter = float(tool_data[10])
            elif hasattr(tool_data, 'diameter'):
                diameter = float(tool_data.diameter)
                
        if tool != self._tool_in_spindle or z_offset != self._tool_offset_z or diameter != self._tool_diameter:
            self._tool_in_spindle = tool
            self._tool_offset_z = z_offset
            self._tool_diameter = diameter
            self.toolChanged.emit()
            
        speed = getattr(self.stat, "spindle_speed", 0.0)
        if speed != self._spindle_speed:
            self._spindle_speed = speed
            self.spindleChanged.emit()

        # 更新报警和消息（循环抽取队列，防止高频报错互相覆盖导致肉眼不可见）
        error_msg = self.err.poll()
        while error_msg:
            kind, text = error_msg
            if kind == 1: # NML_ERROR (致命报警)
                self.record_cnc_log("[⚠️灾难报警]", text)
                self._has_error = True
                if not self._error_text:
                    self._error_text = text
                elif text not in self._error_text:
                    self._error_text += " | " + text
                self.errorChanged.emit()
            else: # 定制常规消息
                self.record_cnc_log("[ℹ️常规消息]", text)
                self._has_message = True
                if not self._message_text:
                    self._message_text = text
                elif text not in self._message_text:
                    self._message_text += " | " + text
                self.messageChanged.emit()
            error_msg = self.err.poll()

        # 更新进给/主轴
        try:
            base_feed = float(self.stat.settings[1]) if hasattr(self.stat, 'settings') and len(self.stat.settings) > 1 else 0.0
            feed_rate = getattr(self.stat, 'feedrate', 1.0)
            feed = int(base_feed * feed_rate)
            
            # --- 业务逻辑下沉：钳位机床物理最大速度 ---
            # 从底层提取系统级最大速度 (注意: stat.max_velocity 的单位通常是 unit/sec，需要 * 60.0)
            max_vel_sec = getattr(self.stat, 'max_velocity', 0.0)
            if max_vel_sec > 0.0:
                max_feed_min = max_vel_sec * 60.0
                if base_feed > max_feed_min:
                    base_feed = max_feed_min
                if feed > max_feed_min:
                    feed = int(max_feed_min)
            # ------------------------------------------
            
            # 获取机床底层真实的运动线速度 (单位/秒 -> 单位/分)
            current_vel = getattr(self.stat, 'current_vel', 0.0)
            actual_feed = int(current_vel * 60.0)
            
            if feed != self._feed or feed_rate != self._feed_override or base_feed != self._programmed_feed or actual_feed != self._actual_feed:
                self._feed = feed
                self._actual_feed = actual_feed
                self._feed_override = feed_rate
                self._programmed_feed = base_feed
                self.feedChanged.emit()

            spindle = 0
            base_speed = 0
            spindle_rate = 1.0
            s_dir = 0
            if hasattr(self.stat, 'spindle') and len(self.stat.spindle) > 0:
                sp_data = self.stat.spindle[0]
                base_speed = int(sp_data.get('speed', 0)) if isinstance(sp_data, dict) else int(getattr(sp_data, 'speed', 0))
                spindle_rate = float(sp_data.get('override', 1.0)) if isinstance(sp_data, dict) else float(getattr(sp_data, 'override', 1.0))
                spindle = int(base_speed * spindle_rate)
                s_dir = int(sp_data.get('direction', 0)) if isinstance(sp_data, dict) else int(getattr(sp_data, 'direction', 0))
            
            if spindle != self._spindle_speed or spindle_rate != self._spindle_override or base_speed != self._spindle_base or s_dir != self._spindle_dir:
                self._spindle_speed = spindle
                self._spindle_override = spindle_rate
                self._spindle_base = base_speed
                self._spindle_dir = s_dir
                self.spindleChanged.emit()
                
            # 更新 G代码追踪及其他运行状态
            p_file = getattr(self.stat, "file", "")
            if p_file != self._program_file:
                self._program_file = p_file
                self.programFileChanged.emit()

            m_line = getattr(self.stat, "motion_line", 0)
            if m_line != self._motion_line:
                self._motion_line = m_line
                self.motionLineChanged.emit()
                
            r_line = getattr(self.stat, "read_line", 0)
            e_state = getattr(self.stat, "exec_state", 0)
            if r_line != self._read_line or e_state != self._exec_state:
                self._read_line = r_line
                self._exec_state = e_state
                self.programStateChanged.emit()
                
            # 更新跳段状态 (Block Delete)
            bd = getattr(self.stat, "block_delete", False)
            if bd != getattr(self, "_block_delete", False):
                self._block_delete = bd
                self.blockDeleteChanged.emit()
                
        except:
            pass

    def _poll_mock(self) -> None:
        """用于 Windows 下的模拟数据"""
        # 初始化默认数据
        if self._task_mode == "未知":
            self._task_mode = "手动"
            self._task_state = "就绪"
            self._actual_position = [12.500, -8.742, 5.000, 0, 90.0, 45.0, 0, 0, 0]
            self._g5x_offset = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            self._g92_offset = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            self._dtg = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            self._homed = (True, True, True, True, False, False, False, False, False)
            self._is_all_homed = True
            self._tool_offset_z = 12.34
            self._tool_diameter = 6.0
            self._feed_override = 1.0
            self._programmed_feed = 1250.0
            self._feed = 1250
            self._actual_feed = 1250
            self._spindle_speed = 8500
            self._motion_mode = 1  # 模拟 TRAJ_MODE_FREE
            self._interp_state = 1 # 模拟 INTERP_IDLE
            self.positionChanged.emit()
            self.modeChanged.emit()
            self.stateChanged.emit()
            self.feedChanged.emit()
            self.spindleChanged.emit()
            self.homedChanged.emit()
            self.motionModeChanged.emit()
            self.interpStateChanged.emit()

        if not self._has_error and self._task_mode == "自动":
            # 制造微动模拟加工
            new_pos = list(self._actual_position)
            for i in range(3):
                new_pos[i] += random.uniform(-0.02, 0.02)
            self._actual_position = tuple(new_pos)
            self.positionChanged.emit()

    # --- 属性暴露给外部 ---
    @Property("QVariantList", notify=positionChanged)
    def actualPosition(self):
        return list(self._actual_position)

    @Property("QVariantList", notify=positionChanged)
    def g5xOffset(self):
        return list(self._g5x_offset)

    @Property("QVariantList", notify=positionChanged)
    def g92Offset(self):
        return list(self._g92_offset)

    @Property("QVariantList", notify=positionChanged)
    def distanceToGo(self):
        return list(self._dtg)

    @Property(str, notify=modeChanged)
    def taskMode(self) -> str:
        """当前任务模式: '手动', '自动', 'MDI', '未知'"""
        return self._task_mode

    @Property(int, notify=motionModeChanged)
    def motionMode(self) -> int:
        """运动控制器模式: TRAJ_MODE_FREE=1, TRAJ_MODE_COORD=2, TRAJ_MODE_TELEOP=3"""
        return self._motion_mode

    @Property(bool, notify=motionModeChanged)
    def isTeleop(self) -> bool:
        """是否处于 Teleop（笛卡尔坐标点动）模式"""
        if HAS_LINUXCNC:
            return self._motion_mode == linuxcnc.TRAJ_MODE_TELEOP
        return False  # mock 模式下模拟 Free 模式

    @Property(int, notify=interpStateChanged)
    def interpState(self) -> int:
        """解释器状态: INTERP_IDLE=1, INTERP_READING=2, INTERP_PAUSED=3, INTERP_WAITING=4"""
        return self._interp_state

    @Property(bool, notify=interpStateChanged)
    def interpIdle(self) -> bool:
        """解释器是否空闲（发送 MDI 前必须检查此项）"""
        if HAS_LINUXCNC:
            return self._interp_state == linuxcnc.INTERP_IDLE
        return True  # mock 模式下始终可发送

    @Property(str, notify=stateChanged)
    def taskState(self):
        return self._task_state

    @Property(bool, notify=errorChanged)
    def hasError(self):
        return self._has_error
        
    @Property(str, notify=errorChanged)
    def errorText(self):
        return self._error_text

    @Property(bool, notify=messageChanged)
    def hasMessage(self):
        return self._has_message
        
    @Property(str, notify=messageChanged)
    def messageText(self):
        return self._message_text

    @Property(int, notify=feedChanged)
    def feed(self):
        return self._feed

    @Property(int, notify=feedChanged)
    def actualFeed(self):
        return self._actual_feed

    @Property(float, notify=feedChanged)
    def feedOverride(self):
        return self._feed_override

    @Property(float, notify=feedChanged)
    def programmedFeed(self):
        return self._programmed_feed

    @Property(int, notify=spindleChanged)
    def spindleSpeed(self):
        return self._spindle_speed

    @Property(float, notify=spindleChanged)
    def spindleOverride(self):
        return getattr(self, '_spindle_override', 1.0)
        
    @Property(int, notify=spindleChanged)
    def programmedSpindle(self):
        return getattr(self, '_spindle_base', 0)
        
    @Property(int, notify=spindleChanged)
    def spindleDir(self):
        return getattr(self, '_spindle_dir', 0)

    @Property(bool, notify=coolantChanged)
    def flood(self) -> bool:
        return self._flood
        
    @Property(bool, notify=coolantChanged)
    def mist(self) -> bool:
        return self._mist
        
    @Property(int, notify=toolChanged)
    def toolInSpindle(self) -> int:
        return self._tool_in_spindle

    @Property(float, notify=toolChanged)
    def toolOffsetZ(self) -> float:
        return self._tool_offset_z

    @Property(float, notify=toolChanged)
    def toolDiameter(self) -> float:
        return self._tool_diameter

    @Property(str, notify=programStateChanged)
    def programFile(self) -> str:
        return self._program_file
        
    @Property(int, notify=programStateChanged)
    def motionLine(self) -> int:
        return self._motion_line
        
    @Property(int, notify=programStateChanged)
    def readLine(self) -> int:
        return self._read_line
        
    @Property(int, notify=programStateChanged)
    def execState(self) -> int:
        return self._exec_state

    @Property("QVariantList", notify=homedChanged)
    def homed(self):
        return list(self._homed)

    @Property(bool, notify=homedChanged)
    def isAllHomed(self):
        return self._is_all_homed

    @Property(bool, notify=blockDeleteChanged)
    def blockDelete(self):
        return self._block_delete

    @Property(int, notify=stateChanged)
    def mpgActiveAxis(self):
        return self._mpg_active_axis

    @Property(str, notify=stateChanged)
    def mpgScaleText(self):
        return self._mpg_scale_text

    # ---------------- 极速物理绝对坐标下沉暴露 ----------------
    @Property(float, notify=positionChanged)
    def absoluteX(self):
        try: return self._actual_position[0] - self._g5x_offset[0]
        except: return 0.0
    @Property(float, notify=positionChanged)
    def absoluteY(self):
        try: return self._actual_position[1] - self._g5x_offset[1]
        except: return 0.0
    @Property(float, notify=positionChanged)
    def absoluteZ(self):
        try: return self._actual_position[2] - self._g5x_offset[2]
        except: return 0.0
    @Property(float, notify=positionChanged)
    def absoluteA(self):
        try: return self._actual_position[3] - self._g5x_offset[3]
        except: return 0.0
    @Property(float, notify=positionChanged)
    def absoluteB(self):
        try: return self._actual_position[4] - self._g5x_offset[4]
        except: return 0.0
    @Property(float, notify=positionChanged)
    def absoluteC(self):
        try: return self._actual_position[5] - self._g5x_offset[5]
        except: return 0.0

    # ---------------- 极速物理机床坐标下沉暴露 ----------------
    @Property(float, notify=positionChanged)
    def machineX(self): return self._actual_position[0] if len(self._actual_position)>0 else 0.0
    @Property(float, notify=positionChanged)
    def machineY(self): return self._actual_position[1] if len(self._actual_position)>1 else 0.0
    @Property(float, notify=positionChanged)
    def machineZ(self): return self._actual_position[2] if len(self._actual_position)>2 else 0.0
    @Property(float, notify=positionChanged)
    def machineA(self): return self._actual_position[3] if len(self._actual_position)>3 else 0.0
    @Property(float, notify=positionChanged)
    def machineB(self): return self._actual_position[4] if len(self._actual_position)>4 else 0.0
    @Property(float, notify=positionChanged)
    def machineC(self): return self._actual_position[5] if len(self._actual_position)>5 else 0.0

    @Property(bool, notify=homedChanged)
    def homedX(self): return self._homed[0] if len(self._homed)>0 else False
    @Property(bool, notify=homedChanged)
    def homedY(self): return self._homed[1] if len(self._homed)>1 else False
    @Property(bool, notify=homedChanged)
    def homedZ(self): return self._homed[2] if len(self._homed)>2 else False
    @Property(bool, notify=homedChanged)
    def homedA(self): return self._homed[3] if len(self._homed)>3 else False
    @Property(bool, notify=homedChanged)
    def homedB(self): return self._homed[4] if len(self._homed)>4 else False
    @Property(bool, notify=homedChanged)
    def homedC(self): return self._homed[5] if len(self._homed)>5 else False
