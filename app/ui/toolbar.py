from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QToolBar, QToolButton, QMenu
from PySide6.QtGui import QIcon
from app.ui.icon_provider import IconProvider


class ToolBar(QToolBar):
    toolChanged = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__("工具", parent)
        self.setMovable(True)
        self.setFloatable(True)
        self._icons = IconProvider("light")

        self._group = QActionGroup(self)
        self._group.setExclusive(True)

        # 工具动作：选择
        self.action_select = QAction(self._icons.get("select"), "选择", self)
        self.action_select.setCheckable(True)
        self.action_select.setData("select")
        self._group.addAction(self.action_select)
        self.addAction(self.action_select)

        # 形状动作
        self.action_point = QAction(self._icons.get("point"), "点", self); self.action_point.setCheckable(True); self.action_point.setData("point"); self._group.addAction(self.action_point)
        self.action_line = QAction(self._icons.get("line"), "直线", self); self.action_line.setCheckable(True); self.action_line.setData("line"); self._group.addAction(self.action_line)
        self.action_rect = QAction(self._icons.get("rect"), "矩形", self); self.action_rect.setCheckable(True); self.action_rect.setData("rect"); self._group.addAction(self.action_rect)
        self.action_ellipse = QAction(self._icons.get("circle"), "圆", self); self.action_ellipse.setCheckable(True); self.action_ellipse.setData("circle"); self._group.addAction(self.action_ellipse)
        self.action_polygon = QAction(self._icons.get("polygon"), "多边形", self); self.action_polygon.setCheckable(True); self.action_polygon.setData("polygon"); self._group.addAction(self.action_polygon)
        
        # 画笔动作
        self.action_brush_pen = QAction(self._icons.get("brush"), "普通画笔", self); self.action_brush_pen.setCheckable(True); self.action_brush_pen.setData("brush_pen"); self._group.addAction(self.action_brush_pen)
        self.action_brush_marker = QAction(self._icons.get("brush"), "马克笔", self); self.action_brush_marker.setCheckable(True); self.action_brush_marker.setData("brush_marker"); self._group.addAction(self.action_brush_marker)
        self.action_brush_calligraphy = QAction(self._icons.get("brush"), "书法笔", self); self.action_brush_calligraphy.setCheckable(True); self.action_brush_calligraphy.setData("brush_calligraphy"); self._group.addAction(self.action_brush_calligraphy)
        self.action_brush_spray = QAction(self._icons.get("brush"), "喷枪", self); self.action_brush_spray.setCheckable(True); self.action_brush_spray.setData("brush_spray"); self._group.addAction(self.action_brush_spray)
        
        # 橡皮擦动作
        self.action_eraser = QAction(self._icons.get("eraser"), "橡皮擦", self); self.action_eraser.setCheckable(True); self.action_eraser.setData("eraser"); self._group.addAction(self.action_eraser)

        # 下拉按钮“图形”
        self.shape_button = QToolButton(self)
        self.shape_button.setText("图形")
        self.shape_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.shape_menu = QMenu(self.shape_button)
        for a in (self.action_point, self.action_line, self.action_rect, self.action_ellipse, self.action_polygon):
            self.shape_menu.addAction(a)
        self.shape_button.setMenu(self.shape_menu)
        self.addWidget(self.shape_button)
        
        # 下拉按钮"画笔"
        self.brush_button = QToolButton(self)
        self.brush_button.setText("画笔")
        self.brush_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.brush_menu = QMenu(self.brush_button)
        for a in (self.action_brush_pen, self.action_brush_marker, self.action_brush_calligraphy, 
                  self.action_brush_spray):
            self.brush_menu.addAction(a)
        self.brush_button.setMenu(self.brush_menu)
        self.addWidget(self.brush_button)
        
        # 橡皮擦按钮
        self.addAction(self.action_eraser)

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


