from __future__ import annotations

from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsLineItem


class LineItem(QGraphicsLineItem):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, parent=None) -> None:
        super().__init__(x1, y1, x2, y2, parent)
        self.setPen(QPen(QColor("#333333"), 2))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)

    def set_points(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """设置直线端点
        
        性能优化：调用 prepareGeometryChange() 通知场景几何变化
        """
        self.prepareGeometryChange()
        self.setLine(x1, y1, x2, y2)

    @classmethod
    def from_dict(cls, data: dict) -> 'LineItem':
        return cls(float(data.get("x1", 0.0)), float(data.get("y1", 0.0)), float(data.get("x2", 0.0)), float(data.get("y2", 0.0)))


