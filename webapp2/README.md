# 二维图形绘图系统 Web 版

一个功能完整的 Web 端二维图形绘图应用，支持多种图形绘制、撤销/重做、导出等功能。

## 📦 页面说明

### 🎨 draw.html - 简洁绘图工具（推荐）
**极简设计的专业绘图工具**
- 纯工具界面，无多余信息
- 单一顶部工具栏，所有功能一目了然
- 现代简洁的扁平化设计
- 完整的键盘快捷键支持
- 适合专注绘图的用户

### 🧪 test.html - 功能测试页面
**完整的功能测试和演示页面**
- 包含状态提示信息
- 详细的功能说明
- 适合开发测试和功能演示

### 🏠 index.html - 完整应用界面
**功能最全面的主应用**
- 侧边栏工具面板
- 主题切换功能
- 保存/加载 JSON 文件
- 完整的 UI 组件

## 功能特性

### 核心功能
- ✅ 多种图形绘制：点、线、矩形、圆形、多边形、画笔路径
- ✅ 选择和移动图形
- ✅ 实时修改图形属性（颜色、线宽、填充）
- ✅ 撤销/重做功能（支持 50 步历史记录）
- ✅ 无限网格辅助（可开关，自适应缩放）
- ✅ 画布缩放和平移
- ✅ 导出为 PNG 图片
- ✅ 保存/加载 JSON 格式
- ✅ 浅色/深色主题切换

### 绘图工具
1. **选择工具** - 选择和移动图形
2. **点工具** - 绘制点
3. **线工具** - 绘制直线
4. **矩形工具** - 绘制矩形
5. **圆形工具** - 绘制圆形
6. **多边形工具** - 绘制多边形（双击完成）
7. **画笔工具** - 自由绘制（支持平滑和简化）
8. **橡皮擦工具** - 擦除图形

### 技术特性
- 纯 HTML + CSS + JavaScript 实现
- 使用 Canvas API 进行高性能渲染
- 响应式设计，支持桌面和移动设备
- 模块化架构，易于扩展
- 完整的事件系统
- 性能优化（requestAnimationFrame、防抖节流）

## 快速开始
```bash
# 启动 Python HTTP 服务器
python -m http.server 8000

# 然后在浏览器中访问
# http://localhost:8000/draw.html    （简洁版）
```

## 使用说明

### 基本操作
1. **选择工具**：点击左侧工具栏的工具图标
2. **绘制图形**：
   - 点：点击画布
   - 线/矩形/圆形：按住鼠标拖动
   - 多边形：点击添加点，双击完成
   - 画笔：按住鼠标拖动绘制
3. **选择和移动**：使用选择工具点击图形，然后拖动
4. **撤销/重做**：点击画布下方的撤销/重做按钮
5. **清空画布**：点击清空按钮（会提示确认）
6. **导出**：
   - 导出 PNG：点击"导出 PNG"按钮
   - 保存 JSON：点击"保存 JSON"按钮

### 快捷键

**工具切换：**
- `1` - 选择工具
- `2` - 点工具
- `3` - 线工具
- `4` - 矩形工具
- `5` - 圆形工具
- `6` - 多边形工具
- `7` - 画笔工具
- `8` - 橡皮擦工具

**编辑操作：**
- `Ctrl+Z` / `Cmd+Z` - 撤销
- `Ctrl+Shift+Z` / `Cmd+Shift+Z` - 重做
- `Ctrl+Y` / `Cmd+Y` - 重做
- `Delete` / `Backspace` - 删除选中的图形
- `Esc` - 取消当前操作/取消选择

**视图控制：**
- `Ctrl+0` / `Cmd+0` - 重置缩放
- `Ctrl++` / `Cmd++` - 放大
- `Ctrl+-` / `Cmd+-` - 缩小
- `G` - 切换网格显示（仅 draw.html 和 test.html）

**文件操作：**
- `Ctrl+E` / `Cmd+E` - 导出 PNG

### 网格功能
- 按 `G` 键或点击"网格"复选框开启/关闭网格
- 网格会随缩放自动调整
- 包含主网格和子网格（每5个单位）
- 缩放过小时自动隐藏

