Rectangle {
	id: $id
    x: $x
    y: $y
    width: $w
    height: $h
    color: "$bgColor"
    border.color: "white"
    border.width: 2
    clip: true
    GCodeGraphics {
        anchors.fill: parent
		anchors.margins: 2
        showWorkAxes: $showWorkAxes
        isOrthographic: $isOrthographic
        cameraZoom: $cameraZoom
    }
    Text {
        z: 1
        x: 5
        y: 5
        text: "刀具: " + status.toolInSpindle
        font.pixelSize: 12
        font.bold: true
        color: "white"
    }
}
