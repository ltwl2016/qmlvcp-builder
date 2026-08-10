Text {
    x: $x
    y: $y
    text: Number($bind).toFixed(4)
    width: $w
    horizontalAlignment: Text.AlignRight
    font.pixelSize: $fontSize
    color: "$color"
    $extraQml
}