### 主题切换
点击右上角的主题切换按钮（🌙/☀️）在浅色和深色主题之间切换。（仅 index.html）

## 项目结构

```
webapp/
├── draw.html              # 简洁绘图工具（推荐）
├── index.html             # 完整应用界面
├── test.html              # 功能测试页面
├── assets/                # 静态资源
│   ├── images/            # 图片资源
│   └── data/              # 数据文件
├── styles/                # 样式文件
│   ├── theme.css          # 主题变量
│   ├── layout.css         # 布局样式
│   ├── components.css     # 组件样式
│   └── animations.css     # 动画定义
└── scripts/               # JavaScript 文件
    ├── main.js            # 主入口
    ├── config.js          # 配置文件
    ├── core/              # 核心模块
    │   ├── canvas.js      # Canvas 管理（含网格功能）
    │   ├── document.js    # 文档管理
    │   ├── serializer.js  # 序列化器
    │   └── history.js     # 历史记录
    ├── shapes/            # 图形类
    │   ├── base.js        # 基础图形类
    │   ├── point.js       # 点
    │   ├── line.js        # 线
    │   ├── rect.js        # 矩形
    │   ├── circle.js      # 圆形
    │   ├── polygon.js     # 多边形
    │   └── path.js        # 画笔路径
    ├── tools/             # 工具类
    │   ├── base.js        # 基础工具类
    │   ├── select.js      # 选择工具
    │   ├── point.js       # 点工具
    │   ├── line.js        # 线工具
    │   ├── rect.js        # 矩形工具
    │   ├── circle.js      # 圆形工具
    │   ├── polygon.js     # 多边形工具
    │   ├── brush.js       # 画笔工具
    │   └── eraser.js      # 橡皮擦工具
    ├── ui/                # UI 模块
    │   └── theme.js       # 主题管理
    └── utils/             # 工具函数
        ├── color.js       # 颜色处理
        ├── geometry.js    # 几何计算
        └── export.js      # 导出功能
```

## 数据格式

### JSON 格式
保存的 JSON 文件格式与 Python 桌面版本兼容：

```json
{
  "version": "2.0",
  "canvas": {
    "width": 800,
    "height": 600
  },
  "metadata": {
    "created": "2025-01-10T12:00:00Z",
    "modified": "2025-01-10T13:00:00Z"
  },
  "shapes": [
    {
      "id": "shape_1",
      "type": "circle",
      "properties": {
        "cx": 100,
        "cy": 100,
        "r": 50,
        "strokeColor": "#0066cc",
        "strokeWidth": 2,
        "fillColor": "#ffffff",
        "opacity": 1.0
      },
      "timestamp": 1704888000000
    }
  ]
}
```

## 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 开发

### 配置
编辑 `scripts/config.js` 文件可以修改默认配置：
- Canvas 尺寸
- 工具默认样式
- 历史记录大小
- 性能参数

### 扩展
添加新工具：
1. 在 `scripts/tools/` 创建新工具类，继承 `BaseTool`
2. 实现 `onMouseDown`, `onMouseMove`, `onMouseUp` 方法
3. 在 `scripts/main.js` 中注册工具

添加新图形：
1. 在 `scripts/shapes/` 创建新图形类，继承 `BaseShape`
2. 实现 `render`, `getBounds`, `toDict`, `fromDict` 方法
3. 在 `scripts/core/serializer.js` 中注册图形类型

## 性能优化

- 使用 `requestAnimationFrame` 进行流畅渲染
- 事件防抖和节流
- 历史记录限制（默认 50 步）
- Canvas 设备像素比适配
- 路径简化算法（道格拉斯-普克）

## 许可证

MIT License

## 作者

绘图系统开发团队

## 版本历史

- v2.1.0 (2025-01-11) - 功能增强
  - 新增 draw.html 简洁绘图工具页面
  - 新增无限网格功能（自适应缩放）
  - 新增画布缩放和平移功能
  - 新增实时修改选中图形属性
  - 完善键盘快捷键系统
  - 优化用户界面和交互体验

- v2.0.0 (2025-01-10) - Web 版本发布
  - 完整的绘图功能
  - 主题系统
  - 响应式设计
  - 与 Python 版本数据格式兼容
