# 二维图形绘图系统 Web 版 (React)

一个功能完整的 Web 端二维图形绘图应用，使用 React + TypeScript + Vite 构建，支持多种图形绘制、撤销/重做、导出等功能。  

## 🚀 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite 5
- **核心绘图**: Canvas API + 自定义绘图引擎
- **样式**: CSS3 (毛玻璃效果、动画)

## 功能特性

### 核心功能
- ✅ 多种图形绘制：点、线、矩形、圆形、多边形、画笔路径、Bézier/B 样条曲线、Bézier 曲面
- ✅ 智能选择工具：优先满足拖动等基本操作，点击控制点或双击图形自动切换到对应工具进行编辑
- ✅ 实时修改图形属性（颜色、线宽、填充）
- ✅ 撤销/重做功能（支持 50 步历史记录）
- ✅ 无限网格辅助（可开关，自适应缩放）
- ✅ 画布缩放和平移
- ✅ 导出为 PNG 图片
- ✅ 保存/加载 JSON 格式
- ✅ 浅色/深色主题切换
- ✅ 交互式引导教程，帮助用户快速上手

### 绘图工具
1. **选择工具** - 选择、移动、变换图形；点击控制点或双击图形自动切换到对应工具进行编辑
2. **点工具** - 绘制点
3. **线工具** - 绘制直线
4. **矩形工具** - 绘制矩形
5. **圆形工具** - 绘制圆形
6. **多边形工具** - 绘制多边形（双击完成）
7. **画笔工具** - 自由绘制（支持平滑和简化）
8. **Bézier 曲线工具** - 手动添加控制点，支持拖拽编辑
9. **B 样条曲线工具** - 均匀 B 样条，绘制过程中实时显示控制点，支持控制点拖拽与阶数配置
10. **Bézier 曲面工具** - 拖拽生成 4×4 控制网格，精确点击检测（仅点击控制点或网格线附近才选中），可双击切换"网格/填充"模式
11. **橡皮擦工具** - 擦除图形

### 技术特性
- React + TypeScript 现代化架构
- 使用 Canvas API 进行高性能渲染
- 响应式设计，支持桌面和移动设备
- 组件化架构，易于维护和扩展
- 完整的事件系统和状态管理
- 性能优化（requestAnimationFrame、防抖节流）
- 引导教程功能，帮助用户快速上手

## 快速开始

### 安装依赖

**Linux/macOS:**
```bash
npm install
```

**Windows:**
```cmd
# 方式一：使用批处理文件（推荐）
setup_env.bat

# 方式二：使用 npm 命令
npm install
```

### 启动开发服务器

**Linux/macOS:**
```bash
# 方式一：使用启动脚本（推荐）
chmod +x start.sh
./start.sh

# 方式二：使用 npm 命令
npm run dev
# 或
npm start
```

**Windows:**
```cmd
# 方式一：使用批处理文件（推荐）
run_server.bat

# 方式二：使用 npm 命令
npm run dev
# 或
npm start
```

开发服务器将在 `http://localhost:5173` 启动。

