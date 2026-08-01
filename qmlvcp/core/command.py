"""
qmlVCP Command Core
提供对 linuxcnc.command() 的面向对象封装。
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Slot, Signal

try:
    import linuxcnc
    HAS_LINUXCNC = True
except ImportError:
    HAS_LINUXCNC = False


class Command(QObject):
    # 下发给上层 UI 的弹窗请求信号
    requestRunFromLineDialog = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        
        if HAS_LINUXCNC:
            self.cmd = linuxcnc.command()
        else:
            self.cmd = None

    @Slot(str)
    def mdi(self, gcode: str) -> None:
        """执行单句 MDI G代码指令"""
        print(f"[qmlVCP Command] 发送 MDI 指令: {gcode}")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MDI)
            self.cmd.wait_complete()
            self.cmd.mdi(gcode)

    @Slot()
    def setModeManual(self) -> None:
        print("[qmlVCP Command] 切换到 手动模式")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MANUAL)
            self.cmd.wait_complete()

    @Slot()
    def setModeAuto(self) -> None:
        print("[qmlVCP Command] 切换到 自动模式")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_AUTO)
            self.cmd.wait_complete()

    @Slot()
    def setModeMDI(self) -> None:
        print("[qmlVCP Command] 切换到 MDI 模式")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MDI)
            self.cmd.wait_complete()


    @Slot(int)
    def setEstop(self, state: int) -> None:
        print(f"[qmlVCP Command] 设置急停: {state}")
        if HAS_LINUXCNC:
            self.cmd.state(linuxcnc.STATE_ESTOP if state else linuxcnc.STATE_ESTOP_RESET)

    @Slot(int)
    def setMachinePower(self, state: int) -> None:
        print(f"[qmlVCP Command] 设置上电: {state}")
        if HAS_LINUXCNC:
            self.cmd.state(linuxcnc.STATE_ON if state else linuxcnc.STATE_OFF)

    @Slot()
    def homeAll(self) -> None:
        print("[qmlVCP Command] 全轴回零")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MANUAL)
            self.cmd.wait_complete()
            self.cmd.teleop_enable(False)
            self.cmd.wait_complete()
            self.cmd.home(-1)

    @Slot()
    def unhomeAll(self) -> None:
        print("[qmlVCP Command] 全轴取消回零")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MANUAL)
            self.cmd.wait_complete()
            self.cmd.teleop_enable(False)
            self.cmd.wait_complete()
            self.cmd.unhome(-1)

    @Slot(int)
    def homeAxis(self, axis_index: int) -> None:
        print(f"[qmlVCP Command] 轴 {axis_index} 回零")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MANUAL)
            self.cmd.wait_complete()
            self.cmd.teleop_enable(False)
            self.cmd.wait_complete()
            self.cmd.home(axis_index)

    @Slot(int)
    def unhomeAxis(self, axis_index: int) -> None:
        print(f"[qmlVCP Command] 轴 {axis_index} 取消回零")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MANUAL)
            self.cmd.wait_complete()
            self.cmd.teleop_enable(False)
            self.cmd.wait_complete()
            self.cmd.unhome(axis_index)

    def jog(self, axis_index: int, speed: float, distance: float = 0.0, is_teleop: bool | None = None) -> None:
        """点动控制。
        支持连续(distance=0.0)或单步(distance>0)。
        """
        if HAS_LINUXCNC:
            if is_teleop is None:
                try:
                    s = linuxcnc.stat()
                    s.poll()
                    is_teleop = (getattr(s, 'motion_mode', 1) == linuxcnc.TRAJ_MODE_TELEOP)
                except Exception:
                    is_teleop = False
            real_joint_flag = not is_teleop
            if real_joint_flag:
                self.cmd.mode(linuxcnc.MODE_MANUAL)
                self.cmd.wait_complete()
            
            if distance > 0:
                self.cmd.jog(linuxcnc.JOG_INCREMENT, real_joint_flag, axis_index, speed, distance)
            else:
                self.cmd.jog(linuxcnc.JOG_CONTINUOUS, real_joint_flag, axis_index, speed)

    def stopJog(self, axis_index: int, is_teleop: bool | None = None) -> None:
        """停止点动。
        可传入 is_teleop 参数直接指定模式，避免重复创建 stat 对象。
        """
        if HAS_LINUXCNC:
            if is_teleop is None:
                try:
                    s = linuxcnc.stat()
                    s.poll()
                    is_teleop = (getattr(s, 'motion_mode', 1) == linuxcnc.TRAJ_MODE_TELEOP)
                except Exception:
                    is_teleop = False
            real_joint_flag = not is_teleop
            self.cmd.jog(linuxcnc.JOG_STOP, real_joint_flag, axis_index)


    @Slot(int)
    def setTeleopEnable(self, enable: int) -> None:
        print(f"[qmlVCP Command] 设置 Teleop: {'开启' if enable else '关闭'}")
        if HAS_LINUXCNC:
            self.cmd.teleop_enable(enable)

    @Slot()
    def zero_axis(self, axis_letter: str) -> None:
        """将指定轴的当前工作坐标清零 (G10 L20)"""
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MDI)
            self.cmd.wait_complete()
            self.cmd.mdi(f"G10 L20 P0 {axis_letter.upper()}0")
            self.cmd.wait_complete()
            self.cmd.mode(linuxcnc.MODE_MANUAL)
            self.cmd.wait_complete()

    def gotoSafeZ(self) -> None:
        """返回安全高度 (G53 Z0)"""
        print("[qmlVCP Command] 移动至安全高度 (Safe Z)")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_MDI)
            self.cmd.wait_complete()
            self.cmd.mdi("G53 G0 Z0")


    @Slot(int)
    def setFlood(self, state: int) -> None:
        print(f"[qmlVCP Command] 设置冷却液 (Flood): {state}")
        if HAS_LINUXCNC:
            self.cmd.flood(state)

    @Slot(int)
    def setMist(self, state: int) -> None:
        print(f"[qmlVCP Command] 设置喷雾 (Mist): {state}")
        if HAS_LINUXCNC:
            self.cmd.mist(state)

    @Slot(int, float)
    def setSpindle(self, direction: int, speed: float) -> None:
        print(f"[qmlVCP Command] 设置主轴: 方向 {direction}, 转速 {speed}")
        if HAS_LINUXCNC:
            if direction == 0:
                self.cmd.spindle(linuxcnc.SPINDLE_OFF)
            elif direction == 1:
                self.cmd.spindle(linuxcnc.SPINDLE_FORWARD, speed)
            elif direction == -1:
                self.cmd.spindle(linuxcnc.SPINDLE_REVERSE, speed)

    @Slot(int)
    def programRun(self, line_number: int, is_idle: bool | None = None) -> None:
        print(f"[qmlVCP Command] 尝试程序启动 (从行号 {line_number})")
        # 出于安全考虑，非空闲状态严禁启动
        if is_idle is False:
            print("[qmlVCP Command] 警告：解释器非空闲，拒绝启动程序！")
            return
            
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_AUTO)
            self.cmd.wait_complete()
            self.cmd.auto(linuxcnc.AUTO_RUN, line_number)

    @Slot()
    def programPause(self) -> None:
        print("[qmlVCP Command] 程序暂停")
        if HAS_LINUXCNC:
            self.cmd.auto(linuxcnc.AUTO_PAUSE)

    @Slot()
    def programResume(self) -> None:
        print("[qmlVCP Command] 程序续距")
        if HAS_LINUXCNC:
            self.cmd.auto(linuxcnc.AUTO_RESUME)

    @Slot()
    def programStep(self) -> None:
        print("[qmlVCP Command] 程序单步")
        if HAS_LINUXCNC:
            self.cmd.auto(linuxcnc.AUTO_STEP)

    @Slot()
    def programStop(self) -> None:
        print("[qmlVCP Command] 程序停止")
        if HAS_LINUXCNC:
            self.cmd.abort()

    @Slot(str)
    def programOpen(self, filepath: str, is_idle: bool | None = None) -> None:
        print(f"[qmlVCP Command] 尝试载入程序: {filepath}")
        if is_idle is False:
            print("[qmlVCP Command] 警告：解释器非空闲，拒绝加载程序！")
            return
            
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_AUTO)
            self.cmd.wait_complete()
            self.cmd.program_open(filepath)

    @Slot()
    def programRewind(self) -> None:
        print("[qmlVCP Command] 程序返回开始 (Rewind)")
        if HAS_LINUXCNC:
            self.cmd.mode(linuxcnc.MODE_AUTO)
            self.cmd.wait_complete()
            self.cmd.task_plan_init()

    @Slot(bool)
    def setBlockDelete(self, state: bool) -> None:
        print(f"[qmlVCP Command] 设置跳段 (Block Delete): {state}")
        if HAS_LINUXCNC:
            self.cmd.set_block_delete(state)


    # ==========================================
    # 核心安全业务逻辑：从指定行运行
    # ==========================================
    @Slot(int)
    def requestRunFromLine(self, line: int, is_idle: bool | None = None) -> None:
        """前端发出运行请求，qmlVCP 中枢进行严格的安全业务校验"""
        print(f"[qmlVCP Command] 收到从第 {line} 行启动的请求验证...")
        if line < 0:
            print("[qmlVCP Command] 拒绝：无效的行号")
            return
        if is_idle is False:
            print("[qmlVCP Command] 拒绝：机器处于非空闲状态")
            return
            
        # 校验通过，中枢下发弹窗指令给外部系统
        self.requestRunFromLineDialog.emit(line)

    @Slot(int)
    def confirmRunFromLine(self, line: int, is_idle: bool | None = None) -> None:
        """最终的安全放行，执行强制启动"""
        if line >= 0 and is_idle is not False:
            print(f"[qmlVCP Command] 用户已确认安全，执行强起指令：行号 {line}")
            self.programRun(line, is_idle=is_idle)

    @Slot(int, 'QVariantMap')
    def confirmRunFromLineWithOptions(self, line: int, options: dict, is_idle: bool | None = None) -> None:
        """接收带有高级参数的强起指令"""
        if line < 0 or is_idle is False:
            return
            
        print(f"[qmlVCP Command] 收到带参强制启动指令，配置: {options}")
        if HAS_LINUXCNC:
            # 1. 切换到 MDI
            self.cmd.mode(linuxcnc.MODE_MDI)
            self.cmd.wait_complete()
            
            # 2. 下发预设指令 (串行下发)
            if options.get("wcs"):
                self.cmd.mdi(options["wcs"])
                self.cmd.wait_complete()
                
            if options.get("spindleEnabled"):
                speed = options.get("spindleSpeed", 0)
                s_dir = options.get("spindleDir", "M3")
                self.cmd.mdi(f"S{speed} {s_dir}")
                self.cmd.wait_complete()
                
            if options.get("coolantOn"):
                self.cmd.mdi("M8")
            else:
                self.cmd.mdi("M9")
            self.cmd.wait_complete()
            
            if options.get("g43Enabled"):
                t = options.get("toolNumber", 0)
                if t > 0:
                    self.cmd.mdi(f"G43 H{t}")
                else:
                    self.cmd.mdi("G43")
            else:
                self.cmd.mdi("G49")
            self.cmd.wait_complete()
            
            if options.get("rtcpEnabled"):
                q = options.get("rtcpQ", 1)
                self.cmd.mdi(f"M428 Q{q}")
                self.cmd.wait_complete()
            elif options.get("rtcpCancel"):
                self.cmd.mdi("M429")
                self.cmd.wait_complete()
            
            # 3. 切换回 AUTO 并执行程序
            self.cmd.mode(linuxcnc.MODE_AUTO)
            self.cmd.wait_complete()
            self.cmd.auto(linuxcnc.AUTO_RUN, line)
            
            # 4. 如果开启了单步，立刻暂停
            if options.get("singleBlock"):
                self.cmd.auto(linuxcnc.AUTO_PAUSE)
        else:
            print("[qmlVCP Command] 脱机模式: 模拟高级五轴发车流程", options)

