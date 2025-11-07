# 跨平台原生绘图系统

一个高性能、跨平台的二维图形绘图应用，采用 C++ 渲染引擎和 Vue.js 现代化界面。

## 特性

- 🎨 **多种图形绘制**：点、线、矩形、圆、椭圆、多边形、自由画笔
- ⚡ **高性能渲染**：C++ + Skia 图形库 + GPU 加速
- 🔄 **光栅化算法**：Bresenham、DDA、中点画圆、扫描线填充等多种算法
- 🖥️ **跨平台支持**：Linux、macOS、Windows
- 🎯 **现代化界面**：Vue 3 + TypeScript + Element Plus
- 📦 **Electron 集成**：统一的跨平台应用框架
- ↩️ **撤销/重做**：支持 100 步历史记录
- 💾 **文件管理**：JSON 格式保存/加载，兼容现有系统
- 🖼️ **多格式导出**：PNG、JPEG、SVG
- 🌐 **国际化**：中文/英文界面

## 技术栈

### 后端（C++）
- C++17
- Skia 图形库
- CMake 构建系统
- vcpkg 依赖管理
- Google Test 单元测试

### 前端（Vue.js）
- Vue 3 (Composition API)
- TypeScript
- Vite 构建工具
- Pinia 状态管理
- Element Plus UI 库
- Vitest 单元测试

### 集成
- Electron 应用框架
- N-API (Node.js Native Addon)
- electron-builder 打包工具

## 项目结构

```
native-drawing-app/
├── src/                    # C++ 源代码
│   ├── core/              # 核心模块
│   │   ├── shapes/        # 图形类
│   │   ├── algorithms/    # 光栅化算法
│   │   ├── rendering/     # 渲染引擎
│   │   ├── document/      # 文档管理
│   │   ├── commands/      # 命令系统
│   │   └── tools/         # 工具系统
│   ├── utils/             # 工具函数
│   └── native/            # Native Addon 绑定
├── ui/                     # Vue.js 前端
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── services/      # 服务层（IPC 通信）
│   │   └── assets/        # 静态资源
│   └── public/            # 公共资源
├── electron/               # Electron 主进程
│   ├── main.ts            # 主进程入口
│   └── preload.ts         # Preload 脚本
├── tests/                  # 测试
│   ├── cpp/               # C++ 单元测试
│   ├── unit/              # Vue 单元测试
│   └── e2e/               # 端到端测试
├── docs/                   # 文档
├── resources/              # 应用资源（图标等）
├── CMakeLists.txt          # CMake 配置
├── package.json            # npm 配置
├── binding.gyp             # Native Addon 构建配置
└── README.md               # 本文件
```

## 快速开始

### 环境要求

- **C++ 编译器**：支持 C++17 的编译器
  - Linux: GCC 7+ 或 Clang 5+
  - macOS: Xcode 10+
  - Windows: Visual Studio 2019+
- **CMake**: 3.20+
- **Node.js**: 18+
- **npm** 或 **yarn**
- **vcpkg**: C++ 依赖管理（可选）

### 安装依赖

```bash
# 安装 C++ 依赖（使用 vcpkg）
vcpkg install skia nlohmann-json boost-geometry

# 安装 Node.js 依赖
npm install
```

### 构建

```bash
# 构建 C++ Native Addon
npm run build:native

# 构建 Vue.js 前端
npm run build:ui

# 开发模式
npm run dev
```

### 运行

```bash
# 启动应用
npm start
```

### 打包

```bash
# 打包所有平台
npm run package

# 打包特定平台
npm run package:linux
npm run package:mac
npm run package:win
```

## 开发指南

详细的开发文档请参阅 [docs/](./docs/) 目录：

- [架构设计](./docs/architecture.md)
- [构建指南](./docs/building.md)
- [API 文档](./docs/api.md)
- [贡献指南](./docs/contributing.md)

## 光栅化算法

本项目实现了多种经典的光栅化算法：

- **Bresenham 直线算法**：高效的整数运算直线绘制
- **DDA 直线算法**：基于增量计算的直线绘制
- **中点画线算法**：基于中点判别的直线绘制
- **中点画圆算法**：利用八对称性的圆形绘制
- **椭圆光栅化算法**：椭圆的精确绘制
- **扫描线填充算法**：多边形的高效填充

所有算法都支持性能对比和实时切换。

## 许可证

MIT License

## 作者

梁力航
