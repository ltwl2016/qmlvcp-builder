# Demo CNC — 示例输出项目 / Example Output Project

> *QmlVcp Builder 生成项目的完整示例 — 开箱可运行*  
> *A complete example of what QmlVcp Builder exports — ready to run*

---

## 这是什么？ / What is this?

这是一个通过 QmlVcp Builder **可视化编辑后导出**的完整 CNC 人机界面项目。你可以直接运行它，也可以作为你自己项目的模板。

This is a complete CNC HMI project **exported by QmlVcp Builder** after visual editing. You can run it directly, or use it as a template for your own project.

## 快速开始 / Quick Start

```bash
# 1. 安装依赖
pip install PySide6>=6.5

# 2. 独立预览模式（无 LinuxCNC 连接也能看界面）
python main.py

# 3. 连接真实 LinuxCNC
python main.py -ini /path/to/linuxcnc.ini
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
