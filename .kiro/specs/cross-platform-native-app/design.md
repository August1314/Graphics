# 设计文档 - 跨平台原生绘图系统

## 概述

本文档描述了跨平台原生绘图系统的技术设计方案。该系统采用 C++ 实现高性能渲染引擎，使用 Vue.js 构建现代化用户界面，通过 CMake 实现跨平台构建，支持 Linux、macOS 和 Windows 三大操作系统。

系统的核心设计理念是：
- **性能优先**：使用 C++ 和 GPU 加速确保高性能渲染
- **跨平台**：统一代码库，最小化平台特定代码
- **模块化**：清晰的架构分层，便于维护和扩展
- **现代化**：采用现代 C++17 标准和 Vue 3 Composition API
- **算法多样性**：实现多种光栅化算法，支持算法切换和对比

## 架构设计

### 整体架构

系统采用三层架构设计：

```
┌─────────────────────────────────────────────────────┐
│         Electron Renderer Process (Vue.js)          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Toolbar  │ │ Canvas   │ │ Property │            │
│  │ Component│ │ Component│ │ Panel    │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────┘
                ↕ Electron IPC (ipcRenderer)
┌─────────────────────────────────────────────────────┐
│           Electron Main Process (Node.js)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Window   │ │ Menu     │ │ File     │            │
│  │ Manager  │ │ Manager  │ │ Manager  │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────┘
                ↕ N-API (Native Addon)
┌─────────────────────────────────────────────────────┐
│         C++ Native Module                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Document │ │ Tool     │ │ Command  │            │
│  │ Manager  │ │ Manager  │ │ Stack    │            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Raster   │ │ Shape    │ │ Renderer │            │
│  │ Algorithms│ │ Library  │ │ (Skia)   │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────┘
```

### 技术栈选择

#### C++ 渲染引擎
- **语言标准**: C++17
- **图形库**: Skia (Google 的 2D 图形库)
  - 跨平台支持优秀
  - GPU 加速
  - 高性能渲染
  - 丰富的 API
- **构建系统**: CMake 3.20+
- **依赖管理**: vcpkg
- **测试框架**: Google Test
- **JSON 库**: nlohmann/json

#### Vue.js 用户界面
- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript 5.0+
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **测试框架**: Vitest

#### 跨平台集成
- **应用框架**: Electron
  - 统一的跨平台 WebView（Chromium）
  - 成熟的 IPC 机制（ipcMain/ipcRenderer）
  - 丰富的 Node.js 生态支持
  - 简化的打包和分发流程
- **IPC 机制**: Electron IPC (主进程 ↔ 渲染进程)
- **原生模块**: Node.js Native Addons (N-API) 用于 C++ 集成


## 组件和接口

### C++ 核心组件

#### 1. 渲染引擎 (RenderingEngine)

负责所有图形的渲染工作，包括光栅化算法实现和 GPU 加速渲染。

**主要类：**

```cpp
class RenderingEngine {
public:
    void initialize(int width, int height);
    void render(const std::vector<Shape*>& shapes);
    void setViewTransform(const Matrix& transform);
    void setRasterAlgorithm(RasterAlgorithm algorithm);
    SkBitmap exportToBitmap();
    
private:
    sk_sp<SkSurface> surface_;
    SkCanvas* canvas_;
    Matrix viewTransform_;
    std::unique_ptr<RasterAlgorithmFactory> algorithmFactory_;
};
```

#### 2. 光栅化算法模块 (RasterAlgorithms)

实现各种光栅化算法，支持算法切换和性能对比。

**算法接口：**

```cpp
class IRasterAlgorithm {
public:
    virtual ~IRasterAlgorithm() = default;
    virtual void drawLine(int x1, int y1, int x2, int y2, const Color& color) = 0;
    virtual void drawCircle(int cx, int cy, int radius, const Color& color) = 0;
    virtual void drawEllipse(int cx, int cy, int rx, int ry, const Color& color) = 0;
    virtual void fillPolygon(const std::vector<Point>& points, const Color& color) = 0;
    virtual std::string getName() const = 0;
    virtual PerformanceMetrics getMetrics() const = 0;
};

// 具体算法实现
class BresenhamLineAlgorithm : public IRasterAlgorithm { /* ... */ };
class DDALineAlgorithm : public IRasterAlgorithm { /* ... */ };
class MidpointCircleAlgorithm : public IRasterAlgorithm { /* ... */ };
class ScanlineFillAlgorithm : public IRasterAlgorithm { /* ... */ };
```

#### 3. 图形库 (ShapeLibrary)

定义所有图形类型及其属性。

**基类和派生类：**

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual void render(RenderingEngine& engine) = 0;
    virtual bool hitTest(const Point& point) const = 0;
    virtual BoundingBox getBounds() const = 0;
    virtual nlohmann::json toJson() const = 0;
    virtual void fromJson(const nlohmann::json& json) = 0;
    
    // 通用属性
    std::string id;
    Color strokeColor;
    float strokeWidth;
    StrokeStyle strokeStyle;
    Color fillColor;
    float opacity;
    Matrix transform;
};

class PointShape : public Shape { /* ... */ };
class LineShape : public Shape { /* ... */ };
class RectShape : public Shape { /* ... */ };
class CircleShape : public Shape { /* ... */ };
class EllipseShape : public Shape { /* ... */ };
class PolygonShape : public Shape { /* ... */ };
class PathShape : public Shape { /* ... */ };
```


#### 4. 文档管理器 (DocumentManager)

管理绘图文档的状态、图形集合和文件 I/O。

```cpp
class DocumentManager {
public:
    void newDocument();
    bool loadDocument(const std::string& filepath);
    bool saveDocument(const std::string& filepath);
    
