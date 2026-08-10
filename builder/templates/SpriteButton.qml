MachImageButton {
    x: $x
    y: $y
    width: $w
    height: $h
    source: assetsDir + "/assets/$src"
    isSprite: true
    enabled: $enabled
    onClicked: $action
	$extraQml
}
