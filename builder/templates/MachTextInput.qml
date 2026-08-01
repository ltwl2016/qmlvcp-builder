MachTextInput {
    x: $x
    y: $y
    width: $w
    height: $h
    text: $bind
    font.pixelSize: $fontSize
    decimals: $decimals
	horizontalAlignment: TextInput.AlignRight
    onAccepted: $action
	$extraQml
}