    void addShape(std::unique_ptr<Shape> shape);
    void removeShape(const std::string& shapeId);
    Shape* getShape(const std::string& shapeId);
    const std::vector<Shape*>& getAllShapes() const;
    
    void setModified(bool modified);
    bool isModified() const;
    
    nlohmann::json serialize() const;
    void deserialize(const nlohmann::json& json);
    
private:
    std::vector<std::unique_ptr<Shape>> shapes_;
    std::string filepath_;
    bool modified_;
    DocumentMetadata metadata_;
};
```

#### 5. 命令系统 (CommandSystem)

实现撤销/重做功能的命令模式。

```cpp
class ICommand {
public:
    virtual ~ICommand() = default;
    virtual void execute() = 0;
    virtual void undo() = 0;
    virtual std::string getDescription() const = 0;
};

class CommandStack {
public:
    void execute(std::unique_ptr<ICommand> command);
    void undo();
    void redo();
    bool canUndo() const;
    bool canRedo() const;
    void clear();
    
private:
    std::vector<std::unique_ptr<ICommand>> undoStack_;
    std::vector<std::unique_ptr<ICommand>> redoStack_;
    size_t maxStackSize_ = 100;
};

// 具体命令实现
class AddShapeCommand : public ICommand { /* ... */ };
class RemoveShapeCommand : public ICommand { /* ... */ };
class ModifyShapeCommand : public ICommand { /* ... */ };
class MoveShapeCommand : public ICommand { /* ... */ };
```

#### 6. 工具管理器 (ToolManager)

管理各种绘图工具的状态和行为。

```cpp
class ITool {
public:
    virtual ~ITool() = default;
    virtual void onMouseDown(const Point& point) = 0;
    virtual void onMouseMove(const Point& point) = 0;
    virtual void onMouseUp(const Point& point) = 0;
    virtual void onCancel() = 0;
    virtual void render(RenderingEngine& engine) = 0;
    virtual std::string getName() const = 0;
};

class ToolManager {
public:
    void registerTool(const std::string& name, std::unique_ptr<ITool> tool);
    void setActiveTool(const std::string& name);
    ITool* getActiveTool();
    
    void handleMouseDown(const Point& point);
    void handleMouseMove(const Point& point);
    void handleMouseUp(const Point& point);
    
private:
    std::map<std::string, std::unique_ptr<ITool>> tools_;
    ITool* activeTool_ = nullptr;
};

// 具体工具实现
class SelectTool : public ITool { /* ... */ };
class LineTool : public ITool { /* ... */ };
class RectTool : public ITool { /* ... */ };
class CircleTool : public ITool { /* ... */ };
class PolygonTool : public ITool { /* ... */ };
class BrushTool : public ITool { /* ... */ };
```


#### 7. Native Addon 接口 (N-API)

通过 Node.js Native Addon 将 C++ 功能暴露给 Electron。

```cpp
// native_addon.cpp
#include <napi.h>
#include "rendering_engine.h"
#include "document_manager.h"

// 包装 C++ 类为 Node.js 对象
class RenderingEngineWrapper : public Napi::ObjectWrap<RenderingEngineWrapper> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports);
    RenderingEngineWrapper(const Napi::CallbackInfo& info);
    
private:
    Napi::Value Render(const Napi::CallbackInfo& info);
    Napi::Value SetViewTransform(const Napi::CallbackInfo& info);
    Napi::Value ExportToBitmap(const Napi::CallbackInfo& info);
    
    std::unique_ptr<RenderingEngine> engine_;
};

// 导出模块
Napi::Object InitAll(Napi::Env env, Napi::Object exports) {
    RenderingEngineWrapper::Init(env, exports);
    DocumentManagerWrapper::Init(env, exports);
    return exports;
}

NODE_API_MODULE(drawing_native, InitAll)
```

**Electron 主进程集成：**

```typescript
// main.ts (Electron Main Process)
import { app, BrowserWindow, ipcMain } from 'electron';
import * as drawingNative from './native/drawing_native.node';

let mainWindow: BrowserWindow;
let renderingEngine: any;

app.whenReady().then(() => {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });
  
  // 初始化 C++ 渲染引擎
  renderingEngine = new drawingNative.RenderingEngine(1920, 1080);
  
  // 注册 IPC 处理器
  ipcMain.handle('render', async (event, shapes) => {
    const bitmap = renderingEngine.render(shapes);
    return bitmap;
  });
  
  ipcMain.handle('addShape', async (event, shape) => {
    // 调用 C++ 方法
    return renderingEngine.addShape(shape);
  });
});
```

### Vue.js 前端组件

#### 1. 主应用组件 (App.vue)

```vue
<template>
  <div class="app" :class="{ 'dark-theme': isDarkTheme }">
    <Toolbar @tool-change="handleToolChange" />
    <div class="main-content">
      <Canvas ref="canvasRef" />
      <PropertyPanel :selected-shape="selectedShape" />
    </div>
    <StatusBar :zoom="zoom" :position="cursorPosition" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useDrawingStore } from '@/stores/drawing';
import { ipcClient } from '@/services/ipc';

const drawingStore = useDrawingStore();
const canvasRef = ref<InstanceType<typeof Canvas>>();
const selectedShape = ref<Shape | null>(null);
const isDarkTheme = ref(false);
const zoom = ref(1.0);
const cursorPosition = ref({ x: 0, y: 0 });

onMounted(() => {
  ipcClient.connect();
});
</script>
```

#### 2. 工具栏组件 (Toolbar.vue)

```vue
<template>
  <div class="toolbar">
    <ToolButton
      v-for="tool in tools"
      :key="tool.id"
      :icon="tool.icon"
      :label="tool.label"
      :active="activeTool === tool.id"
      @click="selectTool(tool.id)"
    />
    <div class="separator"></div>
    <AlgorithmSelector
      v-if="showAlgorithmSelector"
      :algorithms="availableAlgorithms"
      :selected="selectedAlgorithm"
      @change="changeAlgorithm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useDrawingStore } from '@/stores/drawing';

