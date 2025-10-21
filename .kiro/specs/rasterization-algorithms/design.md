# 设计文档 - 光栅化算法实现

## 概述

本设计文档描述了如何在现有的二维图形绘图系统（webapp2）中实现光栅化算法。系统将支持多种光栅化算法（Bresenham、DDA、中点画圆等），并提供直观的算法选择界面。设计采用模块化架构，确保算法实现与现有系统无缝集成。

## 架构

### 整体架构

```
webapp2/
├── scripts/
│   ├── algorithms/              # 新增：光栅化算法模块
│   │   ├── base.js             # 算法基类
│   │   ├── line/               # 直线算法
│   │   │   ├── bresenham.js
│   │   │   ├── dda.js
│   │   │   └── midpoint.js
│   │   ├── circle/             # 圆形算法
│   │   │   └── midpoint.js
│   │   ├── fill/               # 填充算法
│   │   │   ├── scanline.js
│   │   │   └── boundary.js
│   │   └── renderer.js         # 像素渲染器
│   ├── shapes/                 # 修改：扩展图形类
│   │   ├── line.js            # 支持算法选择
│   │   └── circle.js          # 支持算法选择
│   ├── tools/                  # 修改：扩展工具类
│   │   ├── line.js            # 集成算法选择
│   │   └── circle.js          # 集成算法选择
│   └── ui/
│       └── algorithm-selector.js  # 新增：算法选择器 UI
```

### 模块关系

```
┌─────────────────┐
│   UI Layer      │
│ (工具栏/选择器)  │
└────────┬────────┘
         │
┌────────▼────────┐
│   Tools Layer   │
│  (绘图工具)      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Shapes Layer   │
│   (图形类)       │
└────────┬────────┘
         │
┌────────▼────────┐
│ Algorithms Layer│
│  (光栅化算法)    │
└────────┬────────┘
         │
┌────────▼────────┐
│ Renderer Layer  │
│  (像素渲染)      │
└─────────────────┘
```

## 组件和接口

### 1. 算法基类 (BaseAlgorithm)

所有光栅化算法的抽象基类，定义统一接口。

```javascript
class BaseAlgorithm {
    constructor(name, description) {
        this.name = name;
        this.description = description;
        this.stats = { pixelCount: 0, executionTime: 0 };
    }
    
    // 抽象方法：执行算法
    execute(params, renderer) {
        throw new Error('execute() must be implemented');
    }
    
    // 重置统计信息
    resetStats() {
        this.stats = { pixelCount: 0, executionTime: 0 };
    }
    
    // 获取统计信息
    getStats() {
        return { ...this.stats };
    }
}
```

### 2. 像素渲染器 (PixelRenderer)

负责像素级操作，提供统一的像素绘制接口。

```javascript
class PixelRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.imageData = null;
        this.width = 0;
        this.height = 0;
    }
    
    // 开始批量像素操作
    beginPixelMode() {
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.imageData = this.ctx.getImageData(0, 0, this.width, this.height);
    }
    
    // 设置单个像素
    setPixel(x, y, r, g, b, a = 255) {
        if (x < 0 || x >= this.width || y < 0 || y >= this.height) return;
        const index = (Math.floor(y) * this.width + Math.floor(x)) * 4;
        this.imageData.data[index] = r;
        this.imageData.data[index + 1] = g;
        this.imageData.data[index + 2] = b;
        this.imageData.data[index + 3] = a;
    }
    
    // 获取像素颜色
    getPixel(x, y) {
        if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
            return { r: 0, g: 0, b: 0, a: 0 };
        }
        const index = (Math.floor(y) * this.width + Math.floor(x)) * 4;
        return {
            r: this.imageData.data[index],
            g: this.imageData.data[index + 1],
            b: this.imageData.data[index + 2],
            a: this.imageData.data[index + 3]
        };
    }
    
    // 结束批量像素操作并更新画布
    endPixelMode() {
        this.ctx.putImageData(this.imageData, 0, 0);
        this.imageData = null;
    }
}
```

### 3. 直线算法实现

