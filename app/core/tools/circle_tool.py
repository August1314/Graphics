from __future__ import annotations

from typing import Optional, Callable

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsScene

from app.core.shapes.circle_item import CircleItem
from app.core.tools.base_tool import BaseTool


class CircleTool(BaseTool):
    def __init__(self) -> None:
        self._draft: Optional[CircleItem] = None
        self._center: Optional[QPointF] = None
        self._on_committed: Optional[Callable[[CircleItem], None]] = None

    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:  # 左键
            return
        self._center = scene_pos
        self._draft = CircleItem(scene_pos.x(), scene_pos.y(), 1.0)
        self._draft.setOpacity(0.7)
        scene.addItem(self._draft)

    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if not self._draft or not self._center:
            return
        r = ((scene_pos.x() - self._center.x()) ** 2 + (scene_pos.y() - self._center.y()) ** 2) ** 0.5
        self._draft.set_center_radius(self._center.x(), self._center.y(), max(1.0, r))

    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if not self._draft or not self._center:
            self.cancel(scene)
            return
        r = ((scene_pos.x() - self._center.x()) ** 2 + (scene_pos.y() - self._center.y()) ** 2) ** 0.5
        self._draft.setOpacity(1.0)
        self._draft.set_center_radius(self._center.x(), self._center.y(), max(1.0, r))
        if self._on_committed is not None:
            self._on_committed(self._draft)
        self._draft = None
        self._center = None

    def cancel(self, scene: QGraphicsScene) -> None:
        if self._draft is not None:
            scene.removeItem(self._draft)
        self._draft = None
        self._center = None

    def is_active(self) -> bool:
        return self._draft is not None and self._center is not None

    def on_committed(self, callback: Callable[[CircleItem], None]) -> None:
        self._on_committed = callback


