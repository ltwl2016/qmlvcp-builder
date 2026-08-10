ToggleButton {
    x: $x
    y: $y
    width: $w
    height: $h
    source: assetsDir + "/assets/$src"
    pressedSource: $pressedSource
    latched: $bind
    enabled: $enabled
    onPressed: $action_press
    onReleased: $action_release
	$extraQml
}