#### Bresenham 算法

```javascript
class BresenhamLineAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Bresenham', 'Bresenham 直线算法（整数运算）');
    }
    
    execute({ x1, y1, x2, y2, color }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const { r, g, b, a } = this.parseColor(color);
        
        let dx = Math.abs(x2 - x1);
        let dy = Math.abs(y2 - y1);
        let sx = x1 < x2 ? 1 : -1;
        let sy = y1 < y2 ? 1 : -1;
        let err = dx - dy;
        
        let x = Math.round(x1);
        let y = Math.round(y1);
        const endX = Math.round(x2);
        const endY = Math.round(y2);
        
        while (true) {
            renderer.setPixel(x, y, r, g, b, a);
            pixelCount++;
            
            if (x === endX && y === endY) break;
            
            const e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                x += sx;
            }
            if (e2 < dx) {
                err += dx;
                y += sy;
            }
        }
        
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    parseColor(color) {
        // 解析颜色字符串为 RGBA
        const hex = color.replace('#', '');
        return {
            r: parseInt(hex.substr(0, 2), 16),
            g: parseInt(hex.substr(2, 2), 16),
            b: parseInt(hex.substr(4, 2), 16),
            a: 255
        };
    }
}
```

#### DDA 算法

```javascript
class DDALineAlgorithm extends BaseAlgorithm {
    constructor() {
        super('DDA', 'DDA 直线算法（增量计算）');
    }
    
    execute({ x1, y1, x2, y2, color }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const { r, g, b, a } = this.parseColor(color);
        
        const dx = x2 - x1;
        const dy = y2 - y1;
        const steps = Math.max(Math.abs(dx), Math.abs(dy));
        
        const xIncrement = dx / steps;
        const yIncrement = dy / steps;
        
        let x = x1;
        let y = y1;
        
        for (let i = 0; i <= steps; i++) {
            renderer.setPixel(Math.round(x), Math.round(y), r, g, b, a);
            pixelCount++;
            x += xIncrement;
            y += yIncrement;
        }
        
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    parseColor(color) {
        const hex = color.replace('#', '');
        return {
            r: parseInt(hex.substr(0, 2), 16),
            g: parseInt(hex.substr(2, 2), 16),
            b: parseInt(hex.substr(4, 2), 16),
            a: 255
        };
    }
}
```

### 4. 圆形算法实现

#### 中点画圆算法

```javascript
class MidpointCircleAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Midpoint Circle', '中点画圆算法（八对称性）');
    }
    
    execute({ cx, cy, radius, color, fill }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const { r, g, b, a } = this.parseColor(color);
        
        if (fill) {
            // 填充圆形：使用扫描线填充
            pixelCount = this.fillCircle(cx, cy, radius, r, g, b, a, renderer);
        } else {
            // 绘制圆形轮廓
            pixelCount = this.drawCircleOutline(cx, cy, radius, r, g, b, a, renderer);
        }
        
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    drawCircleOutline(cx, cy, radius, r, g, b, a, renderer) {
        let pixelCount = 0;
        let x = 0;
        let y = Math.round(radius);
        let d = 1 - radius;
        
        // 绘制八对称点
        const plot8Points = (cx, cy, x, y) => {
            renderer.setPixel(cx + x, cy + y, r, g, b, a);
            renderer.setPixel(cx - x, cy + y, r, g, b, a);
            renderer.setPixel(cx + x, cy - y, r, g, b, a);
            renderer.setPixel(cx - x, cy - y, r, g, b, a);
            renderer.setPixel(cx + y, cy + x, r, g, b, a);
            renderer.setPixel(cx - y, cy + x, r, g, b, a);
            renderer.setPixel(cx + y, cy - x, r, g, b, a);
            renderer.setPixel(cx - y, cy - x, r, g, b, a);
            return 8;
        };
        
        pixelCount += plot8Points(cx, cy, x, y);
        
        while (x < y) {
            if (d < 0) {
                d += 2 * x + 3;
            } else {
                d += 2 * (x - y) + 5;
                y--;
            }
            x++;
            pixelCount += plot8Points(cx, cy, x, y);
        }
        
        return pixelCount;
    }
    
    fillCircle(cx, cy, radius, r, g, b, a, renderer) {
        let pixelCount = 0;
        const radiusSq = radius * radius;
        
        for (let y = -radius; y <= radius; y++) {
            const width = Math.floor(Math.sqrt(radiusSq - y * y));
            for (let x = -width; x <= width; x++) {
                renderer.setPixel(cx + x, cy + y, r, g, b, a);
                pixelCount++;
            }
        }
        
        return pixelCount;
    }
    
    parseColor(color) {
        const hex = color.replace('#', '');
        return {
            r: parseInt(hex.substr(0, 2), 16),
            g: parseInt(hex.substr(2, 2), 16),
            b: parseInt(hex.substr(4, 2), 16),
            a: 255
        };
    }
}
```

