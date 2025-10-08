from __future__ import annotations

from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene


class AddShapeCommand(QUndoCommand):
    """添加图形命令
    
    用户体验优化：提供清晰的命令描述，包含图形类型信息
    """
    
    def __init__(self, scene: QGraphicsScene, item: QGraphicsItem, text: str = "添加图形") -> None:
        # 用户体验优化：根据图形类型生成更具体的描述
        if text == "添加图形":
            shape_type = self._get_shape_type(item)
            text = f"添加{shape_type}"
        
        super().__init__(text)
        self._scene = scene
        self._item = item
    
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
        self._scene.removeItem(self._item)

    def redo(self) -> None:  # type: ignore[override]
        if self._item.scene() is None:
            self._scene.addItem(self._item)

