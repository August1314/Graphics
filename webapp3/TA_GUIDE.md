# 助教运行与验证指南（webapp3）

> 目标：最快速跑起来并验证关键功能。只需 Node.js（16+），无需后端和数据库。

## 1. 准备环境
- 必装：Node.js 16+（含 npm）
- 浏览器：Chrome / Edge / Firefox / Safari 均可

## 2. 安装依赖
```bash
cd webapp3
npm install
```

## 3. 启动方式
### macOS / Linux
```bash
chmod +x start.sh
./start.sh          # 推荐脚本
# 或 npm run dev
```

### Windows
```cmd
setup_env.bat       # 首次安装依赖
run_server.bat      # 启动开发服务器
# 或 npm run dev
```

默认地址：`http://localhost:5173`

## 4. 关键功能验收清单
- **工具栏**：工具图标下方有文字标签；两行布局（工具 / 视图与算法）。
- **绘制**：点 / 线 / 矩形 / 圆 / 多边形 / 画笔 可正常绘制；矩形默认使用 Canvas 路径，填充与边框对齐。
- **曲线**：Bézier、B 样条可添加控制点，双击结束；选择工具点击控制点会自动切换到对应曲线工具继续编辑。
- **曲面**：曲面工具拖出 4×4 控制网；右侧下拉“曲面模式”可切换网格/填充，填充模式下有默认填充色，切回网格不报错。
- **视图开关**：网格、调试（性能面板）、光栅化（切换算法）可开关，切换后会立即重绘。
- **样式调整**：选中图形后修改描边色/填充色/线宽即时生效；选择填充色时自动关闭“透明”。
- **历史与导出**：撤销 / 重做 / 清空；导出 PNG 按钮可下载当前画面。
- **教程**：右下角“教程”按钮可打开交互式指引。

## 5. 常见问题
- **Canvas2D readback 警告**：`willReadFrequently` 已启用，仅为性能提示，不影响功能。
- **端口占用**：修改 `vite.config.mts` 中的 dev server 端口，或启动时加 `--host --port 5174`。
- **依赖安装慢**：可使用 `npm config set registry https://registry.npmmirror.com` 之后再 `npm install`。

## 6. 目录速览
- `src/`：React 界面（Toolbar、CanvasPane、TourGuide、DrawPage 等）
- `scripts/`：核心绘图引擎与算法（shapes、tools、algorithms、core）
- `start.sh` / `run_server.bat` / `setup_env.bat`：一键安装与启动脚本
- `verify.sh`：基础检查脚本

## 7. 生产构建（可选）
```bash
npm run build
npm run preview   # 预览 dist
```

## 8. 最小验证步骤（推荐）
1) `npm install && npm run dev`
2) 打开 `http://localhost:5173`
3) 画一个矩形，确认填充与边框重合；切换“光栅化”开关后仍正常。
4) 画曲面，切换“曲面模式”到填充，确认有颜色；再切回网格不报错。
5) 点击“导出”按钮，确认能下载 PNG。***