### 5. 填充算法实现

#### 扫描线填充算法

```javascript
class ScanlineFillAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Scanline Fill', '扫描线填充算法');
    }
    
    execute({ vertices, color }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const { r, g, b, a } = this.parseColor(color);
        
        // 构建边表
        const edges = this.buildEdgeTable(vertices);
        if (edges.length === 0) return;
        
        // 获取 Y 范围
        const minY = Math.min(...vertices.map(v => v.y));
        const maxY = Math.max(...vertices.map(v => v.y));
        
        // 扫描线填充
        for (let y = Math.ceil(minY); y <= Math.floor(maxY); y++) {
            const intersections = this.getIntersections(edges, y);
            intersections.sort((a, b) => a - b);
            
            // 填充交点对之间的像素
            for (let i = 0; i < intersections.length; i += 2) {
                if (i + 1 < intersections.length) {
                    const x1 = Math.ceil(intersections[i]);
                    const x2 = Math.floor(intersections[i + 1]);
                    for (let x = x1; x <= x2; x++) {
                        renderer.setPixel(x, y, r, g, b, a);
                        pixelCount++;
                    }
                }
            }
        }
        
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    buildEdgeTable(vertices) {
        const edges = [];
        const n = vertices.length;
        
        for (let i = 0; i < n; i++) {
            const v1 = vertices[i];
            const v2 = vertices[(i + 1) % n];
            
            // 跳过水平边
            if (v1.y === v2.y) continue;
            
            edges.push({
                yMin: Math.min(v1.y, v2.y),
                yMax: Math.max(v1.y, v2.y),
                x: v1.y < v2.y ? v1.x : v2.x,
                slope: (v2.x - v1.x) / (v2.y - v1.y)
            });
        }
        
        return edges;
    }
    
    getIntersections(edges, y) {
        const intersections = [];
        
        for (const edge of edges) {
            if (y >= edge.yMin && y < edge.yMax) {
                const x = edge.x + (y - edge.yMin) * edge.slope;
                intersections.push(x);
            }
        }
        
        return intersections;
    }
    
    parseColor(color) {
        const hex = color.replace('#', '');
        return {
            r: parseInt(hex.substr(0, 2), 16),
            g: parseInt(hex.substr(2, 2), 16),
            b: parseInt(hex.substr(4, 2), 16),
            a: 255
        };
    }
}
```

#### 边界填充算法

