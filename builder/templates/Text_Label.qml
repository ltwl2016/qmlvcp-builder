Rectangle {
    x: $x
    y: $y
    width: $w
    height: $h
    color: "$bgColor"
    border.color: "$borderC"
    border.width: $borderW

    Text {
        anchors.fill: parent
        text: $bind
        font.pixelSize: $fontSize
        color: "$color"
        verticalAlignment: Text.AlignVCenter
    }
}