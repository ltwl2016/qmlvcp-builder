import QtQuick
import QtQuick.Controls.Basic

Rectangle {
    id: root
    width: 512
    height: 366
    color: "transparent"
    border.color: "white"
    border.width: 2

    property int activeLine: -1      
    property var gcodeLines: []      
    
    // 新增：用户手动选中的行号
    property int selectedLine: -1
    // 新增：是否允许用户手动点击选择（通常在机器运行时禁止）
    property bool allowSelection: true
    // 当机器突然开始运行（allowSelection变成false）时，自动清空之前的选中状态
    onAllowSelectionChanged: {
        if (!allowSelection) {
            selectedLine = -1;
            scrollToLine(activeLine);
        }
    }
    
    // 新增：向外提供一个强制滚动的函数，供外部按钮（如重置）调用
    function scrollToLine(line) {
        if (line >= 0 && line < listView.count) {
            listView.currentIndex = line;
            listView.positionViewAtIndex(line, ListView.Center);
        }
    }

    // 新增：输出接口信号，当用户选中某行时向外发送
    signal lineSelected(int lineIndex)

    // 解析 G代码语法高亮 HTML 转换函数
    function highlightGCode(str) {
        if (!str) return "";
        var s = str.toString();
        // 终极绝杀：彻底抛弃所有 HTML 转义符（&lt; 或者 &#60;）！
        // 直接强制将原生的半角尖括号，替换为视觉上完全一样的【全角尖括号】（Unicode: FF1C / FF1E）。
        // 这意味着进入 Qt 引擎的内容里，物理上根本就不存在能引发 HTML 混淆的 "<" 字符了！它就是个字罢了！
        s = s.replace(/</g, "＜").replace(/>/g, "＞");
        
        // 提取小括号以及分号之后的注释，防止内部代码被错误高亮
        var commentRegex = /(\(.*?\)|;.*)/g;
        var parts = s.split(commentRegex);
        for (var i = 0; i < parts.length; i++) {
            if (parts[i].length > 0 && (parts[i].charCodeAt(0) === 40 || parts[i].charCodeAt(0) === 59)) {
                // 注释：深石板灰 (与淡青色背景最融合的低调冷色)，不带下划线不抢镜
                parts[i] = '<font color="#2F4F4F"><i>' + parts[i] + '</i></font>';
            } else {
                var p = parts[i];
                // 单次贯穿式正则替换，彻底防止后层正则误杀前层生成的 HTML hex 颜色代码 (如 #FAF207 中包含 F 数字)
                p = p.replace(/([GMXYZABCIJKRFSTN])([+\-]?\d+(\.\d*)?)/gi, function(match, letter, number) {
                    var l = letter.toUpperCase();
                    // N行号: 沿用注释的深石板灰与斜体，并将数字本身也一并染色，整体弱化
                    if (l === 'N') return '<font color="#2F4F4F"><i>' + letter + number + '</i></font>';
                    // G指令: 深钴蓝 (高对比度冷色)
                    if (l === 'G') return '<font color="#0000CD"><b>' + letter + '</b></font>' + number;
                    // M指令: 猩红 (危险、警示动作)
                    if (l === 'M') return '<font color="#7a0b67"><b>' + letter + '</b></font>' + number;
                    // XYZ坐标: 烧结橙棕色="#59829cff" 
                    if ('XYZABC'.indexOf(l) !== -1) return '<font color="#1500ff">' + letter + '</font>' + number;
                    // IJK圆弧: 深洋红 (与橙棕色能拉开肉眼层次)
                    if ('IJKR'.indexOf(l) !== -1) return '<font color="#8B008B">' + letter + '</font>' + number;
                    // FST速度段: 深翡翠绿 (护眼且有别于其他参数)
                    if ('FST'.indexOf(l) !== -1) return '<font color="#006400">' + letter + '</font>' + number;
                    return match;
                });
                parts[i] = p;
            }
        }
        // 用纯净无任何冗余属性的 html 根标签让 Qt 的 Text.RichText 彻底折服
        return '<html>' + parts.join('') + '</html>';
    }

    // 没有代码时的占位假象
    Rectangle {
        visible: listView.count === 0
        x: 2; y: 178; width: parent.width - 4; height: 20
        color: "white"
    }
    
    Rectangle {
        visible: listView.count === 0
        x: parent.width - 17; y: 2; width: 15; height: parent.height - 4
        color: "#f0f0f0"
        border.color: "#a0a0a0"
        border.width: 1
        Rectangle {
            x: 1; y: 15; width: 13; height: 40
            color: "#c0c0c0"
            border.color: "#a0a0a0"
            border.width: 1
        }
        Text { text: "▲"; font.pixelSize: 8; x: 2; y: 2 }
        Text { text: "▼"; font.pixelSize: 8; x: 2; y: parent.height - 12 }
    }

    // 真实的 ListView，用于显示 G 代码
    ListView {
        id: listView
        anchors.fill: parent
        anchors.margins: 2
        clip: true
        model: root.gcodeLines

        delegate: Rectangle {
            width: listView.width
            height: 20
            
            // 背景颜色逻辑：执行行(白) > 选中行(白) > 默认(透明)
            color: {
                if (index === root.activeLine) return "white";
                if (index === root.selectedLine) return "white"; // 选中行高亮改为白色
                return "transparent";
            }

            Text {
                x: 10
                anchors.verticalCenter: parent.verticalCenter
                textFormat: Text.RichText
                text: root.highlightGCode(modelData)
                color: "black"
                font.pixelSize: 18
                font.family: "Monospace"
                font.bold: index === root.activeLine
            }
            
            // 新增：点击选择功能
            MouseArea {
                anchors.fill: parent
                enabled: root.allowSelection // 核心：绑定是否允许点击的属性
                onClicked: {
                    root.selectedLine = index;
                    root.lineSelected(index);
                }
            }
        }

        // 自动跟随活动行滚动
        onCurrentIndexChanged: positionViewAtIndex(currentIndex, ListView.Center)
        
        ScrollBar.vertical: ScrollBar {
            id: vbar
            policy: listView.count > 0 ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
            
            // 定制滚动条外观，使其与未加载时的 15px 经典滚动条一模一样
            contentItem: Rectangle {
                implicitWidth: 15
                radius: 0
                color: vbar.pressed ? "#a0a0a0" : "#c0c0c0"
                border.color: "#a0a0a0"
                border.width: 1
            }
            background: Rectangle {
                implicitWidth: 15
                color: "#f0f0f0"
                border.color: "#a0a0a0"
                border.width: 1
            }
        }
    }

    // 当 activeLine 改变时，更新 ListView 的当前索引以便自动滚动
    onActiveLineChanged: {
        if (activeLine >= 0 && activeLine < listView.count) {
            listView.currentIndex = activeLine
        }
    }
}
