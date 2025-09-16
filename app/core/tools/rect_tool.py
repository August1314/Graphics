from __future__ import annotations

from typing import Optional, Callable

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsScene

from app.core.shapes.rect_item import RectItem
from app.core.tools.base_tool import BaseTool


class RectTool(BaseTool):
    def __init__(self) -> None:
        self._start: Optional[QPointF] = None
        self._draft: Optional[RectItem] = None
        self._on_committed: Optional[Callable[[RectItem], None]] = None

    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if event.button().value != 1:
            return
        self._start = scene_pos
        self._draft = RectItem(scene_pos.x(), scene_pos.y(), 1.0, 1.0)
        scene.addItem(self._draft)

    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if self._draft is None or self._start is None:
            return
        x1, y1 = self._start.x(), self._start.y()
        x2, y2 = scene_pos.x(), scene_pos.y()
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        self._draft.set_geometry(x, y, max(1.0, w), max(1.0, h))

    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if self._draft is None or self._start is None:
            return
        self.on_move(scene, scene_pos, event)
        if self._on_committed is not None:
            self._on_committed(self._draft)
        self._draft = None
        self._start = None

    def is_active(self) -> bool:
        return self._draft is not None and self._start is not None

    def on_committed(self, cb: Callable[[RectItem], None]) -> None:
        self._on_committed = cb