const drawingStore = useDrawingStore();
const activeTool = computed(() => drawingStore.activeTool);
const selectedAlgorithm = computed(() => drawingStore.selectedAlgorithm);

const tools = [
  { id: 'select', icon: 'cursor', label: 'Select (V)' },
  { id: 'point', icon: 'dot', label: 'Point (P)' },
  { id: 'line', icon: 'line', label: 'Line (L)' },
  { id: 'rect', icon: 'square', label: 'Rectangle (R)' },
  { id: 'circle', icon: 'circle', label: 'Circle (C)' },
  { id: 'polygon', icon: 'polygon', label: 'Polygon (G)' },
  { id: 'brush', icon: 'brush', label: 'Brush (B)' },
];

const selectTool = (toolId: string) => {
  drawingStore.setActiveTool(toolId);
  ipcClient.call('setActiveTool', { tool: toolId });
};
</script>
```


#### 3. 画布组件 (Canvas.vue)

```vue
<template>
  <div class="canvas-container" ref="containerRef">
    <canvas
      ref="canvasRef"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @wheel="handleWheel"
    ></canvas>
    <div v-if="showGrid" class="grid-overlay"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { ipcClient } from '@/services/ipc';

const canvasRef = ref<HTMLCanvasElement>();
const containerRef = ref<HTMLDivElement>();
const showGrid = ref(true);

const handleMouseDown = (event: MouseEvent) => {
  const point = getCanvasPoint(event);
  ipcClient.notify('mouseDown', { x: point.x, y: point.y });
};

const handleMouseMove = (event: MouseEvent) => {
  const point = getCanvasPoint(event);
  ipcClient.notify('mouseMove', { x: point.x, y: point.y });
};

const handleMouseUp = (event: MouseEvent) => {
  const point = getCanvasPoint(event);
  ipcClient.notify('mouseUp', { x: point.x, y: point.y });
};

const handleWheel = (event: WheelEvent) => {
  event.preventDefault();
  const delta = event.deltaY > 0 ? -0.1 : 0.1;
  ipcClient.notify('zoom', { delta });
};

onMounted(() => {
  // 接收来自 C++ 的渲染数据
  ipcClient.on('render', (data: ArrayBuffer) => {
    renderFrame(data);
  });
});
</script>
```

#### 4. 属性面板组件 (PropertyPanel.vue)

```vue
<template>
  <div class="property-panel">
    <h3>Properties</h3>
    <div v-if="selectedShape">
      <ColorPicker
        label="Stroke Color"
        :value="selectedShape.strokeColor"
        @change="updateStrokeColor"
      />
      <Slider
        label="Stroke Width"
        :value="selectedShape.strokeWidth"
        :min="1"
        :max="100"
        @change="updateStrokeWidth"
      />
      <Select
        label="Stroke Style"
        :value="selectedShape.strokeStyle"
        :options="strokeStyles"
        @change="updateStrokeStyle"
      />
      <ColorPicker
        label="Fill Color"
        :value="selectedShape.fillColor"
        @change="updateFillColor"
      />
      <Slider
        label="Opacity"
        :value="selectedShape.opacity"
        :min="0"
        :max="100"
        @change="updateOpacity"
      />
    </div>
    <div v-else class="no-selection">
      No shape selected
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useDrawingStore } from '@/stores/drawing';
import { ipcClient } from '@/services/ipc';

const props = defineProps<{
  selectedShape: Shape | null;
}>();

const updateStrokeColor = (color: string) => {
  if (props.selectedShape) {
    ipcClient.call('updateShapeProperty', {
      shapeId: props.selectedShape.id,
      property: 'strokeColor',
      value: color,
    });
  }
};
</script>
```


## 数据模型

### 文档数据结构

```json
{
  "version": "1.0",
  "metadata": {
    "created": "2025-01-10T12:00:00Z",
    "modified": "2025-01-10T13:00:00Z",
    "author": "User Name",
    "application": "CrossPlatformDrawing"
  },
  "canvas": {
    "width": 1920,
    "height": 1080,
    "backgroundColor": "#FFFFFF"
  },
  "view": {
    "zoom": 1.0,
    "panX": 0,
    "panY": 0
  },
  "shapes": [
    {
      "id": "shape_001",
      "type": "line",
      "properties": {
        "x1": 100,
        "y1": 100,
        "x2": 300,
        "y2": 200,
        "strokeColor": "#FF0000",
        "strokeWidth": 2,
        "strokeStyle": "solid"
      },
      "algorithm": "bresenham",
      "zIndex": 0
    },
    {
      "id": "shape_002",
      "type": "circle",
      "properties": {
        "cx": 400,
        "cy": 300,
        "radius": 50,
        "strokeColor": "#00FF00",
        "strokeWidth": 3,
        "fillColor": "#FFFF00",
        "opacity": 0.8
      },
      "algorithm": "midpoint",
      "zIndex": 1
    },
    {
      "id": "shape_003",
      "type": "polygon",
      "properties": {
        "points": [
          {"x": 500, "y": 100},
          {"x": 600, "y": 150},
          {"x": 550, "y": 250},
          {"x": 450, "y": 200}
        ],
        "strokeColor": "#0000FF",
        "strokeWidth": 2,
        "fillColor": "#FF00FF",
        "fillAlgorithm": "scanline"
      },
      "zIndex": 2
    }
  ],
  "layers": [
    {
      "id": "layer_001",
      "name": "Background",
      "visible": true,
      "locked": false,
      "shapeIds": ["shape_001"]
    },
    {
      "id": "layer_002",
      "name": "Foreground",
      "visible": true,
      "locked": false,
      "shapeIds": ["shape_002", "shape_003"]
    }
  ]
}
```

### C++ 数据类型

```cpp
// 基本类型
struct Point {
    int x, y;
};

