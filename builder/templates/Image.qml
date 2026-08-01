Image {
    x: $x
    y: $y
    width: $w
    height: $h
    source: assetsDir + "/assets/$src"
    sourceClipRect: $sourceClipRect
    fillMode: Image.PreserveAspectFit
	$extraQml
}