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
        self.setLine(x1, y1, x2, y2)