struct Color {
    uint8_t r, g, b, a;
    
    static Color fromHex(const std::string& hex);
    std::string toHex() const;
};

struct BoundingBox {
    int x, y, width, height;
    
    bool contains(const Point& point) const;
    bool intersects(const BoundingBox& other) const;
};

struct Matrix {
    float m[6]; // 2D affine transformation matrix
    
    Matrix translate(float dx, float dy) const;
    Matrix scale(float sx, float sy) const;
    Matrix rotate(float angle) const;
    Point transform(const Point& point) const;
};

// 枚举类型
enum class StrokeStyle {
    Solid,
    Dashed,
    Dotted
};

enum class RasterAlgorithm {
    Bresenham,
    DDA,
    Midpoint,
    Native  // 使用 Skia 原生 API
};

enum class FillAlgorithm {
    Scanline,
    FloodFill,
    Native
};

// 性能指标
struct PerformanceMetrics {
    std::string algorithmName;
    int64_t executionTimeNs;
    int pixelCount;
    double pixelsPerSecond;
};
```


## 光栅化算法实现

### 1. Bresenham 直线算法

```cpp
class BresenhamLineAlgorithm : public IRasterAlgorithm {
public:
    void drawLine(int x1, int y1, int x2, int y2, const Color& color) override {
        auto start = std::chrono::high_resolution_clock::now();
        
        int dx = std::abs(x2 - x1);
        int dy = std::abs(y2 - y1);
        int sx = (x1 < x2) ? 1 : -1;
        int sy = (y1 < y2) ? 1 : -1;
        int err = dx - dy;
        
        int pixelCount = 0;
        while (true) {
            setPixel(x1, y1, color);
            pixelCount++;
            
            if (x1 == x2 && y1 == y2) break;
            
            int e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                x1 += sx;
            }
            if (e2 < dx) {
                err += dx;
                y1 += sy;
            }
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        updateMetrics("Bresenham", start, end, pixelCount);
    }
    
private:
    void setPixel(int x, int y, const Color& color);
    void updateMetrics(const std::string& name, 
                      const TimePoint& start, 
                      const TimePoint& end, 
                      int pixelCount);
};
```

### 2. DDA 直线算法

```cpp
class DDALineAlgorithm : public IRasterAlgorithm {
public:
    void drawLine(int x1, int y1, int x2, int y2, const Color& color) override {
        auto start = std::chrono::high_resolution_clock::now();
        
        int dx = x2 - x1;
        int dy = y2 - y1;
        int steps = std::max(std::abs(dx), std::abs(dy));
        
        float xIncrement = static_cast<float>(dx) / steps;
        float yIncrement = static_cast<float>(dy) / steps;
        
        float x = x1;
        float y = y1;
        
        int pixelCount = 0;
        for (int i = 0; i <= steps; i++) {
            setPixel(std::round(x), std::round(y), color);
            pixelCount++;
            x += xIncrement;
            y += yIncrement;
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        updateMetrics("DDA", start, end, pixelCount);
    }
};
```

### 3. 中点画圆算法

```cpp
class MidpointCircleAlgorithm : public IRasterAlgorithm {
public:
    void drawCircle(int cx, int cy, int radius, const Color& color) override {
        auto start = std::chrono::high_resolution_clock::now();
        
        int x = 0;
        int y = radius;
        int d = 1 - radius;
        
        int pixelCount = 0;
        while (x <= y) {
            // 利用八对称性绘制 8 个点
            plotCirclePoints(cx, cy, x, y, color);
            pixelCount += 8;
            
            if (d < 0) {
                d += 2 * x + 3;
            } else {
                d += 2 * (x - y) + 5;
                y--;
            }
            x++;
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        updateMetrics("Midpoint Circle", start, end, pixelCount);
    }
    
private:
    void plotCirclePoints(int cx, int cy, int x, int y, const Color& color) {
        setPixel(cx + x, cy + y, color);
        setPixel(cx - x, cy + y, color);
        setPixel(cx + x, cy - y, color);
        setPixel(cx - x, cy - y, color);
        setPixel(cx + y, cy + x, color);
        setPixel(cx - y, cy + x, color);
        setPixel(cx + y, cy - x, color);
        setPixel(cx - y, cy - x, color);
    }
};
```


### 4. 扫描线填充算法

```cpp
class ScanlineFillAlgorithm : public IRasterAlgorithm {
public:
    void fillPolygon(const std::vector<Point>& points, const Color& color) override {
        auto start = std::chrono::high_resolution_clock::now();
        
        if (points.size() < 3) return;
        
        // 1. 构建边表 (Edge Table)
        std::map<int, std::vector<Edge>> edgeTable;
        buildEdgeTable(points, edgeTable);
        
        // 2. 初始化活性边表 (Active Edge Table)
        std::vector<Edge> activeEdgeTable;
        
        // 3. 扫描线填充
        int yMin = findMinY(points);
        int yMax = findMaxY(points);
        int pixelCount = 0;
        
        for (int y = yMin; y <= yMax; y++) {
            // 将新边加入 AET
            if (edgeTable.count(y)) {
                for (const auto& edge : edgeTable[y]) {
                    activeEdgeTable.push_back(edge);
                }
            }
            
            // 按 x 坐标排序
            std::sort(activeEdgeTable.begin(), activeEdgeTable.end(),
                     [](const Edge& a, const Edge& b) { return a.x < b.x; });
            
            // 填充像素（配对填充）
            for (size_t i = 0; i + 1 < activeEdgeTable.size(); i += 2) {
                int xStart = std::ceil(activeEdgeTable[i].x);
                int xEnd = std::floor(activeEdgeTable[i + 1].x);
                for (int x = xStart; x <= xEnd; x++) {
                    setPixel(x, y, color);
                    pixelCount++;
                }
            }
            
            // 更新 AET 中的边
            updateActiveEdges(activeEdgeTable, y);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        updateMetrics("Scanline Fill", start, end, pixelCount);
    }
    
private:
    struct Edge {
        float x;        // 当前扫描线与边的交点 x 坐标
        float dx;       // x 的增量 (1/斜率)
        int yMax;       // 边的最大 y 坐标
    };
    
    void buildEdgeTable(const std::vector<Point>& points,
                       std::map<int, std::vector<Edge>>& edgeTable);
    void updateActiveEdges(std::vector<Edge>& aet, int y);
    int findMinY(const std::vector<Point>& points);
    int findMaxY(const std::vector<Point>& points);
};
```

## 错误处理

### 异常处理策略

```cpp
// 自定义异常类
class DrawingException : public std::exception {
public:
    explicit DrawingException(const std::string& message) 
        : message_(message) {}
    
