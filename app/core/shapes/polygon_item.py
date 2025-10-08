from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPen, QBrush, QPolygonF
from PySide6.QtWidgets import QGraphicsPolygonItem, QStyleOptionGraphicsItem, QWidget


class PolygonItem(QGraphicsPolygonItem):
    def __init__(self, points: list[QPointF] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setPen(QPen(QColor("#333333"), 2))
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        
        # 性能优化：启用缓存策略
        # 多边形是静态图形，使用 ItemCoordinateCache 提升性能
        self.setCacheMode(self.CacheMode.ItemCoordinateCache)
        
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



    def paint(self, painter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:  # type: ignore[override]
        """绘制多边形，包含选择高亮
        
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
        painter.drawPolygon(self.polygon())
        
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
            painter.drawRect(self.boundingRect())
        
        painter.restore()
