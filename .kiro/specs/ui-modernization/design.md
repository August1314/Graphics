# UI Modernization Design Document

## Overview

本设计文档详细描述了二维图形绘图系统前端界面的现代化改造方案。设计目标是创建一个简洁、专业、易用的商用级界面，同时保持与现有代码架构的兼容性。设计遵循现代UI/UX最佳实践，采用扁平化设计风格，统一的视觉语言，以及流畅的交互体验。

### Design Principles

1. **简洁至上** - 移除不必要的视觉元素，突出核心功能
2. **一致性** - 统一的配色、字体、间距、圆角等视觉元素
3. **可访问性** - 确保所有用户都能轻松使用
4. **响应式** - 适应不同屏幕尺寸和分辨率
5. **性能优先** - 流畅的动画和快速的响应

## Architecture

### Component Hierarchy

```
MainWindow
├── MenuBar (优化)
├── ToolBar (重新设计)
│   ├── ToolButtonGroup (工具按钮组)
│   ├── Separator (分隔线)
│   └── QuickStylePanel (快速样式面板)
├── CentralWidget (CanvasView)
├── DockWidgets
│   └── PropertyPanel (简化)
└── StatusBar (增强)
```

### Style System Architecture

```
StyleManager
├── ColorPalette (配色方案)
├── Typography (字体系统)
├── Spacing (间距系统)
├── BorderRadius (圆角系统)
└── Animations (动画系统)
```

## Components and Interfaces

### 1. Color Palette (配色方案)

#### Primary Colors
```python
PRIMARY = "#2563eb"      # 主色 - 蓝色
PRIMARY_HOVER = "#1d4ed8"
PRIMARY_ACTIVE = "#1e40af"
PRIMARY_LIGHT = "#dbeafe"
```

#### Neutral Colors
```python
BACKGROUND = "#ffffff"    # 主背景
BACKGROUND_ALT = "#f8fafc"  # 次背景
SURFACE = "#ffffff"       # 表面色
BORDER = "#e2e8f0"        # 边框色
DIVIDER = "#cbd5e1"       # 分隔线
```

#### Text Colors
```python
TEXT_PRIMARY = "#0f172a"    # 主文字
TEXT_SECONDARY = "#64748b"  # 次文字
TEXT_DISABLED = "#cbd5e1"   # 禁用文字
```

#### Semantic Colors
```python
SUCCESS = "#10b981"
WARNING = "#f59e0b"
ERROR = "#ef4444"
INFO = "#3b82f6"
```

### 2. Typography (字体系统)

```python
FONT_FAMILY = "system-ui, -apple-system, 'Segoe UI', sans-serif"

# Font Sizes
FONT_SIZE_XS = 11   # 小号文字
FONT_SIZE_SM = 12   # 次要文字
FONT_SIZE_BASE = 14 # 基础文字
FONT_SIZE_LG = 16   # 大号文字
FONT_SIZE_XL = 18   # 标题文字

# Font Weights
FONT_WEIGHT_NORMAL = 400
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_BOLD = 700
```

### 3. Spacing System (间距系统)

```python
SPACING_XS = 4    # 极小间距
SPACING_SM = 8    # 小间距
SPACING_MD = 12   # 中等间距
SPACING_LG = 16   # 大间距
SPACING_XL = 24   # 超大间距
SPACING_2XL = 32  # 极大间距
```

### 4. Border Radius (圆角系统)

```python
RADIUS_SM = 4     # 小圆角
RADIUS_MD = 6     # 中圆角
RADIUS_LG = 8     # 大圆角
RADIUS_XL = 12    # 超大圆角
RADIUS_FULL = 9999  # 完全圆角
```

### 5. Modern ToolBar Design

#### Layout Structure
```
[Select] [Point] [Line] [Rect] [Circle] [Polygon] [Brush] [Marker] [Calligraphy] [Eraser] | [Color] [Width] [Style]
```

#### Component Specifications

**Tool Button**
- Size: 36x36px
- Icon Size: 20x20px
- Border Radius: 6px
- Padding: 8px
- Margin: 4px
- Hover: background-color with 150ms transition
- Active: border + background color change

