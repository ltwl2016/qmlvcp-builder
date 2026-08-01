import QtQuick
import QmlVcp.Controls 1.0

// 最小示例 — 替换为你自己的界面
Item {
    width: 1024
    height: 768

    // 背景（替换为你 PS 画的全屏背景图）
    Image {
        anchors.fill: parent
        source: "assets/bg.png"
    }

    // 示例：一个自定义按钮
    MachImageButton {
        x: 100; y: 100
        source: "assets/btn_start.png"
        onClicked: console.log("按钮被点击")
    }

    // 示例：X 轴 DRO 读数
    Text {
        x: 200; y: 200
        text: backend.displayToolX.toFixed(4)
        font.pixelSize: 28
        color: "#00ff00"
    }

    // 示例：JOG 方向键
    MachImageButton {
        x: 100; y: 300
        source: "assets/ArrowX+.png"
        onPressed:  backend.jogAxis(0, 1)
        onReleased: backend.jogAxis(0, 0)
    }
}
