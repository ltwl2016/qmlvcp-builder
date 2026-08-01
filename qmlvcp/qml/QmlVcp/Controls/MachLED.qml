import QtQuick

// qmlvcp 内置控件：双帧 LED 指示灯（精灵图左右/上下各一帧）
Item {
    id: root
    
    property string source: ""
    property bool active: false
    property bool isHorizontal: true
    
    width: isHorizontal ? (ledImage.sourceSize.width / 2) : ledImage.sourceSize.width
    height: isHorizontal ? ledImage.sourceSize.height : (ledImage.sourceSize.height / 2)
    
    clip: true
    
    Image {
        id: ledImage
        source: root.source
        x: root.active && root.isHorizontal ? -width / 2 : 0
        y: root.active && !root.isHorizontal ? -height / 2 : 0
    }
}
