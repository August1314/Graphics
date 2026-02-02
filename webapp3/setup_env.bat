@echo off
chcp 65001 > nul
setlocal

echo ==========================================
echo   绘图系统 Web 应用 - 环境设置
echo   Drawing System Web App - Setup
echo ==========================================
echo.

REM 检查 Node.js 是否安装
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js
    echo [Error] Node.js not found.
    echo.
    echo 请先安装 Node.js (版本 16 或更高)
    echo Please install Node.js (version 16 or higher)
    echo 下载地址: https://nodejs.org/
    echo Download: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM 检查 npm 是否可用
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 npm
    echo [Error] npm not found.
    echo.
    pause
    exit /b 1
)

REM 显示版本信息
echo [信息] 检测到 Node.js 和 npm
echo [Info] Node.js and npm detected
echo.
node --version
npm --version
echo.

REM 检查 package.json 是否存在
if not exist "package.json" (
    echo [错误] 未找到 package.json
    echo [Error] package.json not found.
    echo 请确保在项目根目录运行此脚本
    echo Please run this script in the project root directory
    echo.
    pause
    exit /b 1
)

echo [信息] 正在安装依赖...
echo [Info] Installing dependencies...
echo 这可能需要几分钟时间，请耐心等待...
echo This may take a few minutes, please wait...
echo.

REM 安装依赖
call npm install
if %errorlevel% neq 0 (
    echo.
    echo [错误] 依赖安装失败
    echo [Error] Failed to install dependencies
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   环境设置完成！
echo   Setup completed!
echo ==========================================
echo.
echo 现在可以运行 run_server.bat 启动开发服务器
echo You can now run run_server.bat to start the dev server
echo.
pause
