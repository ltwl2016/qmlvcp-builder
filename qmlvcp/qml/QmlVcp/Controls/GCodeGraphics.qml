// QmlVcp Builder - CNC HMI Visual Construction Toolkit
// Copyright (C) 2026 ltwl2016
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import QtQuick
import QtQuick.Controls
import QtQuick3D
import QmlVcp 1.0

Item {
    id: root
    
    // ==========================================
    // 暴露给外部的数据接口，自动下沉绑定到 backend（保持架构整洁）
    // ==========================================
    property real toolX: typeof backend !== "undefined" ? backend.absoluteToolX : 0
    property real toolY: typeof backend !== "undefined" ? backend.absoluteToolY : 0
    property real toolZ: typeof backend !== "undefined" ? backend.absoluteToolZ : 0
    property real toolA: typeof backend !== "undefined" ? backend.absoluteToolA : 0
    property real toolB: typeof backend !== "undefined" ? backend.absoluteToolB : 0
    property string gcodeFile: typeof backend !== "undefined" ? backend.programFile : ""
    
    // 纯前端信号：通知上层目前 3D 计算结束
    signal loadingFinished()
    
    // 监听文件加载/关闭事件
    onGcodeFileChanged: {
        // 无论加载新文件，还是关闭文件，都先清空之前的实时加工光束轨迹
        root.clearLiveTrajectory();
        
        if (!gcodeFile || gcodeFile === "") {
            // 当文件被关闭时，恢复 3D 锚点到机床正中心
            root.targetPivotX = (root.machineMaxX + root.machineMinX) / 2;
            root.targetPivotY = 0;
            root.targetPivotZ = -(root.machineMaxY + root.machineMinY) / 2;
            
            // 恢复默认摄像机平移与缩放
            sceneRoot.x = 0;
            sceneRoot.y = 0;
            root.cameraY = 800;
            root.cameraZ = 800;
            root.cameraZoom = 1.0;
        }
    }
    
    property real machineMinX: typeof backend !== "undefined" ? backend.machineMinX : 0
    property real machineMaxX: typeof backend !== "undefined" ? backend.machineMaxX : 500
    property real machineMinY: typeof backend !== "undefined" ? backend.machineMinY : 0
    property real machineMaxY: typeof backend !== "undefined" ? backend.machineMaxY : 500
    property real machineMinZ: typeof backend !== "undefined" ? backend.machineMinZ : 0
    property real machineMaxZ: typeof backend !== "undefined" ? backend.machineMaxZ : 300
    // 坐标轴长度 (预留的数据接口)
    property real axisLength: 24
    // 坐标轴偏移量 (预留的数据接口，可用来在 3D 空间中移动【机床】原点指示器的位置)
    property real axisOffsetX: 0
    property real axisOffsetY: 0
    property real axisOffsetZ: 0
    
    // 工件坐标系参数 (G54 等工作零点相对于机床零点的物理坐标)
    property real workOffsetX: typeof backend !== "undefined" ? backend.workOffsetX : 200
    property real workOffsetY: typeof backend !== "undefined" ? backend.workOffsetY : 200
    property real workOffsetZ: typeof backend !== "undefined" ? backend.workOffsetZ : 100
    property bool showWorkAxes: true
    
    // 摄像机参数 (预留的数据接口)
    property bool isOrthographic: false // 是否使用正交（等轴测）视图
    property real cameraX: 0
    property real cameraY: 800
    property real cameraZ: 800
    property real cameraRotX: -40
    property real cameraRotY: 0
    property real cameraRotZ: 0
    property real cameraZoom: 1.0 // 正交相机的缩放比例倍数
    
    // 摄像机目标旋转锚点
    property real targetPivotX: (root.machineMaxX + root.machineMinX) / 2
    property real targetPivotY: 0
    property real targetPivotZ: -(root.machineMaxY + root.machineMinY) / 2
    
    // ==========================================
    // 防断层跳线处理 (光带乱窜修复)
    // ==========================================
    // 监听工作偏置变化（例如执行了清零/G10 L20），一旦坐标系突变，切断旧迹避免灾难性跳线
    onWorkOffsetXChanged: clearLiveTrajectory()
    onWorkOffsetYChanged: clearLiveTrajectory()
    onWorkOffsetZChanged: clearLiveTrajectory()

    // 清除实时轨迹的对外接口
    function clearLiveTrajectory() {
        if (liveTrajectory) liveTrajectory.clearPath();
    }
    
    // 定时采样真实刀具坐标，喂给实时刀路生成器
    Timer {
        running: true
        repeat: true
        interval: 30 // ~33 FPS
        onTriggered: {
            if (liveTrajectory) {
                // 将真实的坐标以及当前的 LinuxCNC 运动类型（用于判断 G0/G1）传给底层
                liveTrajectory.appendPoint(root.toolX, root.toolY, root.toolZ, backend.motionType);
            }
        }
    }

    // Qt6 官方正统的现代 3D 引擎节点
    View3D {
        id: view3D
        anchors.fill: parent
        
        // 动态切换摄像机类型
        camera: root.isOrthographic ? orthoCamera : perspCamera
        
        // 环境设置
        environment: SceneEnvironment {
            clearColor: "#1a1a1a"
            backgroundMode: SceneEnvironment.Color
        }

        // 透视摄像机 (近大远小)
        PerspectiveCamera {
            id: perspCamera
            x: root.cameraX
            y: root.cameraY
            z: root.cameraZ
            eulerRotation.x: root.cameraRotX
            eulerRotation.y: root.cameraRotY
            eulerRotation.z: root.cameraRotZ
            
            // 视野角度(Field Of View)，默认是 60。
            // 调小这个值（如 30），可以拉长焦距，透视的畸变就会显著减弱；调大（如 90）则会变成广角鱼眼镜头。
            fieldOfView: 30 
        }
        
        // 正交摄像机 (等轴测视图，没有近大远小，完全工业制图视角)
        OrthographicCamera {
            id: orthoCamera
            x: root.cameraX
            y: root.cameraY
            z: root.cameraZ
            eulerRotation.x: root.cameraRotX
            eulerRotation.y: root.cameraRotY
            eulerRotation.z: root.cameraRotZ
            horizontalMagnification: root.cameraZoom
            verticalMagnification: root.cameraZoom
        }

        // 光源
        DirectionalLight {
            eulerRotation.x: -45
            eulerRotation.y: 45
            ambientColor: Qt.rgba(0.5, 0.5, 0.5, 1.0)
        }

        // 旋转节点，用来实现鼠标拖动 3D 旋转的功能
        Node {
            id: sceneRoot
            
            // 开局默认的等距 -40 度视角（将底盘旋转，摄像机保持居中）
            eulerRotation.y: -40
            
            // 【核心修复】：将 3D 画布的旋转锚点（Pivot）设定为机床或零件的物理几何中心！
            // 这样做有两个巨大好处：
            // 1. 鼠标左键旋转时，画面会完美围绕目标中心旋转，再也不会以 (0,0,0) 为原点像甩大锤一样乱晃。
            // 2. 引擎会自动把这个锚点平移到世界原点，所以它开局就会完美居中在屏幕正中央！
            pivot: Qt.vector3d(root.targetPivotX, root.targetPivotY, root.targetPivotZ)
            

            // ==========================================
            // 机床绝对原点指示器 (红=X, 绿=Y, 蓝=Z)
            // ==========================================
            // 我们通过 Python 中的 AxesGeometry 生成了原生的 Lines 拓扑结构
            Model {
                // 将外部传进来的偏移量接口，映射到坐标轴模型的物理位置
                x: root.axisOffsetX
                y: root.axisOffsetZ
                z: -root.axisOffsetY
                
                geometry: AxesGeometry {
                    axisLength: root.axisLength * 0.01 // 绑定刚才预留的数据接口
                }
                materials: [ DefaultMaterial { 
                    lighting: DefaultMaterial.NoLighting 
                    vertexColorsEnabled: true 
                    opacity: 0.9  // 设置透明度为 90%
                } ]
            }
            
            // ==========================================
            // 工件坐标系原点指示器 (G54 等)
            // ==========================================
            Model {
                visible: root.showWorkAxes
                // 将工件偏移坐标进行 3D 空间映射
                x: root.workOffsetX
                y: root.workOffsetZ
                z: -root.workOffsetY
                
                geometry: AxesGeometry {
                    axisLength: root.axisLength // 工件坐标轴略短于机床绝对坐标轴，便于肉眼区分
                }
                materials: [ DefaultMaterial { 
                    lighting: DefaultMaterial.NoLighting 
                    vertexColorsEnabled: true 
                    opacity: 0.9  // 设置透明度为 90%
                } ]
            }
            
            // ==========================================
            // G 代码刀路轨迹预览
            // ==========================================
            Model {
                // 刀路属于工件坐标系，所以偏移量和工件坐标轴完全一致！
                x: root.workOffsetX
                y: root.workOffsetZ
                z: -root.workOffsetY
                
                geometry: TrajectoryGeometry {
                    gcodeFile: root.gcodeFile // 当外部传入路径时，自动触发多线程解析
                    onPathBoundsParsed: (minX, maxX, minY, maxY, minZ, maxZ) => {
                        // 计算 G代码 自身中心点
                        var cX = (minX + maxX) / 2.0;
                        var cY = (minY + maxY) / 2.0;
                        var cZ = (minZ + maxZ) / 2.0;
                        
                        // 计算基于工件坐标系的绝对3D中心点 (注意 QML 这里的坐标轴映射)
                        root.targetPivotX = root.workOffsetX + cX;
                        root.targetPivotY = root.workOffsetZ + cZ;
                        root.targetPivotZ = -(root.workOffsetY + cY);
                        
                        // 重置摄像机平移，画面对中
                        sceneRoot.x = 0;
                        sceneRoot.y = 0;
                        
                        // 计算最大尺寸，动态调整摄像机距离
                        var sizeX = maxX - minX;
                        var sizeY = maxY - minY;
                        var sizeZ = maxZ - minZ;
                        var maxSize = Math.max(sizeX, sizeY, sizeZ);
                        
                        // 防止空文件或者极小文件导致无限放大
                        if (maxSize < 10) maxSize = 10;
                        
                        // 1. 调整摄像机的前后距离（数字越大，离得越远）
                        root.cameraZ = maxSize * 2.0;
                        
                        // 2. 调整摄像机的物理高度（数字越大，俯视感越强；数字越小，越接近平视）
                        root.cameraY = maxSize * 1.5;
                        
                        // 3. 正交相机的缩放倍率
                        root.cameraZoom = maxSize * 1.5;
                        
                        // 通知前端由于模型生成完毕，可以关闭动画了
                        root.loadingFinished();
                    }
                }
                materials: [ DefaultMaterial { 
                    lighting: DefaultMaterial.NoLighting 
                    vertexColorsEnabled: true // 使用 Python 后台算出的颜色 (G0红，G1绿等)
                    opacity: 0.3  // 设置透明度为 50%
                } ]
            }
            
            // ==========================================
            // 实时走刀轨迹 (Live Trajectory)
            // ==========================================
            Model {
                // 同样属于工件坐标系
                x: root.workOffsetX
                y: root.workOffsetZ
                z: -root.workOffsetY
                
                geometry: LiveTrajectoryGeometry {
                    id: liveTrajectory
                }
                materials: [ DefaultMaterial { 
                    lighting: DefaultMaterial.NoLighting 
                    vertexColorsEnabled: true
                    lineWidth: 1.0 // 在这里修改 实时走刀光束的线条粗细（加粗到 3.0 更显眼）
                    opacity: 0.7  // 设置透明度为 50%
                } ]
            }
            
            // ==========================================
            // 机床虚拟边界 (极细线框方盒)
            // ==========================================
            // 直接把坐标边界传给 Python，Python 会自动构建首尾相连的 1 像素 LineStrip 数组！
            Model {
                geometry: BoundsGeometry {
                    minX: root.machineMinX
                    maxX: root.machineMaxX
                    minY: root.machineMinY
                    maxY: root.machineMaxY
                    minZ: root.machineMinZ
                    maxZ: root.machineMaxZ
                }
                materials: [ DefaultMaterial { 
                    diffuseColor: "red"
                    lighting: DefaultMaterial.NoLighting 
                } ]
            }
            // 刀具模拟 (五轴联动支持：通过外层节点精准围绕“刀尖”旋转)
            Node {
                // 物理绝对坐标 = 工件零点偏移 + 刀具当前工件坐标
                x: Number(root.workOffsetX) + Number(root.toolX)
                y: Number(root.workOffsetZ) + Number(root.toolZ)
                z: -(Number(root.workOffsetY) + Number(root.toolY))
                
                // 机床 A 轴：绕数控 X 轴旋转（对应 3D 空间的 X 轴）
                eulerRotation.x: Number(root.toolA)
                // 机床 B 轴：绕数控 Y 轴旋转（对应 3D 空间的 -Z 轴，因此取反）
                eulerRotation.z: -Number(root.toolB)
                
                Model {
                    source: "#Cone"
                    
                    y: 20
                    
                    eulerRotation.x: 180
                    scale: Qt.vector3d(0.15, 0.2, 0.15)
                    materials: [ DefaultMaterial { 
                        diffuseColor: "white"
                        opacity: 0.7  // 设置透明度为 50%
                    } ]
                }
            }
        }
    }

    // 鼠标 3D 交互
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        
        // 鼠标双击时清除屏幕上乱晃的残余走刀轨迹
        onDoubleClicked: root.clearLiveTrajectory()
        
        property real lastX: 0
        property real lastY: 0

        onPressed: (mouse) => {
            lastX = mouse.x
            lastY = mouse.y
        }

        onPositionChanged: (mouse) => {
            var dx = mouse.x - lastX
            var dy = mouse.y - lastY
            
            if (mouse.buttons & Qt.RightButton) {
                // 右键：旋转
                sceneRoot.eulerRotation.y += dx * 0.5
                sceneRoot.eulerRotation.x += dy * 0.5
            } else if (mouse.buttons & Qt.LeftButton) {
                // 左键：平移（这里根据摄像头高度做一点比例适配，越远移得越快）
                if (!root.isOrthographic) {
                    var panSpeed = 0.8 * (root.cameraY / 800.0);
                    if (panSpeed < 0.1) panSpeed = 0.1;
                    sceneRoot.x += dx * panSpeed;
                    sceneRoot.y -= dy * panSpeed; 
                } else {
                    var orthoPanSpeed = 1.0 / root.cameraZoom;
                    sceneRoot.x += dx * orthoPanSpeed;
                    sceneRoot.y -= dy * orthoPanSpeed;
                }
            }
            
            lastX = mouse.x
            lastY = mouse.y
        }
        
        onWheel: (wheel) => {
            // 计算缩放比例 (滚轮向前为正)
            var zoomDelta = wheel.angleDelta.y * 0.001;
            
            if (!root.isOrthographic) {
                // 【透视相机定点推拉修复】
                // 必须同时、等比例地缩放摄像机的 X, Y, Z！
                // 如果只改 Z 不改 Y，摄像机的视线角度其实是斜的，就会发生画面往下滑的“漂移”，也就是你说的“没对准中心”。
                var scale = 1.0 - zoomDelta;
                var newX = root.cameraX * scale;
                var newY = root.cameraY * scale;
                var newZ = root.cameraZ * scale;
                
                // 限制最近距离，防止穿透
                if (Math.abs(newZ) >= 10 && Math.abs(newY) >= 10) {
                    root.cameraX = newX;
                    root.cameraY = newY;
                    root.cameraZ = newZ;
                }
            } else {
                // 【正交相机缩放】中心不变，直接放大渲染系数
                root.cameraZoom *= (1.0 + zoomDelta);
                if (root.cameraZoom < 0.1) root.cameraZoom = 0.1;
            }
        }
    }   
}