### 构建生产版本
```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 预览生产构建
```bash
npm run preview
```

## 使用说明

### 基本操作
1. **选择工具**：点击顶部工具栏的工具图标
2. **绘制图形**：
   - 点：点击画布
   - 线/矩形/圆形：按住鼠标拖动
   - 多边形：点击添加点，双击完成
   - 画笔：按住鼠标拖动绘制
   - B 样条曲线：点击添加控制点，绘制过程中实时显示控制点和连接线，双击完成
3. **选择和移动**：
   - 使用选择工具点击图形，然后拖动移动图形
   - 选择工具优先满足拖动等基本操作，不会自动切换工具
4. **编辑图形**：
   - **点击控制点**：在选择工具下点击曲线/曲面的控制点，自动切换到对应工具并开始编辑
   - **双击图形**：双击支持编辑的图形（Bézier曲线、B样条曲线、曲面），自动切换到对应工具进入编辑模式
   - **拖动控制点**：切换到对应工具后，可以直接拖动控制点调整形状
5. **修改样式**：选中图形后，可以调整颜色、线宽等属性（无需切换工具）
6. **撤销/重做**：点击工具栏的撤销/重做按钮
7. **清空画布**：点击清空按钮（会提示确认）
8. **导出**：点击"导出"按钮导出 PNG 图片
9. **引导教程**：点击右下角"教程"按钮查看使用说明

### 快捷键

**工具切换：**
- `1` - 选择工具
- `2` - 点工具
- `3` - 线工具
- `4` - 矩形工具
- `5` - 圆形工具
- `6` - 多边形工具
- `7` - 画笔工具
- `8` - 填充工具
- `9` - 橡皮擦工具
- `B` / `b` - Bézier 曲线
- `S` / `s` - B 样条曲线
- `M` / `m` - Bézier 曲面

**编辑操作：**
- `Ctrl+Z` / `Cmd+Z` - 撤销
- `Ctrl+Shift+Z` / `Cmd+Shift+Z` - 重做
- `Ctrl+Y` / `Cmd+Y` - 重做
- `Delete` / `Backspace` - 删除选中的图形
- `Esc` - 取消当前操作/取消选择
- `R` / `r` - 对选中图形顺/逆时针旋转 10°
- `[` / `]` - 对选中图形整体缩放 0.9 / 1.1 倍

**视图控制：**
- `Ctrl+0` / `Cmd+0` - 重置缩放
- `Ctrl++` / `Cmd++` - 放大
- `Ctrl+-` / `Cmd+-` - 缩小

**文件操作：**
- `Ctrl+E` / `Cmd+E` - 导出 PNG

### 网格与曲线/曲面提示
- 点击工具栏"网格"复选框开启/关闭网格
- 曲线/曲面在选中时会高亮控制网格
- **编辑曲线/曲面**：
  - 在选择工具下，点击控制点会自动切换到对应工具并开始编辑
  - 双击曲线/曲面图形也会自动切换到对应工具进入编辑模式
  - 切换后可以直接拖动控制点调整形状
- Bézier 曲面双击可在"网格线"与"曲面填充"两种渲染模式之间切换
- Bézier 曲面使用精确点击检测，只有点击控制点或网格线附近才会被选中，避免误选

## 项目结构

```
webapp3/
├── index.html             # Vite 入口文件
├── package.json           # 项目配置和依赖
├── vite.config.mts        # Vite 配置
├── tsconfig.json          # TypeScript 配置
├── start.sh               # 启动脚本
├── src/                   # React 源码
│   ├── main.tsx           # React 入口
│   ├── App.tsx            # 根组件
│   ├── pages/             # 页面组件
│   │   └── DrawPage.tsx   # 绘图页面
│   ├── components/        # UI 组件
│   │   ├── Toolbar/       # 工具栏组件
│   │   ├── CanvasPane/    # 画布组件
│   │   └── TourGuide/     # 引导教程组件
│   ├── hooks/             # React Hooks
│   │   └── useLegacyDrawingCore.ts  # 绘图核心集成
│   └── styles/            # 样式文件
│       └── global.css     # 全局样式
├── scripts/               # 核心绘图逻辑（纯 JS）
│   ├── config.js          # 配置文件
│   ├── core/              # 核心模块
│   │   ├── canvas.js      # Canvas 管理
│   │   ├── document.js    # 文档管理
│   │   ├── serializer.js  # 序列化器
│   │   └── history.js     # 历史记录
│   ├── shapes/            # 图形类
│   │   ├── base.js        # 基础图形类
│   │   ├── point.js       # 点
│   │   ├── line.js        # 线
│   │   ├── rect.js        # 矩形
│   │   ├── circle.js      # 圆形
│   │   ├── polygon.js     # 多边形
│   │   ├── path.js        # 画笔路径
│   │   ├── bezier_curve.js    # Bézier 曲线
│   │   ├── bspline_curve.js   # B 样条曲线
│   │   └── bezier_surface.js  # Bézier 曲面
│   ├── tools/             # 工具类
│   │   ├── base.js        # 基础工具类
│   │   ├── select.js      # 选择工具
│   │   ├── point.js       # 点工具
│   │   ├── line.js        # 线工具
│   │   ├── rect.js        # 矩形工具
│   │   ├── circle.js      # 圆形工具
│   │   ├── polygon.js     # 多边形工具
│   │   ├── brush.js       # 画笔工具
│   │   ├── eraser.js      # 橡皮擦工具
│   │   ├── fill.js        # 填充工具
│   │   ├── bezier_curve.js    # Bézier 曲线工具
│   │   ├── bspline_curve.js   # B 样条曲线工具
│   │   └── bezier_surface.js  # Bézier 曲面工具
│   ├── algorithms/        # 算法实现
│   │   ├── line/          # 直线算法
│   │   ├── circle/        # 圆形算法
│   │   ├── fill/          # 填充算法
│   │   ├── curve/         # 曲线算法
│   │   └── surface/       # 曲面算法
│   └── utils/             # 工具函数
│       ├── color.js       # 颜色处理
│       ├── geometry.js    # 几何计算
│       └── export.js      # 导出功能
└── assets/                # 静态资源
    ├── images/            # 图片资源
    └── data/              # 数据文件
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
3. 在 `src/hooks/useLegacyDrawingCore.ts` 中注册工具

添加新图形：
1. 在 `scripts/shapes/` 创建新图形类，继承 `BaseShape`
2. 实现 `render`, `getBounds`, `toDict`, `fromDict` 方法
3. 在 `scripts/core/serializer.js` 中注册图形类型

添加新 React 组件：
1. 在 `src/components/` 创建新组件
2. 在 `src/pages/DrawPage.tsx` 中引入和使用

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

- v2.2.0 (2025-01-XX) - 交互优化与功能增强
  - 智能选择工具：优先满足拖动等基本操作，点击控制点或双击图形自动切换到对应工具
  - B 样条曲线优化：绘制过程中实时显示控制点，修复直线显示问题
  - 曲面点击检测优化：精确检测，只有点击控制点或网格线附近才选中
  - 工具栏两行布局：优化空间利用，支持响应式设计
  - 修复 B 样条曲线渲染问题（边界框计算、无效点过滤）
  - 交互式引导教程：新增步骤式教程，帮助用户快速上手

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
