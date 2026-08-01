# Demo CNC — 示例输出项目 / Example Output Project

> *QmlVcp Builder 生成项目的完整示例 — 开箱可运行*  
> *A complete example of what QmlVcp Builder exports — ready to run*

---

## 这是什么？ / What is this?

这是一个通过 QmlVcp Builder **可视化编辑后导出**的完整 CNC 人机界面项目。你可以直接运行它，也可以作为你自己项目的模板。

This is a complete CNC HMI project **exported by QmlVcp Builder** after visual editing. You can run it directly, or use it as a template for your own project.

## 连接 LinuxCNC / Connecting to LinuxCNC

本 QmlVcp 项目本质上是一个**独立 GUI 程序**，要让它接管 LinuxCNC 的显示，只需在 LinuxCNC 配置文件的 `[DISPLAY]` 段中指定 `start.sh` 的路径即可——与 Axs、Touchy、Gmoccapy 的用法完全相同。

This QmlVcp project is a **standalone GUI**. To make LinuxCNC use it as the display, simply point `[DISPLAY]` to `start.sh` in your ini config — exactly the same way you'd use Axis, Touchy, or Gmoccapy.

### 配置方法 / Configuration

编辑你的 LinuxCNC 机器配置文件（通常位于 `~/linuxcnc/configs/<机器名>/<机器名>.ini`）：

Edit your LinuxCNC machine config file (usually at `~/linuxcnc/configs/<machine_name>/<machine_name>.ini`)：

```ini
[DISPLAY]
DISPLAY = /home/cnc/qmlvcp-projects/demo_cnc/start.sh
```

> **注意 / Note**：路径必须是**绝对路径**，指向本项目目录中的 `start.sh`。  
> The path must be an **absolute path** pointing to `start.sh` inside this project directory.

### start.sh 做了什么 / What start.sh does

```bash
#!/bin/bash
cd "$(dirname "$0")"           # 进入项目目录
source "../venv/bin/activate"  # 激活虚拟环境（可选）
python3 -u main.py "$@"        # 启动界面，-ini 参数由 LinuxCNC 自动传入
```

LinuxCNC 启动时会**自动**将 ini 文件路径作为 `-ini` 参数传给 `start.sh`，QmlVcp 框架会解析 ini 配置、初始化 HAL 连接、挂载 NML 通信，无需手动干预。

When LinuxCNC starts, it **automatically** passes the ini file path as a `-ini` argument to `start.sh`. The QmlVcp framework handles ini parsing, HAL initialization, and NML communication — no manual intervention needed.

### 快速开始 / Quick Start

```bash
# 1. 安装依赖
pip install PySide6>=6.5

# 2. 独立预览模式（无 LinuxCNC 连接也能看界面）
python main.py

# 3. 模拟连接（用假 ini 测试 HAL 行为）
python main.py -ini /path/to/test.ini

# 4. 真实 LinuxCNC 环境：按照上面的方法配置 [DISPLAY]，直接启动 LinuxCNC 即可
```

## 文件结构 / File Structure

```
demo_cnc/
├── main.py               # 入口 / Entry point
├── backend.py            # 业务逻辑 / Business logic (自定义你的 CNC 交互)
├── requirements.txt      # Python 依赖 / Dependencies
├── qml/
│   ├── Main.qml          # 主界面 / Main UI (QML 编写)
│   └── qmldir            # QML 模块声明 / Module declaration
├── assets/               # 素材 / Images, icons, textures
└── README.md             # 👈 这个文件 / This file
```

## 功能演示 / What's Demonstrated

| 功能 / Feature              | 文件 / File     | 说明 / Description                     |
|----------------------------|-----------------|---------------------------------------|
| DRO 坐标显示 / DRO Display  | `Main.qml`      | `backend.displayX/Y/Z/A` 属性绑定      |
| JOG 手动控制 / JOG Control  | `Main.qml`      | `backend.jogAxis()` Slot调用           |
| 程序启停 / Cycle Control    | `Main.qml`      | `backend.cycleStart/Stop()`           |
| 急停&上电 / E-stop & Power  | `Main.qml`      | `backend.emergencyStop/machineOn()`   |
| 主轴显示 / Spindle Info     | `Main.qml`      | `backend.spindleSpeed/Dir`            |
| 机床状态 / Machine State    | `Main.qml`      | `backend.machineState`                |
| 自定义属性 / Custom Counter | `backend.py`    | 演示如何添加自定义 @Property 和 @Slot   |

## 从 Builder 导出 / Export from Builder

1. 在 QmlVcp Builder 中拖放控件搭建界面
2. 设置属性（尺寸、颜色、Hal 引脚等）
3. 点击「导出项目」
4. 导出的结果就是类似本示例的项目结构

> 1. Drag & drop controls in QmlVcp Builder to design UI
> 2. Set properties (size, color, HAL pins, etc.)
> 3. Click "Export Project"
> 4. The exported result looks exactly like this example

## 自定义 / Customization

### 添加自定义属性 / Add Custom Property

在 `backend.py` 中：

```python
@Property(float, notify=mySignal)
def myCustomValue(self):
    return self._value
```

### 添加自定义槽 / Add Custom Slot

```python
@Slot(int)
def doSomething(self, param):
    # your logic
    pass
```

在 `Main.qml` 中直接绑定：

```qml
Text { text: backend.myCustomValue }
Button { onClicked: backend.doSomething(42) }
```

## 框架核心对象 / Core Framework Objects

在 `backend.py` 中可直接使用，无需手动初始化：

| 对象 / Object          | 用途 / Purpose                           |
|------------------------|-----------------------------------------|
| `self.cnc_status`      | 读取机床状态 / Read machine state         |
| `self.cnc_command`     | 发送 GCode / 控制指令 / Send commands     |
| `self.jog_controller`  | JOG 手动控制 / Manual axis jogging       |
| `self.override_mgr`    | 进给/主轴倍率 / Feed & spindle override  |
| `self.runtime_tracker` | 加工时间统计 / Runtime statistics        |

## 许可证 / License

GNU General Public License v3.0 — 详见项目根目录 LICENSE 文件。

此示例基于 GPL v3 开源，你可以自由使用、修改和分发，但衍生作品也须以 GPL v3 开源。
