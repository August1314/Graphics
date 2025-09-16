from __future__ import annotations

from typing import Optional, Callable

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsScene

from app.core.shapes.point_item import PointItem
from app.core.tools.base_tool import BaseTool


class PointTool(BaseTool):
    def __init__(self) -> None:
        self._on_committed: Optional[Callable[[PointItem], None]] = None

    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if event.button().value != 1:  # 左键
            return
        p = PointItem(scene_pos.x(), scene_pos.y(), 3.0)
        scene.addItem(p)
        if self._on_committed is not None:
            self._on_committed(p)

    def on_committed(self, cb: Callable[[PointItem], None]) -> None:
        self._on_committed = cb