```javascript
class BoundaryFillAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Boundary Fill', '边界填充算法（基于栈）');
    }
    
    execute({ seedX, seedY, fillColor, boundaryColor }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const fill = this.parseColor(fillColor);
        const boundary = this.parseColor(boundaryColor);
        
        const stack = [{ x: Math.round(seedX), y: Math.round(seedY) }];
        const visited = new Set();
        const maxIterations = 100000; // 防止无限循环
        let iterations = 0;
        
        while (stack.length > 0 && iterations < maxIterations) {
            iterations++;
            const { x, y } = stack.pop();
            const key = `${x},${y}`;
            
            if (visited.has(key)) continue;
            visited.add(key);
            
            const pixel = renderer.getPixel(x, y);
            
            // 检查是否为边界或已填充
            if (this.colorsEqual(pixel, boundary) || this.colorsEqual(pixel, fill)) {
                continue;
            }
            
            // 填充当前像素
            renderer.setPixel(x, y, fill.r, fill.g, fill.b, fill.a);
            pixelCount++;
            
            // 添加四个方向的邻居
            stack.push({ x: x + 1, y });
            stack.push({ x: x - 1, y });
            stack.push({ x, y: y + 1 });
            stack.push({ x, y: y - 1 });
        }
        
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    colorsEqual(c1, c2) {
        return c1.r === c2.r && c1.g === c2.g && c1.b === c2.b && c1.a === c2.a;
    }
    
    parseColor(color) {
        const hex = color.replace('#', '');
        return {
            r: parseInt(hex.substr(0, 2), 16),
            g: parseInt(hex.substr(2, 2), 16),
            b: parseInt(hex.substr(4, 2), 16),
            a: 255
        };
    }
}
```

### 6. 算法选择器 UI

提供直观的算法选择界面，类似专业图形软件。

```javascript
class AlgorithmSelector {
    constructor() {
        this.algorithms = {
            line: [
                { id: 'bresenham', name: 'Bresenham', description: '整数运算，高效' },
                { id: 'dda', name: 'DDA', description: '增量计算' },
                { id: 'midpoint', name: '中点画线', description: '中点判别' },
                { id: 'canvas', name: 'Canvas API', description: '原生绘制' }
            ],
            circle: [
                { id: 'midpoint', name: '中点画圆', description: '八对称性' },
                { id: 'canvas', name: 'Canvas API', description: '原生绘制' }
            ],
            fill: [
                { id: 'scanline', name: '扫描线填充', description: '多边形填充' },
                { id: 'boundary', name: '边界填充', description: '种子填充' },
                { id: 'canvas', name: 'Canvas API', description: '原生填充' }
            ]
        };
        
        this.currentSelections = {
            line: 'bresenham',
            circle: 'midpoint',
            fill: 'scanline'
        };
        
        this.loadPreferences();
    }
    
    // 创建下拉选择器
    createSelector(toolType, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const select = document.createElement('select');
        select.className = 'algorithm-selector';
        select.id = `algorithm-${toolType}`;
        
        const algorithms = this.algorithms[toolType] || [];
        algorithms.forEach(algo => {
            const option = document.createElement('option');
            option.value = algo.id;
            option.textContent = `${algo.name} - ${algo.description}`;
            if (algo.id === this.currentSelections[toolType]) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        
        select.addEventListener('change', (e) => {
            this.setAlgorithm(toolType, e.target.value);
        });
        
        container.appendChild(select);
    }
    
    // 设置算法
    setAlgorithm(toolType, algorithmId) {
        this.currentSelections[toolType] = algorithmId;
        this.savePreferences();
        this.emit('algorithmChanged', { toolType, algorithmId });
    }
    
    // 获取当前算法
    getAlgorithm(toolType) {
        return this.currentSelections[toolType];
    }
    
    // 保存用户偏好
    savePreferences() {
        localStorage.setItem('algorithmPreferences', JSON.stringify(this.currentSelections));
    }
    
    // 加载用户偏好
    loadPreferences() {
        const saved = localStorage.getItem('algorithmPreferences');
        if (saved) {
            this.currentSelections = { ...this.currentSelections, ...JSON.parse(saved) };
        }
    }
}
```

### 7. 扩展图形类

修改现有的 Line 和 Circle 类，支持算法选择。

