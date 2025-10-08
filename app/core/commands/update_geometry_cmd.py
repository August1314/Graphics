from __future__ import annotations

from PySide6.QtGui import QUndoCommand, QPainterPath, QPen, QBrush
from PySide6.QtWidgets import QGraphicsItem


class UpdateGeometryCommand(QUndoCommand):
    """通用几何更新命令：用于擦除等对图元路径与样式的修改可撤销/重做
    
    用户体验优化：提供清晰的命令描述，包含图形类型信息
    """

    def __init__(
        self,
        item: QGraphicsItem,
        old_path: QPainterPath,
        new_path: QPainterPath,
        old_pen: QPen,
        new_pen: QPen,
        old_brush: QBrush,
        new_brush: QBrush,
        text: str = "更新几何",
    ) -> None:
        # 用户体验优化：根据图形类型生成更具体的描述
        if text == "更新几何":
            shape_type = self._get_shape_type(item)
            text = f"修改{shape_type}几何"
        
        super().__init__(text)
        self._item = item
        self._old_path = QPainterPath(old_path)
        self._new_path = QPainterPath(new_path)
        self._old_pen = QPen(old_pen)
        self._new_pen = QPen(new_pen)
        self._old_brush = QBrush(old_brush)
        self._new_brush = QBrush(new_brush)
    
    @staticmethod
    def _get_shape_type(item: QGraphicsItem) -> str:
        """获取图形类型的中文名称"""
        class_name = type(item).__name__
        type_map = {
            'CircleItem': '圆形',
            'RectItem': '矩形',
            'LineItem': '直线',
            'PointItem': '点',
            'PolygonItem': '多边形',
            'BrushPathItem': '画笔路径',
        }
        return type_map.get(class_name, '图形')

    def undo(self) -> None:  # type: ignore[override]
        # 还原路径与样式
        try:
            self._item.setPath(self._old_path)
            if hasattr(self._item, "setPen"):
                self._item.setPen(self._old_pen)
            if hasattr(self._item, "setBrush"):
                self._item.setBrush(self._old_brush)
        except Exception:
            pass

    def redo(self) -> None:  # type: ignore[override]
        # 应用新路径与样式
        try:
            self._item.setPath(self._new_path)
            if hasattr(self._item, "setPen"):
                self._item.setPen(self._new_pen)
            if hasattr(self._item, "setBrush"):
                self._item.setBrush(self._new_brush)
        except Exception:
            pass


