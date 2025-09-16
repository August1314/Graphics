from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsScene

from app.core.shapes.point_item import PointItem
from app.core.tools.base_tool import BaseTool


class PointTool(BaseTool):
    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if event.button().value != 1:  # 左键
            return
        p = PointItem(scene_pos.x(), scene_pos.y(), 3.0)
        scene.addItem(p)

