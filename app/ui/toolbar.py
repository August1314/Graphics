from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QToolBar


class ToolBar(QToolBar):
    toolChanged = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__("工具", parent)
        self.setMovable(True)
        self.setFloatable(True)

        self._group = QActionGroup(self)
        self._group.setExclusive(True)

        # 工具动作（框架占位）
        self.action_select = QAction("选择", self)
        self.action_point = QAction("点", self)
        self.action_line = QAction("直线", self)
        self.action_rect = QAction("矩形", self)
        self.action_ellipse = QAction("圆", self)
        self.action_polygon = QAction("多边形", self)

        for act, name in (
            (self.action_select, "select"),
            (self.action_point, "point"),
            (self.action_line, "line"),
            (self.action_rect, "rect"),
            (self.action_ellipse, "ellipse"),
            (self.action_polygon, "polygon"),
        ):
            act.setCheckable(True)
            act.setData(name)
            self._group.addAction(act)
            self.addAction(act)

        # 默认选择工具
        self.action_select.setChecked(True)

        # 当组内选中变化时发出通知
        self._group.triggered.connect(self._on_triggered)

    def _on_triggered(self, action: QAction) -> None:
        name = action.data() or self.current_tool()
        self.toolChanged.emit(str(name))

    def current_tool(self) -> str:
        checked = self._group.checkedAction()
        if checked is not None and checked.data():
            return str(checked.data())
        return "select"


