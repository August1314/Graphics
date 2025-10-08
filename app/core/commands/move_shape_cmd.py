from __future__ import annotations

from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QGraphicsItem


class MoveShapeCommand(QUndoCommand):
    """移动图形命令
    
    用户体验优化：提供清晰的命令描述，包含图形类型和位置信息
    """
    
    def __init__(self, item: QGraphicsItem, old_pos, new_pos, text: str = "移动图形") -> None:
        # 用户体验优化：根据图形类型生成更具体的描述
        if text == "移动图形":
            shape_type = self._get_shape_type(item)
            # 计算移动距离
            import math
            dx = new_pos.x() - old_pos.x()
            dy = new_pos.y() - old_pos.y()
            distance = math.sqrt(dx*dx + dy*dy)
            text = f"移动{shape_type} ({distance:.0f}px)"
        
        super().__init__(text)
        self._item = item
        self._old = old_pos
        self._new = new_pos
    
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
        self._item.setPos(self._old)

    def redo(self) -> None:  # type: ignore[override]
        self._item.setPos(self._new)

