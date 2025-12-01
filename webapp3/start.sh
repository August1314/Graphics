#!/bin/bash
# 启动本地开发服务器

echo "启动绘图系统 Web 应用..."
echo "在浏览器中访问: http://localhost:8000"
echo "按 Ctrl+C 停止服务器"
echo ""

# 检查 Python 是否可用
if command -v python3 &> /dev/null; then
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    python -m http.server 8000
else
    echo "错误: 未找到 Python"
    echo "请安装 Python 或使用其他方式打开 index.html"
    exit 1
fi
