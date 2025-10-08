from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget


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



    def paint(self, painter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:  # type: ignore[override]
        """绘制点，包含选择高亮
        
        用户体验优化：选中时显示虚线边框
        """
        # 使用 cosmetic 笔，避免缩放影响
        pen = QPen(self.pen())
        try:
            pen.setCosmetic(True)
        except Exception:
            pass
        
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.setPen(pen)
        painter.setBrush(self.brush())
        painter.drawEllipse(self.rect())
        
        # 选中时绘制虚线高亮圆圈
        if self.isSelected():
            sel_pen = QPen(QColor(0, 120, 215))
            sel_pen.setWidth(2)
            try:
                sel_pen.setCosmetic(True)
            except Exception:
                pass
            sel_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # 绘制稍大的圆圈作为高亮
            highlight_rect = self.rect().adjusted(-2, -2, 2, 2)
            painter.drawEllipse(highlight_rect)
        
        painter.restore()
