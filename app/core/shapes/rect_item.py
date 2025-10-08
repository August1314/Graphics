from __future__ import annotations

from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsRectItem


class RectItem(QGraphicsRectItem):
    def __init__(self, x: float, y: float, w: float, h: float, parent=None) -> None:
        super().__init__(x, y, w, h, parent)
        self.setPen(QPen(QColor("#333333"), 2))
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)

    def set_geometry(self, x: float, y: float, w: float, h: float) -> None:
        """设置矩形几何
        
        性能优化：调用 prepareGeometryChange() 通知场景几何变化
        """
        self.prepareGeometryChange()
        self.setRect(x, y, w, h)

    @classmethod
    def from_dict(cls, data: dict) -> 'RectItem':
        return cls(float(data.get("x", 0.0)), float(data.get("y", 0.0)), float(data.get("width", 0.0)), float(data.get("height", 0.0)))