**Separator**
- Width: 1px
- Height: 32px
- Color: DIVIDER
- Margin: 0 8px

**Quick Style Panel**
- Background: SURFACE
- Border: 1px solid BORDER
- Border Radius: 8px
- Padding: 8px 12px
- Margin-left: auto (右对齐)

### 6. Color Picker Component

#### Design
```
┌─────────────────────────────┐
│  Current Color Preview      │
│  ┌─────────────────────┐   │
│  │                     │   │
│  │    [Color Block]    │   │
│  │                     │   │
│  └─────────────────────┘   │
│                             │
│  Quick Colors               │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┐│
│  │  │  │  │  │  │  │  │  ││
│  └──┴──┴──┴──┴──┴──┴──┴──┘│
│                             │
│  [Custom Color Picker...]   │
└─────────────────────────────┘
```

#### Quick Colors Preset
```python
QUICK_COLORS = [
    "#000000",  # 黑色
    "#ffffff",  # 白色
    "#ef4444",  # 红色
    "#f59e0b",  # 橙色
    "#eab308",  # 黄色
    "#22c55e",  # 绿色
    "#3b82f6",  # 蓝色
    "#a855f7",  # 紫色
]
```

### 7. Property Panel Redesign

#### Layout Structure
```
┌─────────────────────────┐
│  Property Panel         │
├─────────────────────────┤
│                         │
│  ┌─ Geometry ─────────┐│
│  │ Center X: [____]   ││
│  │ Center Y: [____]   ││
│  │ Radius:   [____]   ││
│  └────────────────────┘│
│                         │
│  ┌─ Stroke ───────────┐│
│  │ Color:  [■]        ││
│  │ Width:  [____]     ││
│  │ Style:  [____]     ││
│  └────────────────────┘│
│                         │
│  ┌─ Fill ─────────────┐│
│  │ Color:   [■]       ││
│  │ Opacity: [====]    ││
│  └────────────────────┘│
│                         │
└─────────────────────────┘
```

#### Card Style
```python
CARD_BACKGROUND = SURFACE
CARD_BORDER = "1px solid " + BORDER
CARD_RADIUS = RADIUS_LG
CARD_PADDING = SPACING_LG
CARD_MARGIN = SPACING_MD
CARD_SHADOW = "0 1px 3px rgba(0,0,0,0.1)"
```

### 8. Main Window Layout

#### Structure
```
┌──────────────────────────────────────────┐
│  Menu Bar                                │
├──────────────────────────────────────────┤
│  Tool Bar                                │
├──────────────────────────────────────────┤
│                    │                     │
│                    │   Property Panel    │
│    Canvas View     │   ┌───────────────┐│
│                    │   │               ││
│                    │   │               ││
│                    │   │               ││
│                    │   └───────────────┘│
│                    │                     │
├──────────────────────────────────────────┤
│  Status Bar                              │
└──────────────────────────────────────────┘
```

#### Spacing
- Window Padding: 0px (full bleed)
- Canvas Margin: 0px
- Dock Margin: 0px
- Status Bar Height: 24px

### 9. Enhanced Status Bar

#### Content Layout
```
[Tool: Select] | [Pos: 100, 200] | [Zoom: 100%] | [Objects: 5]
```

#### Styling
```python
STATUSBAR_HEIGHT = 24
STATUSBAR_BACKGROUND = BACKGROUND_ALT
STATUSBAR_BORDER_TOP = "1px solid " + BORDER
STATUSBAR_PADDING = "0 " + str(SPACING_MD) + "px"
STATUSBAR_FONT_SIZE = FONT_SIZE_SM
STATUSBAR_TEXT_COLOR = TEXT_SECONDARY
```

## Data Models

### StyleConfig Class

```python
@dataclass
class StyleConfig:
    """样式配置数据类"""
    
    # Colors
    primary: str
    primary_hover: str
    primary_active: str
    background: str
    surface: str
    border: str
    text_primary: str
    text_secondary: str
    
    # Typography
    font_family: str
    font_size_base: int
    font_weight_normal: int
    
    # Spacing
    spacing_sm: int
    spacing_md: int
    spacing_lg: int
    
    # Border Radius
    radius_sm: int
    radius_md: int
    radius_lg: int
    
    # Animations
    transition_fast: str  # "150ms"
    transition_normal: str  # "250ms"
```

