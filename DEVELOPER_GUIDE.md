# 开发者指南

**版本**: 2.0.0  
**更新时间**: 2025-10-08

---

## 📚 目录

1. [项目概述](#项目概述)
2. [架构设计](#架构设计)
3. [核心模块](#核心模块)
4. [扩展指南](#扩展指南)
5. [代码规范](#代码规范)
6. [测试指南](#测试指南)
7. [贡献指南](#贡献指南)

---

## 项目概述

这是一个基于 PySide6 的图形绘制应用程序，支持多种图形绘制、样式编辑、撤销/重做等功能。

### 技术栈
- **UI 框架**: PySide6 (Qt for Python)
- **Python 版本**: 3.11+
- **测试框架**: pytest
- **代码质量**: pylint, mypy

### 项目结构
```
app/
├── core/               # 核心业务逻辑
│   ├── commands/       # 撤销/重做命令
│   ├── shapes/         # 图形类
│   ├── tools/          # 绘图工具
│   ├── document.py     # 文档管理
│   ├── selection.py    # 选择管理
│   ├── styles.py       # 样式管理
│   └── serializer.py   # 序列化
├── controllers/        # 控制器
│   ├── document_controller.py
│   └── property_controller.py
├── managers/           # 管理器
│   └── tool_manager.py
├── state/              # 状态管理
│   └── view_state.py
├── ui/                 # UI 组件
│   ├── main_window.py
│   ├── canvas_view.py
│   ├── canvas_scene.py
│   ├── toolbar.py
│   └── property_panel.py
├── utils/              # 工具类
│   ├── logging_config.py
│   ├── exceptions.py
│   └── error_handler.py
└── main.py             # 应用入口

tests/
├── unit/               # 单元测试
├── integration/        # 集成测试
└── manual/             # 手动测试脚本
```

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────┐
│                  MainWindow                      │
│  (UI 初始化、事件协调)                           │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────┬──────────┐
    │                 │          │          │
┌───▼────┐  ┌────────▼───┐  ┌──▼──────┐  ┌▼─────────┐
│Document│  │Property    │  │Tool     │  │ViewState │
│Ctrl    │  │Controller  │  │Manager  │  │Machine   │
└───┬────┘  └────────┬───┘  └──┬──────┘  └┬─────────┘
    │                │          │          │
┌───▼────────────────▼──────────▼──────────▼─────┐
│              Core Modules                       │
│  Document, SelectionManager, StyleManager      │
└─────────────────────────────────────────────────┘
```

### 设计模式

1. **MVC 模式**
   - Model: Document, Scene
   - View: MainWindow, CanvasView
   - Controller: DocumentController, PropertyController

2. **命令模式**
   - 所有可撤销操作都封装为 Command
   - 使用 QUndoStack 管理历史

3. **管理器模式**
   - SelectionManager: 管理选择
   - StyleManager: 管理样式
   - ToolManager: 管理工具

4. **状态模式**
   - ViewStateMachine: 管理视图状态

5. **观察者模式**
   - 使用 Qt 信号/槽机制
   - 模块间松耦合

---

## 核心模块

### Document (文档管理)

**职责**: 管理文档的完整生命周期

**主要方法**:
```python
# 创建新文档
document.new()

# 保存文档
document.save(file_path)

# 加载文档
document.load(file_path)

# 导出为图片
document.export_png(file_path, width, height)

# 添加图形
document.add_shape(item)

# 删除图形
document.remove_shape(item)
```

**信号**:
- `modified_changed(bool)`: 修改状态变化
- `file_path_changed(str)`: 文件路径变化
- `saved(str)`: 保存成功
- `loaded(str)`: 加载成功

### SelectionManager (选择管理)

**职责**: 统一管理图形的选择状态

**主要方法**:
```python
# 选择图形
selection_mgr.select(items, mode=SelectionMode.REPLACE)

# 选择所有
selection_mgr.select_all()

# 清空选择
selection_mgr.clear_selection()

# 获取选中的图形
items = selection_mgr.get_selected_items()

# 检查是否有选择
has_sel = selection_mgr.has_selection()
```

**选择模式**:
- `REPLACE`: 替换当前选择
- `ADD`: 添加到选择
- `TOGGLE`: 切换选择状态
- `REMOVE`: 从选择中移除

### StyleManager (样式管理)

**职责**: 管理图形的样式属性

**主要方法**:
```python
# 应用样式
style_mgr.apply_style(item, style)

# 应用画笔
style_mgr.apply_pen(item, pen)

# 应用填充
style_mgr.apply_brush(item, brush)

# 批量应用样式
style_mgr.apply_style_to_selection(items, style)

# 获取样式
style = style_mgr.get_style(item)
```

**Style 数据类**:
```python
@dataclass
class Style:
    pen_color: QColor
    pen_width: float
    pen_style: Qt.PenStyle
    brush_color: QColor
    brush_style: Qt.BrushStyle
    opacity: float
```

### PropertyController (属性控制器)

**职责**: 统一处理属性更新，自动创建撤销命令

**主要方法**:
```python
# 更新画笔颜色
property_ctrl.update_pen_color(color)

# 更新画笔宽度
property_ctrl.update_pen_width(width)

# 更新填充颜色
property_ctrl.update_brush_color(color)

# 更新不透明度
property_ctrl.update_opacity(opacity)
```

**特点**:
- 自动创建撤销命令
- 支持批量更新选中图形
- 模板方法模式消除重复代码

### ToolManager (工具管理器)

**职责**: 管理所有绘图工具

**主要方法**:
```python
# 设置当前工具
tool_mgr.set_tool("circle")

# 获取当前工具
tool = tool_mgr.get_current_tool()

# 取消当前工具
tool_mgr.cancel_current_tool()

# 检查工具是否激活
is_active = tool_mgr.is_tool_active()
```

**注册的工具**:
- 基础: `select`, `point`, `line`, `rect`, `circle`, `polygon`
- 画笔: `brush_pen`, `brush_marker`, `brush_calligraphy`, `brush_spray`
- 橡皮擦: `eraser`

### ViewStateMachine (视图状态机)

**职责**: 管理视图的状态转换

**状态**:
- `IDLE`: 空闲（选择模式）
- `DRAWING`: 正在绘制
- `DRAGGING`: 正在拖动
- `RUBBER_BAND`: 框选中
- `PANNING`: 平移中
- `PASTE_PENDING`: 等待粘贴
- `EDITING`: 编辑模式

**主要方法**:
```python
# 开始绘制
state_machine.start_drawing()

# 开始拖动
state_machine.start_dragging()

# 完成操作
state_machine.finish_operation()

# 检查状态
if state_machine.is_in_state(ViewState.DRAWING):
    # 处理绘制逻辑
```

---

## 扩展指南

### 添加新的图形类型

1. **创建图形类**

```python
# app/core/shapes/my_shape_item.py
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen

class MyShapeItem(QGraphicsItem):
    def __init__(self, ...):
        super().__init__()
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        
        # 性能优化：启用缓存
        self.setCacheMode(self.CacheMode.ItemCoordinateCache)
    
    def boundingRect(self):
        # 返回包围盒
        pass
    
    def paint(self, painter, option, widget):
        # 绘制图形
        painter.drawXXX(...)
        
        # 选择高亮
        if self.isSelected():
            sel_pen = QPen(QColor(0, 120, 215))
            sel_pen.setWidth(1)
            sel_pen.setCosmetic(True)
            sel_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())
    
    def to_dict(self) -> dict:
        # 序列化
        return {
            'type': 'MyShape',
            # ... 属性
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        # 反序列化
        return cls(...)
```

2. **注册到序列化器**

```python
# app/core/serializer.py
from app.core.shapes.my_shape_item import MyShapeItem

class Serializer:
    def __init__(self):
        self._type_registry = {
            # ...
            'MyShape': MyShapeItem,
        }
```

3. **创建绘图工具**

```python
# app/core/tools/my_shape_tool.py
from app.core.tools.base_tool import BaseTool

class MyShapeTool(BaseTool):
    def on_press(self, scene, scene_pos, event):
        # 开始绘制
        pass
    
    def on_move(self, scene, scene_pos, event):
        # 更新绘制
        pass
    
    def on_release(self, scene, scene_pos, event):
        # 完成绘制
        pass
```

4. **注册工具**

```python
# app/managers/tool_manager.py
from app.core.tools.my_shape_tool import MyShapeTool

class ToolManager:
    def __init__(self, view):
        self._tools = {
            # ...
            'my_shape': MyShapeTool(),
        }
```

5. **添加到工具栏**

```python
# app/ui/toolbar.py
self.action_my_shape = QAction(icon, "我的图形", self)
self.action_my_shape.setCheckable(True)
self.action_my_shape.setData("my_shape")
self.action_my_shape.setToolTip("我的图形工具 (Y)")
self.action_my_shape.setStatusTip("绘制我的图形")
self._group.addAction(self.action_my_shape)
```

### 添加新的属性

1. **扩展 Style 数据类**

```python
# app/core/styles.py
@dataclass
class Style:
    # 现有属性...
    my_property: float = 1.0  # 新属性
```

2. **添加属性更新方法**

```python
# app/controllers/property_controller.py
def update_my_property(self, value: float) -> None:
    """更新我的属性"""
    def setter(item):
        if hasattr(item, 'set_my_property'):
            item.set_my_property(value)
    
    self._update_property(
        "修改我的属性",
        setter,
        lambda item: getattr(item, 'my_property', 1.0)
    )
```

3. **添加到属性面板**

```python
# app/ui/property_panel.py
# 添加控件和信号
```

---

## 代码规范

### Python 代码风格

遵循 **PEP 8** 规范：

```python
# 导入顺序
from __future__ import annotations  # 1. future imports

import os  # 2. 标准库
import sys

from PySide6.QtCore import Qt  # 3. 第三方库
from PySide6.QtWidgets import QWidget

from app.core.document import Document  # 4. 本地模块

# 类定义
class MyClass:
    """类文档字符串
    
    详细说明...
    
    Attributes:
        attr1: 属性说明
    """
    
    def __init__(self, param: str):
        """初始化方法
        
        Args:
            param: 参数说明
        """
        self._attr = param
    
    def method(self, arg: int) -> str:
        """方法文档字符串
        
        Args:
            arg: 参数说明
        
        Returns:
            返回值说明
        
        Raises:
            ValueError: 异常说明
        """
        return str(arg)
```

### 文档字符串格式

使用 **Google 风格**：

```python
def function(arg1: str, arg2: int = 0) -> bool:
    """简短描述（一行）
    
    详细描述（可选，多行）
    
    Args:
        arg1: 第一个参数的说明
        arg2: 第二个参数的说明，默认值为 0
    
    Returns:
        返回值的说明
    
    Raises:
        ValueError: 参数无效时抛出
        IOError: 文件操作失败时抛出
    
    Examples:
        >>> function("test", 42)
        True
    """
    pass
```

### 命名规范

- **类名**: `PascalCase` (例如: `DocumentController`)
- **函数/方法**: `snake_case` (例如: `get_selected_items`)
- **常量**: `UPPER_SNAKE_CASE` (例如: `MAX_SIZE`)
- **私有成员**: `_leading_underscore` (例如: `_internal_method`)

### 类型注解

使用类型注解提升代码可读性：

```python
from typing import List, Optional, Dict, Any

def process_items(
    items: List[QGraphicsItem],
    options: Optional[Dict[str, Any]] = None
) -> bool:
    """处理图形项"""
    pass
```

### 日志记录

使用统一的日志系统：

```python
import logging

logger = logging.getLogger('drawing_app.module_name')

# 日志级别
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 异常处理

使用自定义异常和错误处理装饰器：

```python
from app.utils.exceptions import FileOperationError
from app.utils.error_handler import handle_errors

@handle_errors(show_dialog=True)
def save_file(path: str) -> None:
    """保存文件
    
    Raises:
        FileOperationError: 文件操作失败
    """
    try:
        # 保存逻辑
        pass
    except IOError as e:
        raise FileOperationError(f"保存失败: {e}")
```

---

## 测试指南

### 单元测试

使用 pytest 编写单元测试：

```python
# tests/unit/test_document.py
import pytest
from app.core.document import Document

class TestDocument:
    """Document 类的单元测试"""
    
    @pytest.fixture
    def document(self, qtbot):
        """创建测试用的 Document 实例"""
        from PySide6.QtWidgets import QGraphicsScene
        from PySide6.QtGui import QUndoStack
        
        scene = QGraphicsScene()
        undo_stack = QUndoStack()
        doc = Document(scene, undo_stack)
        return doc
    
    def test_new_document(self, document):
        """测试创建新文档"""
        document.new()
        assert not document.is_modified()
        assert document.file_path is None
    
    def test_add_shape(self, document):
        """测试添加图形"""
        from app.core.shapes.circle_item import CircleItem
        
        item = CircleItem(0, 0, 10)
        document.add_shape(item)
        
        assert document.is_modified()
        assert item in document.get_all_shapes()
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_document.py

# 运行特定测试类
pytest tests/unit/test_document.py::TestDocument

# 运行特定测试方法
pytest tests/unit/test_document.py::TestDocument::test_new_document

# 显示详细输出
pytest -v

# 显示代码覆盖率
pytest --cov=app --cov-report=html
```

### 性能测试

```python
# tests/performance/test_spray_performance.py
import time

def test_spray_tool_performance():
    """测试喷枪工具性能"""
    # 创建工具
    tool = BrushTool(BrushTool.BrushType.SPRAY)
    
    # 模拟绘制
    start = time.perf_counter()
    for i in range(100):
        tool.on_move(scene, point, event)
    end = time.perf_counter()
    
    # 验证性能
    avg_time = (end - start) / 100
    assert avg_time < 0.033  # 30 FPS
```

---

## 贡献指南

### 开发流程

1. **Fork 项目**
2. **创建功能分支**: `git checkout -b feature/my-feature`
3. **编写代码**: 遵循代码规范
4. **编写测试**: 确保测试覆盖率
5. **提交代码**: `git commit -m "Add: 我的功能"`
6. **推送分支**: `git push origin feature/my-feature`
7. **创建 Pull Request**

### 提交信息规范

使用语义化的提交信息：

```
类型: 简短描述

详细描述（可选）

相关 Issue: #123
```

**类型**:
- `Add`: 新增功能
- `Fix`: 修复 bug
- `Update`: 更新功能
- `Refactor`: 重构代码
- `Docs`: 文档更新
- `Test`: 测试相关
- `Style`: 代码格式
- `Perf`: 性能优化

**示例**:
```
Add: 添加圆形工具

实现了圆形绘制工具，支持：
- 拖动绘制圆形
- 撤销/重做
- 样式编辑

相关 Issue: #42
```

### Code Review 检查清单

- [ ] 代码符合 PEP 8 规范
- [ ] 有完整的文档字符串
- [ ] 有类型注解
- [ ] 有单元测试
- [ ] 测试通过
- [ ] 无 lint 警告
- [ ] 性能符合要求
- [ ] 无安全问题

---

## 常见问题

### Q: 如何调试应用？

A: 使用日志系统：

```python
import logging
logger = logging.getLogger('drawing_app')
logger.setLevel(logging.DEBUG)

# 在代码中添加日志
logger.debug(f"变量值: {value}")
```

### Q: 如何优化性能？

A: 参考 Phase 4 的优化技术：
1. 使用节流机制
2. 启用图形缓存
3. 局部更新而非全局刷新
4. 使用 cosmetic pen

### Q: 如何处理大文件？

A: 
1. 使用流式加载
2. 分批处理图形
3. 显示进度条
4. 异步加载

---

## 参考资源

### 官方文档
- [PySide6 文档](https://doc.qt.io/qtforpython/)
- [Qt 文档](https://doc.qt.io/)
- [Python 文档](https://docs.python.org/3/)

### 相关项目
- [Qt Graphics View Framework](https://doc.qt.io/qt-6/graphicsview.html)
- [Qt Undo Framework](https://doc.qt.io/qt-6/qundo.html)

---

**文档维护者**: Kiro AI Assistant  
**最后更新**: 2025-10-08

