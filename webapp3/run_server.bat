@echo off
chcp 65001 > nul
setlocal

echo ==========================================
echo   绘图系统 Web 应用 (React + Vite)
echo   Drawing System Web App (React + Vite)
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

REM 检查 node_modules 是否存在，如果不存在则安装依赖
if not exist "node_modules" (
    echo [信息] 检测到缺少依赖，正在安装...
    echo [Info] Dependencies missing, installing...
    echo 这可能需要几分钟时间，请耐心等待...
    echo This may take a few minutes, please wait...
    echo.
    call npm install
    if %errorlevel% neq 0 (
        echo.
        echo [错误] 依赖安装失败
        echo [Error] Failed to install dependencies
        echo 请运行 setup_env.bat 手动安装依赖
        echo Please run setup_env.bat to install dependencies manually
        echo.
        pause
        exit /b 1
    )
    echo.
)

echo [信息] 正在启动开发服务器...
echo [Info] Starting development server...
echo.
echo ==========================================
echo   开发服务器地址: http://localhost:5173
echo   Dev Server URL: http://localhost:5173
echo ==========================================
echo.
echo 按 Ctrl+C 停止服务器
echo Press Ctrl+C to stop the server
echo.

REM 启动 Vite 开发服务器
call npm run dev

REM 如果服务器意外退出，暂停以便查看错误信息
if %errorlevel% neq 0 (
    echo.
    echo [错误] 服务器启动失败
    echo [Error] Failed to start server
    echo.
    pause
    exit /b 1
)
