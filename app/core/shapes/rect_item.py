from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget


class RectItem(QGraphicsRectItem):
    def __init__(self, x: float, y: float, w: float, h: float, parent=None) -> None:
        super().__init__(x, y, w, h, parent)
        self.setPen(QPen(QColor("#333333"), 2))
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        
        # 性能优化：启用缓存策略
        # 矩形是静态图形，使用 ItemCoordinateCache 提升性能
        self.setCacheMode(self.CacheMode.ItemCoordinateCache)

    def set_geometry(self, x: float, y: float, w: float, h: float) -> None:
        """设置矩形几何
        
        性能优化：调用 prepareGeometryChange() 通知场景几何变化
        """
        self.prepareGeometryChange()
        self.setRect(x, y, w, h)

    @classmethod
    def from_dict(cls, data: dict) -> 'RectItem':
        return cls(float(data.get("x", 0.0)), float(data.get("y", 0.0)), float(data.get("width", 0.0)), float(data.get("height", 0.0)))



    def paint(self, painter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:  # type: ignore[override]
        """绘制矩形，包含选择高亮
        
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
        painter.drawRect(self.rect())
        
        # 选中时绘制虚线高亮
        if self.isSelected():
            sel_pen = QPen(QColor(0, 120, 215))
            sel_pen.setWidth(1)
            try:
                sel_pen.setCosmetic(True)
            except Exception:
                pass
            sel_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # 绘制稍大的边框作为高亮
            highlight_rect = self.rect().adjusted(-2, -2, 2, 2)
            painter.drawRect(highlight_rect)
        
        painter.restore()
