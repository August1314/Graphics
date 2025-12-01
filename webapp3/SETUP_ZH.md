# webapp2 环境配置与运行指南

本指南将帮助您在 Windows 环境下使用 Conda 配置和运行 webapp2 项目。

## 前置要求

- **Miniconda** 或 **Anaconda** 已安装。
  - 您刚刚已经安装了 Miniconda (`C:\ProgramData\miniconda3`)。
  - **注意**: 如果您刚刚安装完，可能需要**重启终端**（关闭当前 PowerShell 窗口并重新打开）才能让 `conda` 命令生效。

## 快速开始

我们为您准备了自动化脚本，只需双击即可完成大部分操作。

### 1. 创建环境

双击运行项目目录下的 **`setup_env.bat`**。

该脚本会：
1. 检查 `conda` 命令是否可用。
2. 根据 `environment.yml` 创建名为 `webapp2` 的 Python 环境。
3. 安装所需的 Python 版本（3.10）。

### 2. 启动服务器

双击运行项目目录下的 **`run_server.bat`**。

该脚本会：
1. 激活 `webapp2` 环境。
2. 启动本地 HTTP 服务器。
3. 提示您访问 `http://localhost:8000`。

## 手动操作

如果您更喜欢使用命令行，可以按照以下步骤操作：

1.  **打开终端** (PowerShell 或 CMD)。
2.  **进入项目目录**:
    ```powershell
    cd c:\Users\18706\Desktop\Graphics\webapp2
    ```
3.  **创建环境**:
    ```powershell
    conda env create -f environment.yml
    ```
4.  **激活环境**:
    ```powershell
    conda activate webapp2
    ```
5.  **启动服务器**:
    ```powershell
    python -m http.server 8000
    ```

## 常见问题

**Q: 提示 "conda 不是内部或外部命令"？**
A: 这通常是因为 Conda 没有添加到系统环境变量 PATH 中。
- 请尝试重启您的终端。
- 或者，您可以手动将 `C:\ProgramData\miniconda3\Scripts` 添加到环境变量。
- 我们的 `setup_env.bat` 脚本尝试了自动处理此问题，如果仍然失败，请尝试手动添加。

**Q: 端口 8000 被占用？**
A: 编辑 `run_server.bat` 或在命令行中指定其他端口，例如：
```powershell
python -m http.server 8080
```
