Rectangle {
    x: $x
    y: $y
    width: $w
    height: $h
    color: "transparent"
    border.color: "black"
    border.width: 2
    
    TextField {
        anchors.fill: parent
        anchors.margins: 2
        placeholderText: "输入 MDI 指令，按 Enter 执行..."
        font.pixelSize: $fontSize
        color: "#222"
        background: Item {}
        verticalAlignment: Text.AlignVCenter
        onAccepted: {
            var cmd = text.trim()
            if (cmd !== "") {
                backend.submitCommand(cmd)
                text = ""
            }
        }
    }
}
