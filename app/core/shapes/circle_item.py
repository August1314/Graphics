from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem


class CircleItem(QGraphicsEllipseItem):
    def __init__(self, cx: float, cy: float, r: float, parent=None) -> None:
        super().__init__(-r, -r, 2 * r, 2 * r, parent)
        self.setPos(cx, cy)
        self.setPen(QPen(QColor("#0066cc"), 2))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)

    def set_center_radius(self, cx: float, cy: float, r: float) -> None:
        self.setPos(cx, cy)
        self.setRect(-r, -r, 2 * r, 2 * r)

    def center_radius(self) -> tuple[float, float, float]:
        rect: QRectF = self.rect()
        r = rect.width() / 2.0
        pos = self.pos()
        return (pos.x(), pos.y(), r)


