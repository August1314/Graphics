# UI样式指南

## 概述

本文档定义了二维图形绘图系统的UI样式规范，包括配色方案、字体系统、间距系统和组件样式。

## 配色方案

### 主色系
```python
PRIMARY = "#2563eb"          # 主色 - 蓝色
PRIMARY_HOVER = "#1d4ed8"    # 悬停状态
PRIMARY_ACTIVE = "#1e40af"   # 激活状态
PRIMARY_LIGHT = "#dbeafe"    # 浅色背景
```

### 中性色系
```python
BACKGROUND = "#ffffff"       # 主背景
BACKGROUND_ALT = "#f8fafc"   # 次背景
SURFACE = "#ffffff"          # 表面色
BORDER = "#e2e8f0"           # 边框色
DIVIDER = "#cbd5e1"          # 分隔线
```

### 文字色系
```python
TEXT_PRIMARY = "#0f172a"     # 主文字
TEXT_SECONDARY = "#64748b"   # 次文字
TEXT_DISABLED = "#cbd5e1"    # 禁用文字
```

### 语义色系
```python
SUCCESS = "#10b981"          # 成功
WARNING = "#f59e0b"          # 警告
ERROR = "#ef4444"            # 错误
INFO = "#3b82f6"             # 信息
```

## 字体系统

### 字体族
```python
FONT_FAMILY = "system-ui, -apple-system, 'Segoe UI', sans-serif"
```

### 字体大小
```python
FONT_SIZE_XS = 11    # 小号文字
FONT_SIZE_SM = 12    # 次要文字
FONT_SIZE_BASE = 14  # 基础文字
FONT_SIZE_LG = 16    # 大号文字
FONT_SIZE_XL = 18    # 标题文字
```

### 字体粗细
```python
FONT_WEIGHT_NORMAL = 400
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_BOLD = 700
```

## 间距系统

```python
SPACING_XS = 4     # 极小间距
SPACING_SM = 8     # 小间距
SPACING_MD = 12    # 中等间距
SPACING_LG = 16    # 大间距
SPACING_XL = 24    # 超大间距
SPACING_2XL = 32   # 极大间距
```

## 圆角系统

```python
RADIUS_SM = 4      # 小圆角
RADIUS_MD = 6      # 中圆角
RADIUS_LG = 8      # 大圆角
RADIUS_XL = 12     # 超大圆角
RADIUS_FULL = 9999 # 完全圆角
```

## 组件样式

### 工具栏按钮
```css
QToolBar QToolButton {
    background-color: transparent;
    border: 2px solid transparent;
    border-radius: 6px;
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
}

QToolBar QToolButton:hover {
    background-color: #f1f5f9;
}

QToolBar QToolButton:checked {
    background-color: #dbeafe;
    border-color: #2563eb;
}
```

### 按钮
```css
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #cbd5e1;
}
```

### 输入控件
```css
QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 14px;
    color: #0f172a;
    min-height: 32px;
}

QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #2563eb;
    outline: none;
}
```

### 滑块
```css
QSlider::groove:horizontal {
    background-color: #e2e8f0;
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #2563eb;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #1d4ed8;
}
```

## 使用示例

### 创建带样式的按钮
```python
from PySide6.QtWidgets import QPushButton

button = QPushButton("保存")
button.setObjectName("primary-button")
# 样式会自动应用
```

### 创建工具栏按钮
```python
from PySide6.QtGui import QAction
from app.ui.icon_provider import IconProvider

icons = IconProvider("light")
action = QAction(icons.get("select"), "选择", self)
action.setCheckable(True)
action.setToolTip("选择工具 (V)")
action.setStatusTip("选择和移动图形")
```

### 应用自定义颜色
```python
# 使用配色方案中的颜色
button.setStyleSheet(f"background-color: {PRIMARY}; color: white;")
```

## 可访问性

### 键盘导航
- 所有交互元素都支持Tab键导航
- 焦点指示器清晰可见（2px蓝色边框）
- 快捷键提示显示在工具提示中

### 对比度
- 文字和背景对比度符合WCAG AA标准
- 主文字 (#0f172a) 在白色背景上对比度 > 4.5:1
- 次文字 (#64748b) 在白色背景上对比度 > 4.5:1

### 屏幕阅读器
- 所有按钮都有描述性的文本标签
- 使用 `setWhatsThis()` 提供详细说明
- 使用 `setStatusTip()` 提供状态信息

## 响应式设计

### 断点
```python
BREAKPOINT_SM = 800   # 小屏幕
BREAKPOINT_MD = 1024  # 中等屏幕
BREAKPOINT_LG = 1280  # 大屏幕
```

### 自适应行为
- 小屏幕（< 800px）：工具栏折叠，属性面板自动隐藏
- 中等屏幕（800-1024px）：工具栏显示常用工具
- 大屏幕（> 1024px）：显示所有工具和面板

## 性能优化

### 图标缓存
```python
# IconProvider 自动缓存图标
icons = IconProvider("light")
icon = icons.get("select")  # 首次加载
icon = icons.get("select")  # 从缓存读取
```

### 样式表优化
- 使用简洁的选择器
- 避免过度嵌套
- 合理使用继承

## 更新日志

### 2025-10-09
- 初始版本
- 定义完整的设计系统
- 添加组件样式规范
- 添加可访问性指南
