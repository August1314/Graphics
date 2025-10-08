from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget


class CircleItem(QGraphicsEllipseItem):
    def __init__(self, cx: float, cy: float, r: float, parent=None) -> None:
        super().__init__(-r, -r, 2 * r, 2 * r, parent)
        self.setPos(cx, cy)
        self.setPen(QPen(QColor("#0066cc"), 2))
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)

    def set_center_radius(self, cx: float, cy: float, r: float) -> None:
        """设置圆心和半径
        
        性能优化：调用 prepareGeometryChange() 通知场景几何变化
        """
        self.prepareGeometryChange()
        self.setPos(cx, cy)
        self.setRect(-r, -r, 2 * r, 2 * r)

    def center_radius(self) -> tuple[float, float, float]:
        rect: QRectF = self.rect()
        r = rect.width() / 2.0
        pos = self.pos()
        return (pos.x(), pos.y(), r)

    @classmethod
    def from_dict(cls, data: dict) -> 'CircleItem':
        cx = float(data.get("cx", 0.0))
        cy = float(data.get("cy", 0.0))
        r = float(data.get("r", 0.0))
        return cls(cx, cy, r)

    def paint(self, painter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:  # type: ignore[override]
        # 使用 cosmetic 笔，避免选中状态或缩放导致视觉变粗
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
        # 选中时绘制1px虚线高亮，不影响线宽
        if self.isSelected():
            sel = QPen(QColor(0, 120, 215))
            sel.setWidth(1)
            try:
                sel.setCosmetic(True)
            except Exception:
                pass
            sel.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(sel)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())
        painter.restore()