### ThemeManager Class

```python
class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        self._current_theme = "light"
        self._themes = {
            "light": self._create_light_theme(),
            "dark": self._create_dark_theme()
        }
    
    def get_current_theme(self) -> StyleConfig:
        """获取当前主题配置"""
        return self._themes[self._current_theme]
    
    def set_theme(self, theme_name: str):
        """切换主题"""
        if theme_name in self._themes:
            self._current_theme = theme_name
    
    def generate_stylesheet(self) -> str:
        """生成QSS样式表"""
        theme = self.get_current_theme()
        return self._build_qss(theme)
```

## Error Handling

### Style Loading Errors

```python
try:
    stylesheet = theme_manager.generate_stylesheet()
    app.setStyleSheet(stylesheet)
except Exception as e:
    logger.error(f"Failed to load stylesheet: {e}")
    # Fallback to default Qt style
    app.setStyleSheet("")
```

### Icon Loading Errors

```python
def get_icon(name: str) -> QIcon:
    try:
        return icon_provider.get(name)
    except Exception as e:
        logger.warning(f"Failed to load icon '{name}': {e}")
        return QIcon()  # Return empty icon as fallback
```

## Testing Strategy

### Visual Regression Testing

1. **Screenshot Comparison**
   - 捕获关键界面状态的截图
   - 与基准截图进行像素级比较
   - 检测意外的视觉变化

2. **Component Testing**
   - 测试每个UI组件的渲染
   - 验证样式是否正确应用
   - 检查响应式行为

### Interaction Testing

1. **Tool Switching**
   - 测试工具切换的响应时间
   - 验证视觉反馈是否正确
   - 检查状态栏更新

2. **Color Picker**
   - 测试颜色选择功能
   - 验证颜色预览更新
   - 检查快速颜色选择

3. **Property Panel**
   - 测试属性值更新
   - 验证实时预览
   - 检查输入验证

### Performance Testing

1. **Rendering Performance**
   - 测量界面初始化时间
   - 测量工具切换延迟
   - 测量属性更新延迟

2. **Memory Usage**
   - 监控内存占用
   - 检测内存泄漏
   - 优化资源使用

### Accessibility Testing

1. **Keyboard Navigation**
   - 测试Tab键导航顺序
   - 验证快捷键功能
   - 检查焦点指示器

2. **Contrast Ratio**
   - 测量文字和背景对比度
   - 确保符合WCAG AA标准
   - 验证色盲友好性

3. **Screen Reader**
   - 测试屏幕阅读器兼容性
   - 验证ARIA标签
   - 检查语义化HTML

## Implementation Details

### QSS Stylesheet Structure

```css
/* ===== Global Styles ===== */
QMainWindow {
    background-color: #ffffff;
}

/* ===== ToolBar ===== */
QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 12px;
    spacing: 4px;
}

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

/* ===== DockWidget ===== */
QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}

QDockWidget::title {
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
}

/* ===== Buttons ===== */
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

/* ===== Input Fields ===== */
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

/* ===== Sliders ===== */
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

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
    padding: 0 12px;
    font-size: 12px;
    color: #64748b;
}

/* ===== Menus ===== */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 4px 8px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #f1f5f9;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 32px 8px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #f1f5f9;
}

QMenu::separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 4px 8px;
}
```

### Icon System Enhancement

```python
class ModernIconProvider(IconProvider):
    """现代化图标提供器"""
    
    def __init__(self, theme: str = "light"):
        super().__init__(theme)
        self._icon_size = 20  # 统一图标尺寸
        self._icon_color = "#0f172a" if theme == "light" else "#f8fafc"
    
    def get_colored_icon(self, name: str, color: str) -> QIcon:
        """获取指定颜色的图标"""
        # 实现图标着色逻辑
        pass
    
    def get_icon_with_badge(self, name: str, badge: str) -> QIcon:
        """获取带徽章的图标"""
        # 实现徽章叠加逻辑
        pass
```

