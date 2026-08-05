Item {
    x: $x
    y: $y
    width: $w
    height: $h
    property bool _flash: false
    Image {
        anchors.fill: parent
        source: assetsDir + "/assets/$src"
        fillMode: Image.Stretch
        sourceClipRect: backend.machineOn ? Qt.rect($w, 0, $w, $h) :
                        (parent._flash ? Qt.rect($w, 0, $w, $h) : Qt.rect(0, 0, $w, $h))
    }
    MouseArea {
        anchors.fill: parent
        onClicked: $action
    }
    Timer {
        running: !backend.machineOn
        repeat: true
        interval: 500
        onTriggered: parent._flash = !parent._flash
    }
}