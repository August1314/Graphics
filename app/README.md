# 应用目录说明（app/）

本目录包含二维绘图应用的全部源码与资源。入口为 `main.py`（模块方式运行）。

## 从零配置到运行（Conda）

以下命令在项目根目录执行：

```
# 1) 创建并激活环境（可自定义 python 版本）
conda create -n pnt python=3.11 -y
conda activate pnt

# 2) 安装依赖（优先使用 requirements.txt）
pip install -r requirements.txt

# 3) 运行应用
python -m app.main

# 总结
conda create -n pnt python=3.11 -y
conda activate pnt
pip install -r requirements.txt
python -m app.main
```

## 目录结构

- `main.py`：应用入口，初始化 Qt 应用、加载主题、创建 `MainWindow`。
- `core/`
  - `shapes/`：自定义 `QGraphicsItem` 图元（`CircleItem`、`RectItem`、`BrushPathItem` 等）
  - `tools/`：画布工具（画笔、直线、矩形、橡皮擦等）
  - `commands/`：撤销/重做命令（基于 `QUndoStack`）
  - `serializer.py`：场景 JSON 编解码
- `ui/`
  - `main_window.py`：主窗口、菜单/工具栏、属性面板、保存/加载
  - `canvas_view.py`：`QGraphicsView` 子类，缩放/平移、工具分派、框选与拖动
  - `canvas_scene.py`：`QGraphicsScene` 子类（稳定性暂时关闭自动高亮）
  - `property_panel.py` 与 `props/`：属性面板组件（画笔、圆、矩形等）
- `resources/`：图标与主题资源
- `i18n/`：多语言（占位）
- `io/`：样例数据等

## 功能概览

- 创建：点/线/矩形/圆/多边形、自由画笔路径
- 选择/移动：支持框选与多选成组移动（一次撤销全部回位）
- 样式：颜色、线宽、线型（实线/虚线等），均纳入撤销/重做
- 橡皮擦：对象擦除（默认），保留预览指示
- JSON：保存/加载场景（`scene.json`）
- 主题：`qt_material`（在 `main.py` 配置）

## 重要交互注意

- 画笔宽度需点击“应用”按钮提交，再切换样式；可避免 Qt 层在同一事件周期内的重入导致不稳定。
- 框选期间不会刷新属性面板，避免几何被回写导致“越选越大”。
- 自动高亮（加粗描边）已关闭，选中反馈使用各图元的虚线框。

## 开发提示

- 撤销/重做接入：见 `ui/main_window.py`；所有更改尽量以命令入栈。
- 属性回写：多数地方对 `scene.update_base_style()` 做了 `blockSignals(True/False)` 包裹以防重入。
- 序列化：为新图元实现 `to_dict()/from_dict()` 以参与 `serializer.dump/load`。

## 依赖

- Python 3.10+
- PySide6
- qt-material（可选）

