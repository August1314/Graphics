@echo off
chcp 65001 > nul
setlocal

echo Creating Conda environment 'webapp2'...
echo 正在创建 Conda 环境 'webapp2'...

REM 检查 Conda 是否在 PATH 中
where conda >nul 2>nul
if %errorlevel% neq 0 (
    REM 尝试添加默认安装路径
    if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" (
        set "PATH=%PATH%;C:\ProgramData\miniconda3\Scripts;C:\ProgramData\miniconda3"
        echo Added Miniconda to PATH temporarily.
        echo 已临时添加 Miniconda 到 PATH。
    ) else (
        echo Error: Conda not found.
        echo 错误: 未找到 Conda。
        pause
        exit /b 1
    )
)

call conda env create -f environment.yml
if %errorlevel% neq 0 (
    echo.
    echo Environment creation failed (it might already exist).
    echo 环境创建失败（可能已存在）。
    echo Trying to update instead...
    echo 尝试更新环境...
    call conda env update -f environment.yml
)

echo.
echo Done!
echo 完成！
pause
