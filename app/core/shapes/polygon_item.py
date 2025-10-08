from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QPolygonF
from PySide6.QtWidgets import QGraphicsPolygonItem


class PolygonItem(QGraphicsPolygonItem):
    def __init__(self, points: list[QPointF] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setPen(QPen(QColor("#333333"), 2))
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        if points:
            self.set_polygon(points)

    def set_polygon(self, points: list[QPointF]) -> None:
        """设置多边形顶点
        
        性能优化：调用 prepareGeometryChange() 通知场景几何变化
        """
        self.prepareGeometryChange()
        self.setPolygon(QPolygonF(points))

    @classmethod
    def from_dict(cls, data: dict) -> 'PolygonItem':
        pts = [QPointF(float(x), float(y)) for x, y in data.get("points", [])]
        it = cls()
        if pts:
            it.set_polygon(pts)
        return it