    const char* what() const noexcept override {
        return message_.c_str();
    }
    
private:
    std::string message_;
};

class FileIOException : public DrawingException {
    using DrawingException::DrawingException;
};

class RenderException : public DrawingException {
    using DrawingException::DrawingException;
};

// 错误处理包装器
template<typename Func>
auto safeExecute(Func&& func, const std::string& operation) {
    try {
        return func();
    } catch (const DrawingException& e) {
        logError(operation, e.what());
        notifyUI("error", {{"operation", operation}, {"message", e.what()}});
        throw;
    } catch (const std::exception& e) {
        logError(operation, e.what());
        notifyUI("error", {{"operation", operation}, {"message", "Unexpected error"}});
        throw DrawingException(std::string("Unexpected error: ") + e.what());
    }
}
```

### 自动保存机制

```cpp
class AutoSaveManager {
public:
    AutoSaveManager(DocumentManager* docManager, int intervalSeconds = 300)
        : docManager_(docManager), interval_(intervalSeconds) {
        startAutoSave();
    }
    
    ~AutoSaveManager() {
        stopAutoSave();
    }
    
private:
    void startAutoSave() {
        autoSaveThread_ = std::thread([this]() {
            while (running_) {
                std::this_thread::sleep_for(std::chrono::seconds(interval_));
                if (docManager_->isModified()) {
                    saveToTempFile();
                }
            }
        });
    }
    
    void saveToTempFile() {
        try {
            std::string tempPath = getTempFilePath();
            docManager_->saveDocument(tempPath);
            logInfo("Auto-saved to: " + tempPath);
        } catch (const FileIOException& e) {
            logError("Auto-save failed", e.what());
        }
    }
    
    DocumentManager* docManager_;
    int interval_;
    std::thread autoSaveThread_;
    std::atomic<bool> running_{true};
};
```


## 测试策略

### 单元测试

#### C++ 单元测试 (Google Test)

```cpp
// 测试光栅化算法
TEST(BresenhamAlgorithmTest, DrawsHorizontalLine) {
    MockPixelBuffer buffer(100, 100);
    BresenhamLineAlgorithm algorithm(&buffer);
    
    algorithm.drawLine(10, 50, 90, 50, Color{255, 0, 0, 255});
    
    // 验证像素
    for (int x = 10; x <= 90; x++) {
        EXPECT_EQ(buffer.getPixel(x, 50), Color{255, 0, 0, 255});
    }
}

TEST(BresenhamAlgorithmTest, DrawsVerticalLine) {
    MockPixelBuffer buffer(100, 100);
    BresenhamLineAlgorithm algorithm(&buffer);
    
    algorithm.drawLine(50, 10, 50, 90, Color{0, 255, 0, 255});
    
    for (int y = 10; y <= 90; y++) {
        EXPECT_EQ(buffer.getPixel(50, y), Color{0, 255, 0, 255});
    }
}

TEST(MidpointCircleTest, DrawsCircleCorrectly) {
    MockPixelBuffer buffer(200, 200);
    MidpointCircleAlgorithm algorithm(&buffer);
    
    algorithm.drawCircle(100, 100, 50, Color{0, 0, 255, 255});
    
    // 验证圆上的点
    EXPECT_EQ(buffer.getPixel(150, 100), Color{0, 0, 255, 255});
    EXPECT_EQ(buffer.getPixel(50, 100), Color{0, 0, 255, 255});
}

// 测试命令系统
TEST(CommandStackTest, UndoRedo) {
    CommandStack stack;
    int value = 0;
    
    auto cmd1 = std::make_unique<LambdaCommand>(
        [&]() { value += 10; },
        [&]() { value -= 10; }
    );
    
    stack.execute(std::move(cmd1));
    EXPECT_EQ(value, 10);
    
    stack.undo();
    EXPECT_EQ(value, 0);
    
    stack.redo();
    EXPECT_EQ(value, 10);
}

// 测试序列化
TEST(SerializationTest, ShapeToJson) {
    LineShape line;
    line.id = "line_001";
    line.x1 = 10;
    line.y1 = 20;
    line.x2 = 100;
    line.y2 = 200;
    line.strokeColor = Color{255, 0, 0, 255};
    
    nlohmann::json json = line.toJson();
    
    EXPECT_EQ(json["id"], "line_001");
    EXPECT_EQ(json["type"], "line");
    EXPECT_EQ(json["properties"]["x1"], 10);
}
```

#### Vue.js 单元测试 (Vitest)

```typescript
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import Toolbar from '@/components/Toolbar.vue';
import { createPinia } from 'pinia';

describe('Toolbar', () => {
  it('renders all tool buttons', () => {
    const wrapper = mount(Toolbar, {
      global: {
        plugins: [createPinia()],
      },
    });
    
    expect(wrapper.findAll('.tool-button')).toHaveLength(7);
  });
  
  it('emits tool-change event when tool is selected', async () => {
    const wrapper = mount(Toolbar, {
      global: {
        plugins: [createPinia()],
      },
    });
    
    await wrapper.find('[data-tool="line"]').trigger('click');
    
    expect(wrapper.emitted('tool-change')).toBeTruthy();
    expect(wrapper.emitted('tool-change')?.[0]).toEqual(['line']);
  });
  
  it('highlights active tool', async () => {
    const wrapper = mount(Toolbar, {
      global: {
        plugins: [createPinia()],
      },
    });
    
    const lineButton = wrapper.find('[data-tool="line"]');
    await lineButton.trigger('click');
    
    expect(lineButton.classes()).toContain('active');
  });
});
```

### 集成测试

```cpp
// C++ 集成测试
TEST(IntegrationTest, DrawAndSaveDocument) {
    DocumentManager docManager;
    RenderingEngine engine;
    
    // 创建图形
    auto line = std::make_unique<LineShape>();
    line->x1 = 10;
    line->y1 = 10;
    line->x2 = 100;
    line->y2 = 100;
    
    docManager.addShape(std::move(line));
    
    // 渲染
    engine.render(docManager.getAllShapes());
    
    // 保存
    std::string tempFile = "/tmp/test_document.json";
    EXPECT_TRUE(docManager.saveDocument(tempFile));
    
    // 加载
    DocumentManager loadedDoc;
    EXPECT_TRUE(loadedDoc.loadDocument(tempFile));
    EXPECT_EQ(loadedDoc.getAllShapes().size(), 1);
}
```

### 端到端测试

```typescript
// E2E 测试 (Playwright)
import { test, expect } from '@playwright/test';

test('draw a line and save', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // 选择直线工具
  await page.click('[data-tool="line"]');
  
  // 在画布上绘制
  const canvas = page.locator('canvas');
  await canvas.click({ position: { x: 100, y: 100 } });
  await canvas.click({ position: { x: 300, y: 300 } });
  
  // 保存文档
  await page.click('[data-action="save"]');
  
  // 验证保存对话框
  await expect(page.locator('.save-dialog')).toBeVisible();
});
```


## 性能优化

### 渲染优化

#### 1. 脏矩形更新

```cpp
class DirtyRectManager {
public:
    void markDirty(const BoundingBox& rect) {
        dirtyRegions_.push_back(rect);
    }
    
