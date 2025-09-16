from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsScene

from app.core.shapes.line_item import LineItem
from app.core.tools.base_tool import BaseTool


class LineTool(BaseTool):
    def __init__(self) -> None:
        self._draft: Optional[LineItem] = None
        self._start: Optional[QPointF] = None

    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if event.button().value != 1:
            return
        self._start = scene_pos
        self._draft = LineItem(scene_pos.x(), scene_pos.y(), scene_pos.x(), scene_pos.y())
        scene.addItem(self._draft)

    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if self._draft is None or self._start is None:
            return
        self._draft.set_points(self._start.x(), self._start.y(), scene_pos.x(), scene_pos.y())

    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if self._draft is None or self._start is None:
            return
        self._draft.set_points(self._start.x(), self._start.y(), scene_pos.x(), scene_pos.y())
        self._draft = None
        self._start = None

    def is_active(self) -> bool:
        return self._draft is not None and self._start is not None

