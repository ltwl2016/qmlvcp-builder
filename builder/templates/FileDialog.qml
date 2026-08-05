FileDialog {
    id: $id
    title: "$title"
    nameFilters: ["G-Code 文件 (*.NC *.nc *.ngc *.gcode *.tap)", "所有文件 (*)"]
    onAccepted: {
        var path = currentFile.toString()
        path = path.replace(/^(file:\/{2,3})/, "/").replace(/^\/\//, "/")
        backend.loadProgram(path)
    }
}