    void clearDirty() {
        dirtyRegions_.clear();
    }
    
    std::vector<BoundingBox> getDirtyRegions() const {
        // 合并重叠的脏矩形
        return mergeDirtyRegions(dirtyRegions_);
    }
    
private:
    std::vector<BoundingBox> dirtyRegions_;
    
    std::vector<BoundingBox> mergeDirtyRegions(
        const std::vector<BoundingBox>& regions) const;
};
```

#### 2. 空间索引 (R-tree)

```cpp
class SpatialIndex {
public:
    void insert(Shape* shape) {
        rtree_.insert(std::make_pair(shape->getBounds(), shape));
    }
    
    void remove(Shape* shape) {
        rtree_.remove(std::make_pair(shape->getBounds(), shape));
    }
    
    std::vector<Shape*> query(const BoundingBox& region) const {
        std::vector<std::pair<BoundingBox, Shape*>> results;
        rtree_.query(bgi::intersects(region), std::back_inserter(results));
        
        std::vector<Shape*> shapes;
        for (const auto& pair : results) {
            shapes.push_back(pair.second);
        }
        return shapes;
    }
    
private:
    using RTree = bgi::rtree<
        std::pair<BoundingBox, Shape*>,
        bgi::quadratic<16>
    >;
    RTree rtree_;
};
```

#### 3. 视口裁剪

```cpp
class ViewportCuller {
public:
    std::vector<Shape*> cullShapes(
        const std::vector<Shape*>& shapes,
        const BoundingBox& viewport) const {
        
        std::vector<Shape*> visibleShapes;
        for (Shape* shape : shapes) {
            if (viewport.intersects(shape->getBounds())) {
                visibleShapes.push_back(shape);
            }
        }
        return visibleShapes;
    }
};
```

#### 4. 对象池

```cpp
template<typename T>
class ObjectPool {
public:
    ObjectPool(size_t initialSize = 100) {
        for (size_t i = 0; i < initialSize; i++) {
            pool_.push_back(std::make_unique<T>());
        }
    }
    
    T* acquire() {
        if (pool_.empty()) {
            return new T();
        }
        T* obj = pool_.back().release();
        pool_.pop_back();
        return obj;
    }
    
    void release(T* obj) {
        pool_.push_back(std::unique_ptr<T>(obj));
    }
    
private:
    std::vector<std::unique_ptr<T>> pool_;
};
```

### 内存优化

```cpp
class MemoryManager {
public:
    static MemoryManager& instance() {
        static MemoryManager instance;
        return instance;
    }
    
    size_t getCurrentUsage() const {
        return currentUsage_.load();
    }
    
    void trackAllocation(size_t size) {
        currentUsage_ += size;
        if (currentUsage_ > maxUsage_) {
            logWarning("Memory usage high: " + std::to_string(currentUsage_));
        }
    }
    
