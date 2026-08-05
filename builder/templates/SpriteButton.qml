MachImageButton {
    x: $x
    y: $y
    width: $w
    height: $h
    source: assetsDir + "/assets/$src"
    pressedSource: "$pressedSource"
    isSprite: true
    enabled: $enabled
    onClicked: $action
	$extraQml
}