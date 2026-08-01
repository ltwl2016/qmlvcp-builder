Rectangle {
    x: $x
    y: $y
    width: $w
    height: $h
    color: "transparent"
    border.color: "white"
    border.width: 2
    clip: true
    TextField {
        anchors.fill: parent
        anchors.margins: 2
        background: Item {}
        placeholderText: "输入命令...."
        font.pixelSize: $fontSize
        onAccepted: {
            var cmd = text.trim()
            if (cmd !== "") {
                backend.submitCommand(cmd)
                text = ""
            }
        }
    }
}