```javascript
// Line 类扩展
class Line extends BaseShape {
    constructor(x1, y1, x2, y2, properties = {}) {
        super(properties.id, 'line', properties);
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
        this.algorithm = properties.algorithm || 'bresenham';
        this.useRasterization = properties.useRasterization !== false;
    }
    
    render(ctx) {
        if (this.useRasterization && this.algorithm !== 'canvas') {
            this.renderWithAlgorithm(ctx);
        } else {
            this.renderWithCanvas(ctx);
        }
        this.renderSelection(ctx);
    }
    
    renderWithAlgorithm(ctx) {
        const renderer = new PixelRenderer(ctx.canvas);
        renderer.beginPixelMode();
        
        const algorithm = AlgorithmFactory.createLineAlgorithm(this.algorithm);
        algorithm.execute({
            x1: this.x1,
            y1: this.y1,
            x2: this.x2,
            y2: this.y2,
            color: this.properties.strokeColor
        }, renderer);
        
        renderer.endPixelMode();
        
        // 可选：显示统计信息
        if (window.DEBUG_MODE) {
            console.log(`${algorithm.name}:`, algorithm.getStats());
        }
    }
    
    renderWithCanvas(ctx) {
        ctx.save();
        this.applyStyle(ctx);
        ctx.beginPath();
        ctx.moveTo(this.x1, this.y1);
        ctx.lineTo(this.x2, this.y2);
        ctx.stroke();
        ctx.restore();
    }
    
    setAlgorithm(algorithm) {
        this.algorithm = algorithm;
    }
}

// Circle 类扩展
class Circle extends BaseShape {
    constructor(cx, cy, radius, properties = {}) {
        super(properties.id, 'circle', properties);
        this.cx = cx;
        this.cy = cy;
        this.radius = radius;
        this.algorithm = properties.algorithm || 'midpoint';
        this.useRasterization = properties.useRasterization !== false;
    }
    
    render(ctx) {
        if (this.useRasterization && this.algorithm !== 'canvas') {
            this.renderWithAlgorithm(ctx);
        } else {
            this.renderWithCanvas(ctx);
        }
        this.renderSelection(ctx);
    }
    
    renderWithAlgorithm(ctx) {
        const renderer = new PixelRenderer(ctx.canvas);
        renderer.beginPixelMode();
        
        const algorithm = AlgorithmFactory.createCircleAlgorithm(this.algorithm);
        
        // 绘制轮廓
        algorithm.execute({
            cx: this.cx,
            cy: this.cy,
            radius: this.radius,
            color: this.properties.strokeColor,
            fill: false
        }, renderer);
        
        // 填充
        if (this.properties.fillColor !== 'transparent') {
            algorithm.execute({
                cx: this.cx,
                cy: this.cy,
                radius: this.radius,
                color: this.properties.fillColor,
                fill: true
            }, renderer);
        }
        
        renderer.endPixelMode();
    }
    
    renderWithCanvas(ctx) {
        ctx.save();
        this.applyStyle(ctx);
        ctx.beginPath();
        ctx.arc(this.cx, this.cy, this.radius, 0, Math.PI * 2);
        if (this.properties.fillColor !== 'transparent') {
            ctx.fill();
        }
        ctx.stroke();
        ctx.restore();
    }
    
    setAlgorithm(algorithm) {
        this.algorithm = algorithm;
    }
}
```

### 8. 算法工厂

提供统一的算法实例创建接口。

```javascript
class AlgorithmFactory {
    static lineAlgorithms = {
        'bresenham': () => new BresenhamLineAlgorithm(),
        'dda': () => new DDALineAlgorithm(),
        'midpoint': () => new MidpointLineAlgorithm()
    };
    
    static circleAlgorithms = {
        'midpoint': () => new MidpointCircleAlgorithm()
    };
    
    static fillAlgorithms = {
        'scanline': () => new ScanlineFillAlgorithm(),
        'boundary': () => new BoundaryFillAlgorithm()
    };
    
    static createLineAlgorithm(type) {
        const factory = this.lineAlgorithms[type];
        if (!factory) {
            throw new Error(`Unknown line algorithm: ${type}`);
        }
        return factory();
    }
    
    static createCircleAlgorithm(type) {
        const factory = this.circleAlgorithms[type];
        if (!factory) {
            throw new Error(`Unknown circle algorithm: ${type}`);
        }
        return factory();
    }
    
    static createFillAlgorithm(type) {
        const factory = this.fillAlgorithms[type];
        if (!factory) {
            throw new Error(`Unknown fill algorithm: ${type}`);
        }
        return factory();
    }
}
```

## 数据模型

### 算法配置