    void trackDeallocation(size_t size) {
        currentUsage_ -= size;
    }
    
private:
    std::atomic<size_t> currentUsage_{0};
    size_t maxUsage_ = 500 * 1024 * 1024; // 500 MB
};
```

## 构建系统

### CMakeLists.txt 结构

```cmake
cmake_minimum_required(VERSION 3.20)
project(CrossPlatformDrawing VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 选项
option(BUILD_TESTS "Build tests" ON)
option(ENABLE_GPU_ACCELERATION "Enable GPU acceleration" ON)

# 查找依赖
find_package(Skia REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(Boost REQUIRED COMPONENTS geometry)

if(BUILD_TESTS)
    find_package(GTest REQUIRED)
    enable_testing()
endif()

# 平台特定设置
if(APPLE)
    find_library(WEBKIT_FRAMEWORK WebKit)
    set(PLATFORM_LIBS ${WEBKIT_FRAMEWORK})
elseif(UNIX)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(GTK3 REQUIRED gtk+-3.0)
    pkg_check_modules(WEBKIT2 REQUIRED webkit2gtk-4.0)
    set(PLATFORM_LIBS ${GTK3_LIBRARIES} ${WEBKIT2_LIBRARIES})
elseif(WIN32)
    set(PLATFORM_LIBS WebView2LoaderStatic)
endif()

# 源文件
add_subdirectory(src)
add_subdirectory(ui)

if(BUILD_TESTS)
    add_subdirectory(tests)
endif()

# 安装规则
install(TARGETS CrossPlatformDrawing
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

# 打包
include(CPack)
set(CPACK_PACKAGE_NAME "CrossPlatformDrawing")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_GENERATOR "DEB;RPM;NSIS;DragNDrop")
```

### 构建脚本

```bash
#!/bin/bash
# build.sh - 跨平台构建脚本

set -e

BUILD_TYPE=${1:-Release}
BUILD_DIR="build/${BUILD_TYPE}"

echo "Building CrossPlatformDrawing (${BUILD_TYPE})..."

# 1. 构建 C++ Native Addon
echo "Building C++ Native Addon..."
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}

cmake ../.. \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DBUILD_TESTS=ON \
    -DENABLE_GPU_ACCELERATION=ON

cmake --build . --config ${BUILD_TYPE} -j$(nproc)

# 运行 C++ 测试
if [ "${BUILD_TYPE}" = "Debug" ]; then
    ctest --output-on-failure
fi

cd ../..

# 2. 安装 Node.js 依赖
echo "Installing Node.js dependencies..."
npm install

# 3. 构建 Vue.js 前端
echo "Building Vue.js frontend..."
npm run build

# 4. 打包 Electron 应用
if [ "${BUILD_TYPE}" = "Release" ]; then
    echo "Packaging Electron app..."
    npm run package
fi

echo "Build complete!"
```

**package.json 配置：**

```json
{
  "name": "cross-platform-drawing",
  "version": "1.0.0",
  "main": "dist-electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build && electron-builder",
    "build:native": "./build.sh Release",
    "package": "electron-builder --publish never",
    "package:win": "electron-builder --win",
    "package:mac": "electron-builder --mac",
    "package:linux": "electron-builder --linux"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "electron": "^28.0.0",
    "electron-builder": "^24.9.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "node-gyp": "^10.0.0"
  },
  "build": {
    "appId": "com.example.drawing",
    "productName": "CrossPlatformDrawing",
    "directories": {
      "output": "release"
    },
    "files": [
      "dist/**/*",
      "dist-electron/**/*",
      "native/**/*.node"
    ],
    "mac": {
      "target": ["dmg", "zip"],
      "category": "public.app-category.graphics-design"
    },
    "win": {
      "target": ["nsis", "portable"]
    },
    "linux": {
      "target": ["AppImage", "deb", "rpm"],
      "category": "Graphics"
    }
  }
}
```


## 部署和打包

### Electron 打包

使用 electron-builder 进行跨平台打包，配置已在 package.json 中定义。

```bash
# 打包所有平台（需要在对应平台上执行）
npm run package

# 仅打包 Windows
npm run package:win

# 仅打包 macOS
npm run package:mac

# 仅打包 Linux
npm run package:linux
```

**输出文件：**
- **Linux**: `release/CrossPlatformDrawing-1.0.0.AppImage`, `.deb`, `.rpm`
- **macOS**: `release/CrossPlatformDrawing-1.0.0.dmg`, `.zip`
- **Windows**: `release/CrossPlatformDrawing Setup 1.0.0.exe`, portable版

**代码签名（可选）：**

```bash
# macOS
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=password
npm run package:mac

# Windows
export CSC_LINK=/path/to/certificate.pfx
export CSC_KEY_PASSWORD=password
npm run package:win
```

## 国际化实现

### C++ 国际化

```cpp
class I18nManager {
public:
    static I18nManager& instance() {
        static I18nManager instance;
        return instance;
    }
    
    void loadLanguage(const std::string& languageCode) {
        std::string path = "resources/i18n/" + languageCode + ".json";
        std::ifstream file(path);
        if (file.is_open()) {
            file >> translations_;
            currentLanguage_ = languageCode;
        }
    }
    
    std::string translate(const std::string& key) const {
        if (translations_.contains(key)) {
            return translations_[key];
        }
        return key; // 返回 key 作为后备
    }
    
    std::string getCurrentLanguage() const {
        return currentLanguage_;
    }
    
private:
    nlohmann::json translations_;
    std::string currentLanguage_ = "en";
};

// 使用宏简化翻译
#define TR(key) I18nManager::instance().translate(key)
```

### Vue.js 国际化

```typescript
// i18n.ts
import { createI18n } from 'vue-i18n';

const messages = {
  en: {
    toolbar: {
      select: 'Select',
      line: 'Line',
      rectangle: 'Rectangle',
      circle: 'Circle',
    },
    menu: {
      file: 'File',
      edit: 'Edit',
      view: 'View',
    },
  },
  zh: {
    toolbar: {
      select: '选择',
      line: '直线',
      rectangle: '矩形',
      circle: '圆形',
    },
    menu: {
      file: '文件',
      edit: '编辑',
      view: '视图',
    },
  },
};

export const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages,
});
```

## 安全考虑

### 文件系统安全

```cpp
class SecureFileManager {
public:
    bool isPathSafe(const std::string& path) const {
        // 检查路径遍历攻击
        if (path.find("..") != std::string::npos) {
            return false;
        }
        
        // 检查绝对路径
        std::filesystem::path p(path);
        if (p.is_absolute()) {
            // 确保在允许的目录内
            return isWithinAllowedDirectory(p);
        }
        
        return true;
    }
    
