GCodeViewer {
    x: $x
    y: $y
    width: $w
    height: $h
	gcodeLines: backend.programLines
    activeLine: backend.lineNumber
    allowSelection: backend.interpState === 1
}