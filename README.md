# QmlVcp Builder — CNC 界面可视化拼装工具

> 可在 Windows 下开发，导出项目运行于 LinuxCNC / Develop on Windows, deploy on LinuxCNC

[中文](#中文) | [English](#english)

---

## 中文

### 简介

QmlVcp Builder 是一款**可视化**的 CNC 操作界面拼装工具，面向 LinuxCNC 数控系统。无需手写 QML 代码，通过拖拽控件、编辑属性即可快速搭建工业级触摸屏操作面板。

**核心特点：**

- **零代码拼装** — 拖拽放置按钮、指示灯、DRO、刀路显示等控件
- **实时预览** — 所见即所得，编辑区即时显示控件位置和样式
- **动作/绑定系统** — 内置丰富的机床指令（回零、主轴、冷却液等）和状态绑定
- **多页面架构** — 支持主页 / 侧面板 / 顶栏 / 底栏分区布局
- **一键导出** — 生成完整可运行的 QML 项目，拷到 LinuxCNC 上即可使用
- **离线安装** — 支持在无网络的 LinuxCNC 机器上离线安装 PySide6

### 界面概览

| 标签页 | 功能 |
|--------|------|
| **环境设置** | 创建 Python 虚拟环境、安装 PySide6（在线/离线） |
| **界面拼装** | 控件列表 → 拖放至画布 → 属性编辑 → 实时预览 |
| **项目导出** | 设置导出路径、一键生成可运行项目 |

### 支持的控件

| 控件 | 说明 |
|------|------|
| `ImageButton` | 贴图按钮（支持按下/松开双帧、可选透明） |
| `SpriteButton` | 精灵图多帧按钮 |
| `LED` | 状态指示灯（颜色随状态变化） |
| `FlashLED` | 闪烁指示灯 |
| `Text_DRO` | 数字读数器（坐标/速度/转速显示） |
| `Text_Label` | 静态文本标签 |
| `TextField` | 文本输入框 |
| `MachTextInput` | 工业风文本输入 |
| `GCodeGraphics` | 3D 刀路可视化 |
| `GCodeViewer` | G 代码列表浏览器 |
| `EmergencyStop` | 急停按钮 |
| `JOGButton` | 点动按钮（带方向和速度控制） |
| `Image` | 静态贴图（背景/Logo） |
| `Rectangle` | 矩形色块 |
| `Timer` | 定时器控件 |
| `FileDialog` | 文件浏览对话框 |
| `RunFromHereDialog` | 断点续跑弹窗 |

### 使用方式

#### 1. 环境准备

| 角色 | 操作系统 | Python | 依赖 |
|------|----------|--------|------|
| **Builder（开发机）** | Windows / Linux | 3.10+ | PyQt5（LinuxCNC 2.9.8+ 自带，无需额外安装） |
| **导出的项目（机床）** | LinuxCNC (Debian/Ubuntu) | 3.10+ | PySide6 ≥ 6.5（需在 venv 中安装） |

> Builder 本身用 PyQt5 开发（LinuxCNC 2.9.8+ 原生自带），导出的项目运行框架基于 PySide6。

- **Windows 开发机**：用于设计界面，直接 `python main.py` 启动 Builder
- **LinuxCNC 机床**：用于运行生成的界面项目，需先安装 venv + PySide6（见下方步骤 6）

#### 2. 启动 Builder

```bash
cd qmlvcp-builder
python main.py
```

#### 3. 环境设置（首次使用）

1. 切换到「**环境设置**」标签页
2. 点击「**创建虚拟环境**」，等待完成
3. 点击「**安装 PySide6**」
   - 有网络：自动在线安装
   - 无网络：提前下载 whl 文件放入 `offline_wheels/{arch}/` 目录

#### 4. 拼装界面

1. 切换到「**界面拼装**」标签页
2. 左侧控件列表中选择控件类型
3. 点击「**+ 添加**」按钮，控件出现在画布上
4. 在画布上**拖拽**调整位置，**拖拽边角**调整大小
5. 右侧属性面板编辑控件属性：
   - **基础属性**（x, y, 宽, 高, 层级）
   - **外观属性**（颜色、贴图路径、文字、字体大小）
   - **动作绑定**（按钮点击执行什么 CNC 操作）
   - **状态绑定**（指示灯/文字关联哪个机床状态）
6. 多页面切换：通过右下角页面切换器管理多个主页面

#### 5. 导出项目

1. 切换到「**项目导出**」标签页
2. 设置导出目录（默认 `~/my-cnc`）
3. 点击「**导出项目**」
4. 将导出的目录复制到 LinuxCNC 机器上

#### 6. 在 LinuxCNC 上部署运行

##### 6.1 安装依赖

导出的项目依赖 **PySide6 ≥ 6.5**，需要在 LinuxCNC 机床上的**虚拟环境**中安装。

```bash
# 1. 进入导出项目目录
cd my-cnc

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 安装 PySide6（在线）
pip install PySide6>=6.5

# 5. 验证安装
python -c "from PySide6.QtCore import *; print('OK')"
```

##### 6.2 离线安装（无网络时）

适用于无互联网连接的 LinuxCNC 机床：

```bash
# 1. 在同架构的有网机器上下载 PySide6 离线包
pip download --only-binary=:all: PySide6>=6.5 -d offline_wheels/x86_64/

# 2. 将 offline_wheels/ 复制到 LinuxCNC 机床的项目目录中

# 3. 在机床上的 venv 中离线安装
source venv/bin/activate
pip install offline_wheels/x86_64/*.whl
```

支持的架构：`x86_64`、`aarch64`

##### 6.3 配置 LinuxCNC 启动

编辑你的 LinuxCNC 机床配置文件（`.ini`），在 `[DISPLAY]` 段中指定项目的 `start.sh`：

```ini
[DISPLAY]
DISPLAY = /path/to/my-cnc/start.sh
```

`start.sh` 会自动激活 venv 并启动界面，LinuxCNC 启动时会将 ini 路径作为 `-ini` 参数传入，框架自动完成 HAL 连接和 NML 通信初始化。

##### 6.4 独立预览（不连接 LinuxCNC）

```bash
cd my-cnc
source venv/bin/activate
python main.py
```

此模式仅用于预览界面外观，不连接 HAL/NML。

### 目录结构

```
qmlvcp-builder/
├── main.py                  # Builder 入口
├── builder/                 # Builder 核心代码
│   ├── main_window.py       # 主窗口（三标签页）
│   ├── preview_canvas.py    # 预览画布（拖拽/缩放控件）
│   ├── properties_mixin.py  # 属性面板逻辑
│   ├── field_registry.py    # 属性字段工厂
│   ├── project_exporter.py  # 项目导出器
│   ├── project_importer.py  # 项目导入器
│   ├── env_setup.py         # 虚拟环境 + PySide6 安装
│   ├── controls.py          # 控件/动作/绑定定义
│   ├── templates/           # QML 控件模板
│   │   └── *.qml            # 17 个控件模板
│   ├── mainwindow.ui        # Qt Designer 布局文件
│   └── mainwindow.qss       # 全局样式表
├── qmlvcp/                  # 运行时库（随项目导出）
│   ├── core/                # 核心模块
│   │   ├── status.py        # 机床状态读取
│   │   ├── command.py       # 指令下发
│   │   ├── jog_controller.py# JOG 控制
│   │   ├── hal_manager.py   # HAL 引脚管理
│   │   ├── gcode_graphics.py# 刀路渲染引擎
│   │   ├── gcode_parser.py       # G 代码解析器
│   │   └── fast_gcode_parser.so  # C++ 加速（x86_64 预编译，aarch64 需自行 g++ 编译）
│   └── qml/QmlVcp/              # QML 控件库
└── offline_wheels/               # 离线安装包存放目录
    ├── x86_64/
    └── aarch64/
```

### 开发文档

#### 项目架构

Builder 基于 **PyQt5**（LinuxCNC 2.9.8+ 原生自带），生成的运行时项目基于 **PySide6**。

三标签页架构：
```
MainWindow (QMainWindow)
├── Tab 1: 环境设置 (EnvManager)
│   ├── 创建/检测 venv
│   ├── 安装 PySide6（在线 + 离线回退）
│   └── 状态日志
├── Tab 2: 界面拼装 (PropertiesMixin)
│   ├── 控件列表 (左侧)
│   ├── 预览画布 (中间, PreviewCanvas)
│   └── 属性面板 (右侧, 动态表单)
└── Tab 3: 项目导出
    ├── 导出路径设置
    ├── 窗口尺寸配置
    └── QML 模板渲染导出
```

#### 数据模型

```python
_pages = [{
    "name": "mainwindow",
    "controls": [{
        "type": "ImageButton",
        "x": 100, "y": 200,
        "w": 120, "h": 80,
        "image": "assets/btn_start.png",
        "action": "cmd.progRun",
        "bind": "",
        "z": 0,
        "visible": True
    }, ...],
    "bg": "",
    "x": 0, "y": 0,
    "width": 1375, "height": 1000
}]
```

#### 添加新控件

1. 在 `builder/templates/` 下创建 `NewControl.qml` 模板
2. 在 `builder/templates/controls.py` 中注册控件属性定义
3. 控件模板使用 `{FIELD}` 占位符，导出时自动替换

#### 预定义动作与绑定

动作 (Actions) — 按钮点击时执行：
- `command.homeAll()` — 全部回零
- `command.setSpindle(1, 0)` — 主轴正转
- `command.programRun(0)` — 启动程序
- 更多见 `builder/controls.py` 中的 `ACTIONS` 字典

状态绑定 (Status Binds) — 控件属性跟随机床状态：
- `status.homedX` — X 轴是否已回零
- `status.spindleSpeed` — 当前主轴转速
- `status.absoluteX` — X 轴绝对坐标
- 更多见 `builder/controls.py` 中的 `STATUS_BINDS` 字典

#### 导出原理

1. 收集所有页面/面板的控件数据
2. 遍历控件，从 `builder/templates/` 读取对应 QML 模板
3. 将属性值填入模板占位符 (如 `{x}`, `{y}`, `{width}`, `{image}`, `{action}`, `{bind}` 等)
4. 合并生成 `Main.qml`
5. 将 `qmlvcp/` 运行时库、`main.py`、`backend.py` 复制到导出目录
6. 最终产物是一个完整独立、可直接 `python main.py` 运行的项目

---

## English

### Introduction

QmlVcp Builder is a **visual** CNC operator interface assembly tool for LinuxCNC. Build industrial-grade touchscreen control panels by drag-and-drop without writing QML code.

**Key Features:**

- **Zero-code Assembly** — Drag and drop controls (buttons, indicators, DROs, toolpath displays, etc.)
- **Real-time Preview** — WYSIWYG editing with instant position/style feedback
- **Action/Binding System** — Rich built-in CNC commands (homing, spindle, coolant, etc.) and status bindings
- **Multi-page Architecture** — Supports main page / side panel / topbar / bottombar layouts
- **One-click Export** — Generates a complete runnable QML project, ready for LinuxCNC
- **Offline Installation** — Install PySide6 on air-gapped LinuxCNC machines via offline wheels

### UI Overview

| Tab | Function |
|-----|----------|
| **Environment Setup** | Create venv, install PySide6 (online/offline) |
| **UI Assembly** | Control palette → drop on canvas → edit properties → preview |
| **Project Export** | Set export path, one-click generate runnable project |

### Supported Controls

| Control | Description |
|---------|-------------|
| `ImageButton` | Image button (dual-frame press/release, optional transparency) |
| `SpriteButton` | Multi-frame sprite button |
| `LED` | Status indicator (color changes with state) |
| `FlashLED` | Flashing indicator |
| `Text_DRO` | Digital readout (position/speed/RPM display) |
| `Text_Label` | Static text label |
| `TextField` | Text input field |
| `MachTextInput` | Industrial-style text input |
| `GCodeGraphics` | 3D toolpath visualization |
| `GCodeViewer` | G-code file browser |
| `EmergencyStop` | Emergency stop button |
| `JOGButton` | Jog button (with direction and speed control) |
| `Image` | Static image (background/logo) |
| `Rectangle` | Colored rectangle |
| `Timer` | Timer control |
| `FileDialog` | File browser dialog |
| `RunFromHereDialog` | Run-from-here dialog |

### Usage

#### 1. Prerequisites

| Role | OS | Python | Dependencies |
|------|----|--------|--------------|
| **Builder (dev machine)** | Windows / Linux | 3.10+ | PyQt5 (bundled with LinuxCNC 2.9.8+, no extra install) |
| **Exported project (CNC machine)** | LinuxCNC (Debian/Ubuntu) | 3.10+ | PySide6 ≥ 6.5 (install in venv, see step 6) |

> The Builder uses PyQt5 (native to LinuxCNC 2.9.8+). Exported projects run on PySide6.

- **Windows dev machine**: Design interfaces — run `python main.py` to launch Builder
- **LinuxCNC machine**: Run the exported project — requires venv + PySide6 (see step 6 below)

#### 2. Launch Builder

```bash
cd qmlvcp-builder
python main.py
```

#### 3. Environment Setup (first use)

1. Switch to **Environment Setup** tab
2. Click **Create venv**, wait for completion
3. Click **Install PySide6**
   - With network: automatic online install
   - Without network: pre-download whl files into `offline_wheels/{arch}/`

#### 4. Assemble UI

1. Switch to **UI Assembly** tab
2. Select a control type from the left palette
3. Click **+ Add** to place it on the canvas
4. **Drag** to reposition, **drag corners** to resize
5. Edit properties in the right panel:
   - **Basic** (x, y, width, height, z-order)
   - **Appearance** (color, image path, text, font size)
   - **Action binding** (what CNC operation does this button trigger)
   - **Status binding** (which machine state drives this indicator/label)
6. Multi-page switching: use the page switcher at bottom-right

#### 5. Export Project

1. Switch to **Project Export** tab
2. Set export directory (default `~/my-cnc`)
3. Click **Export Project**
4. Copy the exported directory to your LinuxCNC machine

#### 6. Deploy on LinuxCNC

##### 6.1 Install Dependencies

The exported project requires **PySide6 ≥ 6.5**, which must be installed in a **virtual environment** on the LinuxCNC machine.

```bash
# 1. Enter the exported project directory
cd my-cnc

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the venv
source venv/bin/activate

# 4. Install PySide6 (online)
pip install PySide6>=6.5

# 5. Verify installation
python -c "from PySide6.QtCore import *; print('OK')"
```

##### 6.2 Offline Installation (no internet)

For air-gapped LinuxCNC machines:

```bash
# 1. On a network-connected machine with the same architecture:
pip download --only-binary=:all: PySide6>=6.5 -d offline_wheels/x86_64/

# 2. Copy offline_wheels/ to the LinuxCNC machine's project directory

# 3. Install inside the venv on the LinuxCNC machine
source venv/bin/activate
pip install offline_wheels/x86_64/*.whl
```

Supported architectures: `x86_64`, `aarch64`

##### 6.3 Configure LinuxCNC Startup

Edit your LinuxCNC machine config file (`.ini`), point `[DISPLAY]` to the project's `start.sh`:

```ini
[DISPLAY]
DISPLAY = /path/to/my-cnc/start.sh
```

`start.sh` auto-activates the venv and launches the UI. LinuxCNC passes the ini path as `-ini` on startup; the framework handles HAL connection and NML communication automatically.

##### 6.4 Standalone Preview (no LinuxCNC)

```bash
cd my-cnc
source venv/bin/activate
python main.py
```

This mode only previews the UI appearance, without HAL/NML connection.

### Directory Structure

```
qmlvcp-builder/
├── main.py                  # Builder entry point
├── builder/                 # Builder core
│   ├── main_window.py       # Main window (three tabs)
│   ├── preview_canvas.py    # Preview canvas (drag/resize controls)
│   ├── properties_mixin.py  # Property panel logic
│   ├── field_registry.py    # Property field factory
│   ├── project_exporter.py  # Project exporter
│   ├── project_importer.py  # Project importer
│   ├── env_setup.py         # venv + PySide6 installer
│   ├── controls.py          # Control/action/binding definitions
│   ├── templates/           # QML control templates (17 .qml files)
│   ├── mainwindow.ui        # Qt Designer layout
│   └── mainwindow.qss       # Global stylesheet
├── qmlvcp/                  # Runtime library (bundled on export)
│   ├── core/                # Core modules
│   │   ├── status.py        # Machine status reader
│   │   ├── command.py       # Command dispatcher
│   │   ├── jog_controller.py# JOG controller
│   │   ├── hal_manager.py   # HAL pin manager
│   │   ├── gcode_graphics.py# Toolpath rendering engine
│   │   ├── gcode_parser.py        # G-code parser
│   │   └── fast_gcode_parser.so   # C++ accelerator (prebuilt for x86_64, recompile for aarch64)
│   └── qml/QmlVcp/               # QML control library
└── offline_wheels/                # Offline wheel storage
    ├── x86_64/
    └── aarch64/
```

### Development Guide

#### Architecture

The Builder is built on **PyQt5** (native to LinuxCNC 2.9.8+). Generated runtime projects use **PySide6**.

Three-tab architecture:
```
MainWindow (QMainWindow)
├── Tab 1: Environment (EnvManager)
│   ├── Create/detect venv
│   ├── Install PySide6 (online + offline fallback)
│   └── Status log
├── Tab 2: UI Assembly (PropertiesMixin)
│   ├── Control palette (left)
│   ├── Preview canvas (center, PreviewCanvas)
│   └── Property panel (right, dynamic form)
└── Tab 3: Project Export
    ├── Export path config
    ├── Window size config
    └── QML template rendering & export
```

#### Data Model

```python
_pages = [{
    "name": "mainwindow",
    "controls": [{
        "type": "ImageButton",
        "x": 100, "y": 200,
        "w": 120, "h": 80,
        "image": "assets/btn_start.png",
        "action": "cmd.progRun",
        "bind": "",
        "z": 0,
        "visible": True
    }, ...],
    "bg": "",
    "x": 0, "y": 0,
    "width": 1375, "height": 1000
}]
```

#### Adding a New Control

1. Create `NewControl.qml` template in `builder/templates/`
2. Register control property definitions in `builder/templates/controls.py`
3. Use `{FIELD}` placeholders in templates — auto-replaced on export

#### Predefined Actions & Status Binds

**Actions** — triggered on button click:
- `command.homeAll()` — Home all axes
- `command.setSpindle(1, 0)` — Spindle CW
- `command.programRun(0)` — Start program
- See more in `builder/controls.py` → `ACTIONS` dict

**Status Binds** — control properties follow machine state:
- `status.homedX` — X-axis homed?
- `status.spindleSpeed` — Current spindle RPM
- `status.absoluteX` — X-axis absolute position
- See more in `builder/controls.py` → `STATUS_BINDS` dict

#### Export Workflow

1. Collect all control data from pages/panels
2. Iterate controls, read corresponding QML templates from `builder/templates/`
3. Fill template placeholders with property values (e.g. `{x}`, `{y}`, `{image}`, `{action}`, `{bind}`)
4. Merge into `Main.qml`
5. Copy `qmlvcp/` runtime library, `main.py`, `backend.py` to export directory
6. Final output is a fully self-contained runnable project

---

## 参与贡献 / Contributing

> **本项目已具备基本功能，但距离成熟完善还有大量工作要做。欢迎任何人参与进来！**
> **This project has core functionality working, but is far from mature. Contributors of all skill levels are welcome!**

### 当前状态 / Current State（诚实的 / honestly）

| 方面 / Area | 状态 / Status |
|-------------|---------------|
| Builder drag-drop assembly | ✅ Working |
| Control types (17) | ✅ Buttons, LEDs, DROs, toolpath, JOG... |
| Action/binding system | ✅ Common CNC operations covered |
| Project export | ✅ One-click runnable output |
| Multi-page layout | ✅ Main/side/top/bottom panels |
| Documentation | ⚠️ Basic coverage, missing video tutorials |
| Control variety | ⚠️ Room for more industrial widgets |
| HAL pin customization | ⚠️ Only predefined bindings |
| i18n / multi-language | ❌ Not implemented |
| Unit tests | ❌ Not covered |
| Real-machine testing | ❌ Needs multi-machine validation |
| Keyboard shortcuts | ❌ Not implemented |

### 欢迎参与的方向 / Ways to Contribute

无论你是 Python/QML 开发者、LinuxCNC 用户、设计师还是文档写手，都有可以入手的地方。

#### 开发 / Development

- **新控件 / New controls** — 添加滑块、旋钮、仪表盘、波形图等控件（需同时写 QML 模板 + 属性定义）。/ Add sliders, knobs, gauges, waveform displays etc. (QML template + property definition needed).
- **HAL 引脚灵活绑定 / Flexible HAL binding** — 让用户自定义 HAL 引脚映射，而非只选预定义绑定。/ Let users map arbitrary HAL pins instead of only predefined bindings.
- **键盘快捷键 / Keyboard shortcuts** — Builder 编辑态和运行态快捷键。/ Shortcuts for Builder editing and runtime.
- **单元测试 / Unit tests** — 为核心模块补充 pytest。/ Add pytest coverage for core modules.
- **多语言 / i18n** — Builder 和导出界面都支持多语言。/ Multi-language support for both Builder and exported UIs.

#### 体验 / UX

- **更美观的默认样式 / Better default styling** — QSS/CSS 调优。 / Polish the look and feel.
- **触屏手势 / Touch gestures** — 滑动、缩放等。 / Swipe, pinch-zoom, etc.
- **控件对齐辅助 / Snap & alignment** — 画布吸附对齐、等间距分布。 / Canvas snapping, evenly-spaced distribution.

#### 内容 / Content

- **示例项目 / Example projects** — 用 Builder 搭真实 CNC 面板并贡献到 `examples/`。 / Build real panels and contribute them.
- **教程视频 / Video tutorials** — 从零到上机的完整演示。 / Full walkthrough from scratch.
- **文档翻译 / Doc translation** — 中↔英双向完善。/ Bilingual polish.
- **实机测试 / Real-machine testing** — 不同版本 LinuxCNC、不同分辨率上测试反馈。/ Test on different LinuxCNC versions and screen resolutions.

#### 如何参与 / How to Get Involved

1. **Fork** this repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "describe your change"`
4. Open a **Pull Request**

也可以在 **Issues** 中提新想法、报告 Bug、讨论设计。没有任何贡献是"太小"的——改一个错别字也是一种帮助。

Also feel free to open **Issues** for ideas, bug reports, or design discussions. No contribution is "too small" — even fixing a typo helps.

---

## License

This project is part of the QmlVcp ecosystem for LinuxCNC.