    bool saveDocument(const std::string& path, const nlohmann::json& data) {
        if (!isPathSafe(path)) {
            throw SecurityException("Unsafe file path");
        }
        
        // 使用临时文件 + 原子重命名
        std::string tempPath = path + ".tmp";
        std::ofstream file(tempPath);
        if (!file.is_open()) {
            return false;
        }
        
        file << data.dump(2);
        file.close();
        
        std::filesystem::rename(tempPath, path);
        return true;
    }
    
private:
    bool isWithinAllowedDirectory(const std::filesystem::path& path) const;
};
```

### 输入验证

```cpp
class InputValidator {
public:
    static bool validateColor(const std::string& color) {
        // 验证十六进制颜色格式
        std::regex hexPattern("^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$");
        return std::regex_match(color, hexPattern);
    }
    
    static bool validateCoordinate(int coord, int min, int max) {
        return coord >= min && coord <= max;
    }
    
    static bool validateStrokeWidth(float width) {
        return width >= 0.1f && width <= 100.0f;
    }
};
```

## 日志系统

```cpp
enum class LogLevel {
    Debug,
    Info,
    Warning,
    Error
};

class Logger {
public:
    static Logger& instance() {
        static Logger instance;
        return instance;
    }
    
    void log(LogLevel level, const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        
        std::ostringstream oss;
        oss << "[" << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S") << "] "
            << "[" << levelToString(level) << "] "
            << message << std::endl;
        
        std::cout << oss.str();
        
        if (logFile_.is_open()) {
            logFile_ << oss.str();
            logFile_.flush();
        }
    }
    
    void setLogFile(const std::string& path) {
        logFile_.open(path, std::ios::app);
    }
    
private:
    std::mutex mutex_;
    std::ofstream logFile_;
    
    std::string levelToString(LogLevel level) const {
        switch (level) {
            case LogLevel::Debug: return "DEBUG";
            case LogLevel::Info: return "INFO";
            case LogLevel::Warning: return "WARN";
            case LogLevel::Error: return "ERROR";
            default: return "UNKNOWN";
        }
    }
};

// 便捷宏
#define LOG_DEBUG(msg) Logger::instance().log(LogLevel::Debug, msg)
#define LOG_INFO(msg) Logger::instance().log(LogLevel::Info, msg)
#define LOG_WARN(msg) Logger::instance().log(LogLevel::Warning, msg)
#define LOG_ERROR(msg) Logger::instance().log(LogLevel::Error, msg)
```

## 总结

本设计文档详细描述了跨平台原生绘图系统的技术架构和实现方案。主要特点包括：

1. **高性能渲染**：使用 C++ 和 Skia 实现 GPU 加速渲染
2. **现代化界面**：采用 Vue 3 构建响应式用户界面
3. **跨平台支持**：通过 CMake 和统一代码库支持三大操作系统
4. **算法多样性**：实现多种光栅化算法，支持切换和对比
5. **完整功能**：满足作业一和作业二的所有要求
6. **可维护性**：模块化设计，清晰的架构分层
7. **可测试性**：完善的单元测试、集成测试和端到端测试
8. **性能优化**：脏矩形更新、空间索引、视口裁剪等优化技术
9. **安全可靠**：输入验证、错误处理、自动保存等机制

该设计为后续的实现提供了清晰的技术路线和详细的实现指导。


## Electron 架构优势

采用 Electron 框架相比原生 WebView 方案的优势：

### 1. 统一的跨平台体验
- **一致的 Chromium 内核**：避免不同平台 WebView 的差异和兼容性问题
- **统一的开发和调试体验**：所有平台使用相同的开发工具和调试方法
- **减少平台特定代码**：不需要为每个平台编写不同的 WebView 集成代码

### 2. 成熟的生态系统
- **electron-builder**：强大的打包工具，支持自动更新、代码签名等
- **丰富的插件**：大量现成的 Electron 插件可直接使用
- **活跃的社区**：遇到问题容易找到解决方案

### 3. 更好的开发体验
- **热重载**：开发时支持热重载，提高开发效率
- **DevTools**：内置 Chrome DevTools，调试方便
- **Node.js 集成**：可以直接使用 Node.js 生态的包

### 4. 简化的 IPC 机制
- **ipcMain/ipcRenderer**：Electron 提供的 IPC 机制简单易用
- **contextBridge**：安全地暴露 API 给渲染进程
- **不需要自己实现 JSON-RPC**：减少代码复杂度

### 5. 更容易的 Native Addon 集成
- **N-API**：Node.js 提供的稳定 C++ 绑定 API
- **node-gyp**：成熟的 Native Addon 构建工具
- **丰富的文档和示例**：容易找到参考资料

### 权衡考虑

**劣势：**
- 应用体积较大（~100-150MB，包含 Chromium）
- 内存占用相对较高
- 启动速度略慢于原生应用

**适用场景：**
- ✅ 学习项目和原型开发
- ✅ 需要快速跨平台开发
- ✅ 对应用体积不敏感
- ✅ 需要丰富的 UI 交互

**不适用场景：**
- ❌ 对体积和内存极度敏感的应用
- ❌ 需要极致性能的应用
- ❌ 嵌入式或资源受限环境

对于本项目（学习性质的绘图系统），Electron 是一个很好的选择，可以让我们专注于核心功能实现，而不是处理跨平台的细节问题。
