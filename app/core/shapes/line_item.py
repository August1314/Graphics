from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QStyleOptionGraphicsItem, QWidget


class LineItem(QGraphicsLineItem):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, parent=None) -> None:
        super().__init__(x1, y1, x2, y2, parent)
        self.setPen(QPen(QColor("#333333"), 2))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        
        # 性能优化：启用缓存策略
        # 直线是静态图形，使用 ItemCoordinateCache 提升性能
        self.setCacheMode(self.CacheMode.ItemCoordinateCache)

    def set_points(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """设置直线端点
        
        性能优化：调用 prepareGeometryChange() 通知场景几何变化
        """
        self.prepareGeometryChange()
        self.setLine(x1, y1, x2, y2)

    @classmethod
    def from_dict(cls, data: dict) -> 'LineItem':
        return cls(float(data.get("x1", 0.0)), float(data.get("y1", 0.0)), float(data.get("x2", 0.0)), float(data.get("y2", 0.0)))



    def paint(self, painter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:  # type: ignore[override]
        """绘制直线，包含选择高亮
        
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
        painter.drawLine(self.line())
        
        # 选中时绘制虚线高亮
        if self.isSelected():
            sel_pen = QPen(QColor(0, 120, 215))
            sel_pen.setWidth(3)  # 稍粗一点，更明显
            try:
                sel_pen.setCosmetic(True)
            except Exception:
                pass
            sel_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.drawLine(self.line())
        
        painter.restore()
