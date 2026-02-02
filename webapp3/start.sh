#!/bin/bash
# 启动 React 开发服务器

echo "=========================================="
echo "  绘图系统 Web 应用 (React + Vite)"
echo "=========================================="
echo ""
echo "正在启动开发服务器..."
echo ""

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "检测到缺少依赖，正在安装..."
    npm install
    echo ""
fi

# 启动 Vite 开发服务器
echo "开发服务器地址: http://localhost:5173"
echo "按 Ctrl+C 停止服务器"
echo ""

npm run dev
