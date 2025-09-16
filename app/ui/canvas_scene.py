from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsScene, QGraphicsItem


class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # 设定一个默认场景大小
        self.setSceneRect(QRectF(0, 0, 1200, 800))
        # 放置两个示例图元，验证渲染与交互
        rect = QGraphicsRectItem(100, 120, 200, 100)
        rect.setPen(QPen(QColor("#00AA00"), 3))
        rect.setBrush(QBrush(QColor("#FF0000")))
        rect.setFlags(rect.flags() | rect.GraphicsItemFlag.ItemIsMovable | rect.GraphicsItemFlag.ItemIsSelectable)
        self._tag_base_style(rect)
        self.addItem(rect)

        circle = QGraphicsEllipseItem(400, 200, 120, 120)
        circle.setPen(QPen(QColor("#0066cc"), 2))
        circle.setBrush(QBrush(QColor(255, 255, 255, 0)))
        circle.setFlags(circle.flags() | circle.GraphicsItemFlag.ItemIsMovable | circle.GraphicsItemFlag.ItemIsSelectable)
        self._tag_base_style(circle)
        self.addItem(circle)

        # 选择变化监听
        self.selectionChanged.connect(self._on_selection_changed)

    # 自定义数据键保存原样式
    _DATA_BASE_COLOR = int(Qt.ItemDataRole.UserRole) + 1
    _DATA_BASE_WIDTH = int(Qt.ItemDataRole.UserRole) + 2

    def _tag_base_style(self, item: QGraphicsItem) -> None:
        pen = getattr(item, "pen", None)
        if callable(pen):
            p = item.pen()
            item.setData(self._DATA_BASE_COLOR, p.color())
            item.setData(self._DATA_BASE_WIDTH, p.widthF())

    # 公共方法：将当前样式设为基础样式
    def update_base_style(self, item: QGraphicsItem) -> None:
        self._tag_base_style(item)

    # 公共方法：根据当前选择状态，刷新高亮/还原
    def refresh_selection_styles(self) -> None:
        self._on_selection_changed()

    def _restore_style(self, item: QGraphicsItem) -> None:
        pen = getattr(item, "pen", None)
        set_pen = getattr(item, "setPen", None)
        if callable(pen) and callable(set_pen):
            base_color = item.data(self._DATA_BASE_COLOR)
            base_width = item.data(self._DATA_BASE_WIDTH)
            if base_color is not None and base_width is not None:
                p = item.pen()
                p.setColor(base_color)
                p.setWidthF(float(base_width))
                item.setPen(p)

    def _highlight_style(self, item: QGraphicsItem) -> None:
        pen = getattr(item, "pen", None)
        set_pen = getattr(item, "setPen", None)
        if callable(pen) and callable(set_pen):
            p = item.pen()
            base_color = item.data(self._DATA_BASE_COLOR) or p.color()
            base_width = float(item.data(self._DATA_BASE_WIDTH) or p.widthF())
            # 加深颜色与加粗
            color = QColor(base_color)
            color = color.darker(125)
            p.setColor(color)
            p.setWidthF(max(base_width * 1.5, base_width + 1.0))
            item.setPen(p)

    def _on_selection_changed(self) -> None:
        # 遍历所有可选项，根据选中状态应用样式
        for item in self.items():
            if not (item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
                continue
            # 每次选中时，以当前样式为基础样式
            if item.isSelected():
                self._tag_base_style(item)
                self._highlight_style(item)
            else:
                self._restore_style(item)