```javascript
{
    toolType: 'line' | 'circle' | 'fill',
    algorithmId: string,
    enabled: boolean,
    debugMode: boolean
}
```

### 图形属性扩展

```javascript
{
    // 现有属性
    strokeColor: string,
    strokeWidth: number,
    fillColor: string,
    opacity: number,
    
    // 新增属性
    algorithm: string,           // 使用的算法 ID
    useRasterization: boolean,   // 是否使用光栅化算法
    algorithmStats: {            // 算法统计信息（可选）
        pixelCount: number,
        executionTime: number
    }
}
```

### 性能统计

```javascript
{
    algorithmName: string,
    pixelCount: number,
    executionTime: number,      // 毫秒
    timestamp: number
}
```

## 错误处理

### 1. 参数验证

```javascript
class ParameterValidator {
    static validateLineParams(x1, y1, x2, y2) {
        if (!Number.isFinite(x1) || !Number.isFinite(y1) || 
            !Number.isFinite(x2) || !Number.isFinite(y2)) {
            throw new Error('Invalid line coordinates');
        }
    }
    
    static validateCircleParams(cx, cy, radius) {
        if (!Number.isFinite(cx) || !Number.isFinite(cy)) {
            throw new Error('Invalid circle center');
        }
        if (!Number.isFinite(radius) || radius < 0) {
            throw new Error('Invalid circle radius');
        }
    }
    
    static validateColor(color) {
        const hexRegex = /^#[0-9A-Fa-f]{6}$/;
        if (!hexRegex.test(color)) {
            throw new Error('Invalid color format');
        }
    }
}
```

### 2. 边界检查

- 所有像素操作前检查坐标是否在画布范围内
- 防止数组越界访问
- 处理退化情况（零长度直线、零半径圆形）

### 3. 性能保护

```javascript
class PerformanceGuard {
    static MAX_PIXELS = 1000000;  // 最大像素数
    static MAX_ITERATIONS = 100000;  // 最大迭代次数
    
    static checkPixelCount(count) {
        if (count > this.MAX_PIXELS) {
            throw new Error('Pixel count exceeds limit');
        }
    }
    
    static checkIterations(iterations) {
        if (iterations > this.MAX_ITERATIONS) {
            throw new Error('Iteration count exceeds limit');
        }
    }
}
```

### 4. 回退机制

当光栅化算法失败时，自动回退到 Canvas API：

```javascript
render(ctx) {
    try {
        if (this.useRasterization && this.algorithm !== 'canvas') {
            this.renderWithAlgorithm(ctx);
        } else {
            this.renderWithCanvas(ctx);
        }
    } catch (error) {
        console.error('Rasterization failed, falling back to Canvas API:', error);
        this.renderWithCanvas(ctx);
    }
    this.renderSelection(ctx);
}
```

## 测试策略

### 1. 单元测试

测试每个算法的正确性：

```javascript
describe('BresenhamLineAlgorithm', () => {
    test('should draw horizontal line', () => {
        const algorithm = new BresenhamLineAlgorithm();
        const renderer = new MockRenderer();
        algorithm.execute({ x1: 0, y1: 0, x2: 10, y2: 0, color: '#000000' }, renderer);
        expect(renderer.pixels.length).toBe(11);
    });
    
    test('should draw vertical line', () => {
        const algorithm = new BresenhamLineAlgorithm();
        const renderer = new MockRenderer();
        algorithm.execute({ x1: 0, y1: 0, x2: 0, y2: 10, color: '#000000' }, renderer);
        expect(renderer.pixels.length).toBe(11);
    });
    
    test('should draw diagonal line', () => {
        const algorithm = new BresenhamLineAlgorithm();
        const renderer = new MockRenderer();
        algorithm.execute({ x1: 0, y1: 0, x2: 10, y2: 10, color: '#000000' }, renderer);
        expect(renderer.pixels.length).toBeGreaterThan(10);
    });
});
```

### 2. 集成测试

测试算法与图形类的集成：

