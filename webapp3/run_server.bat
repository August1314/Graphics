@echo off
chcp 65001 > nul
setlocal

REM 检查 Conda 是否在 PATH 中
where conda >nul 2>nul
if %errorlevel% neq 0 (
    REM 尝试添加默认安装路径
    if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" (
        set "PATH=%PATH%;C:\ProgramData\miniconda3\Scripts;C:\ProgramData\miniconda3"
    ) else (
        echo Error: Conda not found.
        echo 错误: 未找到 Conda。
        pause
        exit /b 1
    )
)

echo Starting webapp2 server...
echo 正在启动 webapp2 服务器...

REM 激活环境
call conda activate webapp2
if %errorlevel% neq 0 (
    echo Failed to activate environment 'webapp2'.
    echo 无法激活环境 'webapp2'。
    echo Please run setup_env.bat first.
    echo 请先运行 setup_env.bat。
    pause
    exit /b 1
)

echo.
echo Server is running at: http://localhost:8000
echo 服务器运行于: http://localhost:8000
echo Press Ctrl+C to stop.
echo 按 Ctrl+C 停止。
echo.

python -m http.server 8000
pause