### Animation System

```python
class AnimationHelper:
    """动画辅助类"""
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 250):
        """淡入动画"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
    
    @staticmethod
    def slide_in(widget: QWidget, direction: str = "left", duration: int = 250):
        """滑入动画"""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        # 设置起始和结束位置
        animation.start()
```

## Migration Strategy

### Phase 1: Style System Setup
1. 创建 `StyleManager` 类
2. 定义配色方案和样式常量
3. 生成基础QSS样式表
4. 应用到主窗口

### Phase 2: ToolBar Redesign
1. 移除下拉菜单，展开所有工具按钮
2. 确认移除喷枪工具
3. 添加分隔线
4. 优化快速样式面板
5. 应用新样式

### Phase 3: Property Panel Simplification
1. 移除标签页，使用单页面
2. 采用卡片式布局
3. 优化输入控件样式
4. 添加空状态提示

### Phase 4: Color Picker Enhancement
1. 创建自定义颜色选择器组件
2. 添加快速颜色预设
3. 优化颜色预览显示
4. 集成到工具栏和属性面板

### Phase 5: Main Window Polish
1. 移除文件停靠面板
2. 优化菜单栏
3. 增强状态栏
4. 调整整体布局

### Phase 6: Testing and Refinement
1. 进行视觉回归测试
2. 性能测试和优化
3. 可访问性测试
4. 用户反馈收集和改进

## Responsive Design

### Breakpoints

```python
BREAKPOINT_SM = 800   # 小屏幕
BREAKPOINT_MD = 1024  # 中等屏幕
BREAKPOINT_LG = 1280  # 大屏幕
```

### Adaptive Behaviors

**Small Screen (< 800px)**
- 工具栏折叠为下拉菜单
- 属性面板自动隐藏
- 状态栏显示简化信息

**Medium Screen (800-1024px)**
- 工具栏显示常用工具
- 属性面板可停靠
- 状态栏显示完整信息

**Large Screen (> 1024px)**
- 工具栏显示所有工具
- 属性面板固定显示
- 状态栏显示详细信息

## Accessibility Features

### Keyboard Navigation

```python
# 工具快捷键
SHORTCUTS = {
    "V": "select",
    "P": "point",
    "L": "line",
    "R": "rect",
    "C": "circle",
    "G": "polygon",
    "B": "brush_pen",
    "M": "brush_marker",
    "K": "brush_calligraphy",
    "E": "eraser",
}
```

### Focus Indicators

```css
*:focus {
    outline: 2px solid #2563eb;
    outline-offset: 2px;
}
```

### ARIA Labels

```python
button.setAccessibleName("选择工具")
button.setAccessibleDescription("选择和移动画布上的图形")
```

## Performance Optimizations

### Style Caching

```python
class StyleCache:
    """样式缓存"""
    
    def __init__(self):
        self._cache = {}
    
    def get_stylesheet(self, theme: str) -> str:
        if theme not in self._cache:
            self._cache[theme] = self._generate_stylesheet(theme)
        return self._cache[theme]
```

### Lazy Loading

```python
# 延迟加载非关键UI组件
def _init_property_panel(self):
    if not hasattr(self, '_property_panel'):
        self._property_panel = PropertyPanel(self)
    return self._property_panel
```

### Icon Preloading

```python
# 预加载常用图标
def preload_icons(self):
    for name in ["select", "point", "line", "rect", "circle"]:
        self.icon_provider.get(name)
```

## Future Enhancements

1. **Dark Mode Support** - 完整的深色主题
2. **Custom Themes** - 用户自定义主题
3. **Icon Customization** - 用户自定义图标
4. **Layout Presets** - 预设布局方案
5. **Workspace Profiles** - 工作区配置文件
6. **Touch Support** - 触摸屏优化
7. **Tablet Support** - 数位板压感支持
8. **Plugin System** - 插件系统支持自定义UI

## Conclusion

本设计文档提供了一个全面的UI现代化方案，涵盖了从配色方案到组件设计，从交互动画到可访问性的各个方面。通过实施这个设计，我们将创建一个简洁、专业、易用的商用级绘图应用界面。
