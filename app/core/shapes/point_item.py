from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsEllipseItem


class PointItem(QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, radius: float = 3.0, parent=None) -> None:
        r = max(0.5, radius)
        super().__init__(-r, -r, 2 * r, 2 * r, parent)
        self.setPos(x, y)
        self.setPen(QPen(QColor("#000000"), 1))
        self.setBrush(QBrush(QColor("#000000")))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        
        # 性能优化：启用缓存策略
        # 点是静态图形，使用 ItemCoordinateCache 提升性能
        self.setCacheMode(self.CacheMode.ItemCoordinateCache)

    @classmethod
    def from_dict(cls, data: dict) -> 'PointItem':
        return cls(float(data.get("x", 0.0)), float(data.get("y", 0.0)), float(data.get("r", 3.0)))


