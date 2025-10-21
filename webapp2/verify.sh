#!/bin/bash

# 项目完整性验证脚本

echo "🔍 验证 Web UI 迁移项目..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
total=0
passed=0
failed=0

# 检查函数
check_file() {
    total=$((total + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        passed=$((passed + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $1 ${RED}(缺失)${NC}"
        failed=$((failed + 1))
        return 1
    fi
}

check_dir() {
    total=$((total + 1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        passed=$((passed + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $1/ ${RED}(缺失)${NC}"
        failed=$((failed + 1))
        return 1
    fi
}

echo "📁 检查目录结构..."
check_dir "assets"
check_dir "assets/data"
check_dir "assets/images"
check_dir "scripts"
check_dir "scripts/core"
check_dir "scripts/shapes"
check_dir "scripts/tools"
check_dir "scripts/ui"
check_dir "scripts/utils"
check_dir "styles"
echo ""

echo "📄 检查 HTML 文件..."
check_file "index.html"
check_file "test.html"
echo ""

echo "🎨 检查 CSS 文件..."
check_file "styles/theme.css"
check_file "styles/layout.css"
check_file "styles/components.css"
check_file "styles/animations.css"
echo ""

echo "⚙️ 检查配置和入口..."
check_file "scripts/config.js"
check_file "scripts/main.js"
echo ""

echo "🔧 检查核心模块..."
check_file "scripts/core/canvas.js"
check_file "scripts/core/document.js"
check_file "scripts/core/history.js"
check_file "scripts/core/serializer.js"
echo ""

echo "📐 检查图形类..."
check_file "scripts/shapes/base.js"
check_file "scripts/shapes/point.js"
check_file "scripts/shapes/line.js"
check_file "scripts/shapes/rect.js"
check_file "scripts/shapes/circle.js"
check_file "scripts/shapes/polygon.js"
check_file "scripts/shapes/path.js"
echo ""

echo "🛠️ 检查工具类..."
check_file "scripts/tools/base.js"
check_file "scripts/tools/select.js"
check_file "scripts/tools/point.js"
check_file "scripts/tools/line.js"
check_file "scripts/tools/rect.js"
check_file "scripts/tools/circle.js"
check_file "scripts/tools/polygon.js"
check_file "scripts/tools/brush.js"
check_file "scripts/tools/eraser.js"
echo ""

echo "🎨 检查 UI 组件..."
check_file "scripts/ui/theme.js"
check_file "scripts/ui/navigation.js"
echo ""

echo "🔨 检查工具函数..."
check_file "scripts/utils/color.js"
check_file "scripts/utils/geometry.js"
check_file "scripts/utils/export.js"
check_file "scripts/utils/errors.js"
echo ""

echo "📚 检查文档..."
check_file "README.md"
check_file "QUICKSTART.md"
check_file "DEPLOYMENT.md"
check_file "PROJECT_SUMMARY.md"
echo ""

echo "📊 检查数据文件..."
check_file "assets/data/samples.json"
echo ""

echo "🚀 检查启动脚本..."
check_file "start.sh"
echo ""

# 统计结果
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 验证结果："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "总计: ${YELLOW}${total}${NC} 项"
echo -e "通过: ${GREEN}${passed}${NC} 项"
echo -e "失败: ${RED}${failed}${NC} 项"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！项目完整。${NC}"
    echo ""
    echo "🎉 项目已准备就绪！"
    echo ""
    echo "运行以下命令启动应用："
    echo "  ./start.sh"
    echo ""
    echo "或者："
    echo "  python3 -m http.server 8000"
    echo ""
    exit 0
else
    echo -e "${RED}❌ 发现 ${failed} 个问题，请检查缺失的文件。${NC}"
    echo ""
    exit 1
fi
