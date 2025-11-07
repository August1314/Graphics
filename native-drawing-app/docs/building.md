# 构建指南

本文档说明如何在不同平台上构建 Native Drawing App。

## 环境要求

### 所有平台

- **Node.js**: 18.0.0 或更高版本
- **npm**: 9.0.0 或更高版本
- **CMake**: 3.20 或更高版本
- **Git**: 用于克隆仓库

### Linux

- GCC 7+ 或 Clang 5+
- 开发工具：`build-essential`
- GTK 3 开发库（用于 Electron）

```bash
# Ubuntu/Debian
sudo apt-get install build-essential cmake git nodejs npm
sudo apt-get install libgtk-3-dev

# Fedora
sudo dnf install gcc-c++ cmake git nodejs npm
sudo dnf install gtk3-devel
```

### macOS

- Xcode 10+ 或 Xcode Command Line Tools
- Homebrew（推荐）

```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 使用 Homebrew 安装依赖
brew install cmake node
```

### Windows

- Visual Studio 2019 或更高版本（包含 C++ 工具）
- CMake
- Node.js

推荐使用 Visual Studio Installer 安装"使用 C++ 的桌面开发"工作负载。

## 依赖安装

### C++ 依赖

本项目使用 vcpkg 管理 C++ 依赖。

```bash
# 克隆 vcpkg（如果还没有）
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.sh  # Linux/macOS
# 或
./bootstrap-vcpkg.bat  # Windows

# 安装依赖
./vcpkg install nlohmann-json boost-geometry
```

### Node.js 依赖

```bash
cd native-drawing-app
npm install
```

## 构建步骤

### 使用构建脚本（推荐）

```bash
# Linux/macOS
chmod +x build.sh
./build.sh Release

# Windows
# 使用 Git Bash 或 WSL 运行 build.sh
# 或手动执行以下步骤
```

### 手动构建

#### 1. 构建 C++ 核心库

```bash
mkdir -p build/Release
cd build/Release
cmake ../.. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
cd ../..
```

#### 2. 构建 Native Addon

```bash
npm run build:native
```

#### 3. 构建 Vue.js 前端

```bash
npm run build:ui
```

#### 4. 构建 Electron 主进程

```bash
npm run build:electron
```

## 开发模式

开发模式支持热重载，方便快速迭代。

```bash
# 启动开发服务器
npm run dev
```

这将同时启动：
- Vite 开发服务器（Vue.js 前端）
- Electron 应用

## 打包

### 打包所有平台

```bash
npm run package
```

### 打包特定平台

```bash
# Linux
npm run package:linux

# macOS
npm run package:mac

# Windows
npm run package:win
```

打包后的文件将输出到 `release/` 目录。

## 测试

### 运行所有测试

```bash
npm test
```

### 运行特定测试

```bash
# C++ 单元测试
npm run test:cpp

# Vue.js 单元测试
npm run test:unit

# 端到端测试
npm run test:e2e
```

## 故障排除

### 常见问题

#### 1. node-gyp 构建失败

确保已安装 Python 3 和 C++ 编译器。

```bash
# 检查 Python 版本
python --version  # 应该是 3.x

# 重新安装 node-gyp
npm install -g node-gyp
```

#### 2. CMake 找不到依赖

确保 vcpkg 已正确安装依赖，并设置 CMAKE_TOOLCHAIN_FILE：

```bash
cmake ../.. -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake
```

#### 3. Electron 启动失败

清除缓存并重新安装：

```bash
rm -rf node_modules package-lock.json
npm install
```

## 下一步

- 阅读 [架构设计](./architecture.md) 了解系统架构
- 阅读 [API 文档](./api.md) 了解 API 接口
- 阅读 [贡献指南](./contributing.md) 了解如何贡献代码