```javascript
describe('Line with Bresenham', () => {
    test('should render using Bresenham algorithm', () => {
        const line = new Line(0, 0, 100, 100, { algorithm: 'bresenham' });
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        expect(() => line.render(ctx)).not.toThrow();
    });
});
```

### 3. 视觉测试

对比不同算法的绘制结果：

- 绘制相同的图形使用不同算法
- 对比像素差异
- 验证视觉一致性

### 4. 性能测试

测试算法性能：

```javascript
describe('Algorithm Performance', () => {
    test('Bresenham should be faster than DDA for long lines', () => {
        const bresenham = new BresenhamLineAlgorithm();
        const dda = new DDALineAlgorithm();
        const renderer = new MockRenderer();
        
        const params = { x1: 0, y1: 0, x2: 1000, y2: 1000, color: '#000000' };
        
        bresenham.execute(params, renderer);
        const bresenhamTime = bresenham.getStats().executionTime;
        
        dda.execute(params, renderer);
        const ddaTime = dda.getStats().executionTime;
        
        expect(bresenhamTime).toBeLessThan(ddaTime * 1.5);
    });
});
```

## UI/UX 设计

### 1. 工具栏布局

```
┌─────────────────────────────────────────────────────────────┐
│ [工具] [算法选择] [样式] [操作] [视图] [调试]                │
├─────────────────────────────────────────────────────────────┤
│ 👆 ⚫ 📏 ▭ ⭕ ⬡ 🖌️ 🧹                                        │
│                                                             │
│ 当前工具: 直线                                               │
│ 算法: [Bresenham ▼] [Canvas API] [DDA] [中点画线]           │
│                                                             │
│ 描边: [■] 2px  填充: [■] 透明                               │
│                                                             │
│ [调试模式: ☐] [显示统计: ☐]                                 │
└─────────────────────────────────────────────────────────────┘
```

### 2. 算法选择器样式

```css
.algorithm-selector {
    display: flex;
    gap: 8px;
    padding: 8px;
    background: #f5f5f5;
    border-radius: 6px;
}

.algorithm-option {
    padding: 6px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.algorithm-option:hover {
    background: #e0e0e0;
}

.algorithm-option.active {
    background: #2196F3;
    color: white;
    border-color: #2196F3;
}

.algorithm-info {
    font-size: 11px;
    color: #666;
    margin-top: 2px;
}
```

### 3. 调试面板

当启用调试模式时，显示性能统计：

```
┌─────────────────────────┐
│ 算法性能统计             │
├─────────────────────────┤
│ 算法: Bresenham         │
│ 像素数: 142             │
│ 执行时间: 0.8ms         │
│ 效率: 177,500 px/s      │
└─────────────────────────┘
```

### 4. 算法对比模式

分屏显示不同算法的绘制结果：

```
┌──────────────┬──────────────┐
│  Bresenham   │     DDA      │
│              │              │
│   [图形]     │   [图形]     │
│              │              │
│ 142 像素     │ 145 像素     │
│ 0.8ms        │ 1.2ms        │
└──────────────┴──────────────┘
```

## 性能优化

### 1. 批量像素操作

使用 ImageData 批量更新像素，避免频繁调用 Canvas API：

```javascript
// 不推荐：每个像素单独更新
for (let i = 0; i < pixels.length; i++) {
    ctx.fillRect(pixels[i].x, pixels[i].y, 1, 1);
}

// 推荐：批量更新
renderer.beginPixelMode();
for (let i = 0; i < pixels.length; i++) {
    renderer.setPixel(pixels[i].x, pixels[i].y, r, g, b, a);
}
renderer.endPixelMode();
```

### 2. 整数运算

所有算法使用整数运算，避免浮点数计算：

```javascript
// 不推荐
let x = x1 + (x2 - x1) * t;

// 推荐
let x = Math.round(x1 + (x2 - x1) * t);
```

### 3. 增量计算

使用增量计算减少重复运算：

```javascript
// Bresenham 算法使用增量
let err = dx - dy;
while (true) {
    // ...
    const e2 = 2 * err;  // 只计算一次
    if (e2 > -dy) {
        err -= dy;
        x += sx;
    }
    if (e2 < dx) {
        err += dx;
        y += sy;
    }
}
```

