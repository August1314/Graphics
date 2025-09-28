from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QToolBar, QToolButton, QMenu
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from app.ui.icon_provider import IconProvider


class ToolBar(QToolBar):
    toolChanged = Signal(str)
    # 快速笔触设置
    quickStrokeColorChanged = Signal(object)  # QColor
    quickStrokeWidthChanged = Signal(float)
    quickStrokeDashChanged = Signal(object)   # Qt.PenStyle

    def __init__(self, parent=None) -> None:
        super().__init__("工具", parent)
        self.setMovable(True)
        self.setFloatable(True)
        self._icons = IconProvider("light")
        # 统一图标大小与展示风格
        self.setIconSize(QSize(18, 18))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self._group = QActionGroup(self)
        self._group.setExclusive(True)

        # 工具动作：选择
        self.action_select = QAction(self._icons.get("select"), "选择", self)
        self.action_select.setCheckable(True)
        self.action_select.setData("select")
        self.action_select.setIconVisibleInMenu(True)
        self._group.addAction(self.action_select)
        self.addAction(self.action_select)

        # 形状动作
        self.action_point = QAction(self._icons.get("point"), "点", self); self.action_point.setCheckable(True); self.action_point.setData("point"); self.action_point.setIconVisibleInMenu(True); self._group.addAction(self.action_point)
        self.action_line = QAction(self._icons.get("line"), "直线", self); self.action_line.setCheckable(True); self.action_line.setData("line"); self.action_line.setIconVisibleInMenu(True); self._group.addAction(self.action_line)
        self.action_rect = QAction(self._icons.get("rect"), "矩形", self); self.action_rect.setCheckable(True); self.action_rect.setData("rect"); self.action_rect.setIconVisibleInMenu(True); self._group.addAction(self.action_rect)
        self.action_ellipse = QAction(self._icons.get("circle"), "圆", self); self.action_ellipse.setCheckable(True); self.action_ellipse.setData("circle"); self.action_ellipse.setIconVisibleInMenu(True); self._group.addAction(self.action_ellipse)
        self.action_polygon = QAction(self._icons.get("polygon"), "多边形", self); self.action_polygon.setCheckable(True); self.action_polygon.setData("polygon"); self.action_polygon.setIconVisibleInMenu(True); self._group.addAction(self.action_polygon)
        
        # 画笔动作（使用独立图标）——本版本移除喷枪入口
        self.action_brush_pen = QAction(self._icons.get("brush_pen"), "普通画笔", self); self.action_brush_pen.setCheckable(True); self.action_brush_pen.setData("brush_pen"); self.action_brush_pen.setIconVisibleInMenu(True); self._group.addAction(self.action_brush_pen)
        self.action_brush_marker = QAction(self._icons.get("brush_marker"), "马克笔", self); self.action_brush_marker.setCheckable(True); self.action_brush_marker.setData("brush_marker"); self.action_brush_marker.setIconVisibleInMenu(True); self._group.addAction(self.action_brush_marker)
        self.action_brush_calligraphy = QAction(self._icons.get("brush_calligraphy"), "书法笔", self); self.action_brush_calligraphy.setCheckable(True); self.action_brush_calligraphy.setData("brush_calligraphy"); self.action_brush_calligraphy.setIconVisibleInMenu(True); self._group.addAction(self.action_brush_calligraphy)
        
        # 橡皮擦动作
        self.action_eraser = QAction(self._icons.get("eraser"), "橡皮擦", self); self.action_eraser.setCheckable(True); self.action_eraser.setData("eraser"); self.action_eraser.setIconVisibleInMenu(True); self._group.addAction(self.action_eraser)

        # 下拉按钮"图形"
        self.shape_button = QToolButton(self)
        self.shape_button.setText("图形")
        # 点击整个按钮直接弹出菜单
        self.shape_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.shape_menu = QMenu(self.shape_button)
        for a in (self.action_point, self.action_line, self.action_rect, self.action_ellipse, self.action_polygon):
            self.shape_menu.addAction(a)
        self.shape_button.setMenu(self.shape_menu)
        self.addWidget(self.shape_button)
        
        # 下拉按钮"画笔"
        self.brush_button = QToolButton(self)
        self.brush_button.setText("画笔")
        # 点击整个按钮直接弹出菜单
        self.brush_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.brush_menu = QMenu(self.brush_button)
        for a in (self.action_brush_pen, self.action_brush_marker, self.action_brush_calligraphy):
            self.brush_menu.addAction(a)
        self.brush_button.setMenu(self.brush_menu)
        self.addWidget(self.brush_button)
        
        # 橡皮擦按钮
        self.addAction(self.action_eraser)

        # ------- 快速笔触设置（颜色/宽度/线型） -------
        from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSpinBox, QComboBox, QLabel
        from PySide6.QtGui import QColor
        self._quick_container = QWidget(self)
        lay = QHBoxLayout(self._quick_container)
        lay.setContentsMargins(8, 2, 8, 2)
        lay.setSpacing(8)
        # 颜色
        lbl_color = QLabel("颜色"); lbl_color.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._btn_color = QPushButton("选择"); self._btn_color.setMinimumWidth(64); self._btn_color.setMinimumHeight(28)
        self._btn_color.clicked.connect(self._pick_quick_color)
        # 线宽
        lbl_width = QLabel("线宽"); lbl_width.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._spin_width = QSpinBox(); self._spin_width.setRange(1, 50); self._spin_width.setValue(2); self._spin_width.setMinimumWidth(60); self._spin_width.setMinimumHeight(28)
        self._spin_width.valueChanged.connect(lambda v: self.quickStrokeWidthChanged.emit(float(v)))
        # 线型
        lbl_dash = QLabel("线型"); lbl_dash.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._combo_dash = QComboBox(); self._combo_dash.addItems(["实线", "虚线"]); self._combo_dash.setMinimumWidth(76); self._combo_dash.setMinimumHeight(28)
        try:
            self._combo_dash.setEditable(True); le = self._combo_dash.lineEdit();
            if le is not None:
                le.setReadOnly(True); le.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            for i in range(self._combo_dash.count()):
                self._combo_dash.setItemData(i, Qt.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
        except Exception:
            pass
        self._combo_dash.currentIndexChanged.connect(self._emit_dash)
        # 默认色
        self._quick_color = QColor("#0066cc"); self._apply_color_button()
        lay.addWidget(lbl_color); lay.addWidget(self._btn_color); lay.addWidget(lbl_width); lay.addWidget(self._spin_width); lay.addWidget(lbl_dash); lay.addWidget(self._combo_dash)
        self.addWidget(self._quick_container)

        # 默认选择工具
        self.action_select.setChecked(True)

        # 当组内选中变化时发出通知
        self._group.triggered.connect(self._on_triggered)
        self.shape_menu.triggered.connect(self._on_shape_menu_triggered)
        self.brush_menu.triggered.connect(self._on_brush_menu_triggered)

    def _on_triggered(self, action: QAction) -> None:
        name = action.data() or self.current_tool()
        if name in ("point", "line", "rect", "circle", "polygon"):
            self.shape_button.setText(action.text())
            self.brush_button.setText("画笔")
        elif name.startswith("brush_"):
            self.brush_button.setText(action.text())
            self.shape_button.setText("图形")
        elif name == "eraser":
            self.shape_button.setText("图形")
            self.brush_button.setText("画笔")
        else:
            self.shape_button.setText("图形")
            self.brush_button.setText("画笔")
        self.toolChanged.emit(str(name))

    def _on_shape_menu_triggered(self, action: QAction) -> None:
        action.setChecked(True)
        self._on_triggered(action)
    
    def _on_brush_menu_triggered(self, action: QAction) -> None:
        action.setChecked(True)
        self._on_triggered(action)

    def current_tool(self) -> str:
        checked = self._group.checkedAction()
        if checked is not None and checked.data():
            return str(checked.data())
        return "select"

    # ------- 快速笔触槽 -------
    def _pick_quick_color(self) -> None:
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self._quick_color, self, "选择描边颜色")
        if color.isValid():
            self._quick_color = color
            self._apply_color_button()
            self.quickStrokeColorChanged.emit(color)

    def _apply_color_button(self) -> None:
        self._btn_color.setStyleSheet(f"background-color: {self._quick_color.name()}; padding: 2px 8px;")

    def _emit_dash(self, idx: int) -> None:
        from PySide6.QtCore import Qt as _Qt
        style = _Qt.PenStyle.SolidLine if idx == 0 else _Qt.PenStyle.DashLine
        self.quickStrokeDashChanged.emit(style)


