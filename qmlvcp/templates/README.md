# qmlvcp 模板项目

## 目录结构

```
my-cnc/
├── main.py          ← 入口（复制即用）
├── backend.py       ← 你的业务逻辑
├── qml/
│   ├── qmldir
│   └── Main.qml      ← 你的界面
└── assets/          ← 你的贴图（按钮/背景/LED/...）
```

## 快速开始

1. 复制 `template/` 到你的项目目录
2. 在 `backend.py` 中添加你的自定义 Property 和 Slot
3. 用 PS 画出按钮/LED/背景贴图，放入 `assets/`
4. 在 `Main.qml` 里用固定坐标拼装界面

## QML 可用上下文

| 变量 | 类型 | 用途 |
|------|------|------|
| `backend` | Backend | 你的业务逻辑（自定义 Property/Slot） |
| `status` | Status | 机床实时状态（位置/速度/模式/报警） |
| `command` | Command | 指令下发（MDI/程序控制） |
| `jog` | JogController | JOG 控制（速度/步距/模式） |
| `hal` | HalManager | HAL 引脚管理 |

## 内置控件 (import QmlVcp.Controls 1.0)

| 控件 | 说明 |
|------|------|
| `MachImageButton` | 贴图按钮（支持精灵图多帧） |
| `MachLED` | 双帧 LED 指示灯 |
| `GCodeGraphics` | 3D 刀路可视化 |
| `GCodeViewer` | G 代码列表浏览器 |
| `MachTextInput` | 工业风文本输入 |
| `RunFromHereDialog` | 断点续跑弹窗 |