### 4. 对称性优化

利用图形对称性减少计算量：

```javascript
// 圆形的八对称性
const plot8Points = (cx, cy, x, y) => {
    renderer.setPixel(cx + x, cy + y, r, g, b, a);
    renderer.setPixel(cx - x, cy + y, r, g, b, a);
    renderer.setPixel(cx + x, cy - y, r, g, b, a);
    renderer.setPixel(cx - x, cy - y, r, g, b, a);
    renderer.setPixel(cx + y, cy + x, r, g, b, a);
    renderer.setPixel(cx - y, cy + x, r, g, b, a);
    renderer.setPixel(cx + y, cy - x, r, g, b, a);
    renderer.setPixel(cx - y, cy - x, r, g, b, a);
};
```

### 5. 内存优化

- 重用 ImageData 对象
- 避免不必要的数组分配
- 使用 Set 代替数组进行查找操作

## 兼容性考虑

### 浏览器兼容性

- Canvas API: 所有现代浏览器支持
- ImageData: 所有现代浏览器支持
- localStorage: 所有现代浏览器支持

### 降级策略

对于不支持的浏览器，自动使用 Canvas API：

```javascript
if (!ctx.getImageData) {
    console.warn('ImageData not supported, using Canvas API');
    this.useRasterization = false;
}
```

## 安全性

### 1. 输入验证

所有用户输入必须验证：

- 坐标范围检查
- 颜色格式验证
- 参数类型检查

### 2. 资源限制

防止恶意输入导致的资源耗尽：

- 限制最大像素数
- 限制最大迭代次数
- 超时保护

### 3. 错误隔离

算法错误不应影响整个应用：

- try-catch 包裹算法执行
- 错误日志记录
- 自动回退机制

## 可扩展性

### 添加新算法

1. 创建新的算法类继承 BaseAlgorithm
2. 实现 execute 方法
3. 在 AlgorithmFactory 中注册
4. 在 AlgorithmSelector 中添加选项

```javascript
// 1. 创建新算法
class NewLineAlgorithm extends BaseAlgorithm {
    constructor() {
        super('New Algorithm', 'Description');
    }
    
    execute(params, renderer) {
        // 实现算法逻辑
    }
}

// 2. 注册算法
AlgorithmFactory.lineAlgorithms['new'] = () => new NewLineAlgorithm();

// 3. 添加 UI 选项
algorithms.line.push({
    id: 'new',
    name: 'New Algorithm',
    description: 'Description'
});
```

### 支持新图形类型

1. 创建新的图形类
2. 实现光栅化渲染方法
3. 创建对应的算法实现
4. 添加工具类支持

## 文档和注释

### 代码注释规范

```javascript
/**
 * Bresenham 直线算法实现
 * 
 * 使用整数运算绘制直线，避免浮点数计算。
 * 算法复杂度: O(max(dx, dy))
 * 
 * @param {Object} params - 参数对象
 * @param {number} params.x1 - 起点 X 坐标
 * @param {number} params.y1 - 起点 Y 坐标
 * @param {number} params.x2 - 终点 X 坐标
 * @param {number} params.y2 - 终点 Y 坐标
 * @param {string} params.color - 颜色（十六进制格式）
 * @param {PixelRenderer} renderer - 像素渲染器
 * 
 * @throws {Error} 如果参数无效
 * 
 * @example
 * const algorithm = new BresenhamLineAlgorithm();
 * algorithm.execute({ x1: 0, y1: 0, x2: 100, y2: 100, color: '#000000' }, renderer);
 */
```

### 用户文档

提供详细的用户指南：

- 算法选择说明
- 性能对比
- 使用建议
- 常见问题解答

## 总结

本设计文档详细描述了光栅化算法在绘图系统中的实现方案。通过模块化设计、统一接口、性能优化和完善的错误处理，确保系统能够高效、稳定地运行。算法选择器提供了直观的用户界面，使用户能够轻松切换不同的算法并对比效果。
