Item {
    x: $x
    y: $y
    width: $w
    height: $h
    property bool flashState: false

    Timer {
        running: $bind
        repeat: true
        interval: $interval
        onTriggered: parent.flashState = !parent.flashState
        onRunningChanged: if (!running) parent.flashState = false
    }

    Image {
        anchors.fill: parent
        source: assetsDir + "/assets/$src"
        sourceClipRect: ($bind && parent.flashState) ? Qt.rect($w, 0, $w, $h) : Qt.rect(0, 0, $w, $h)
    }
}