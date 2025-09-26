from __future__ import annotations

from typing import List, Optional, Callable

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsScene

from app.core.shapes.polygon_item import PolygonItem
from app.core.tools.base_tool import BaseTool


class PolygonTool(BaseTool):
    def __init__(self) -> None:
        self._points: List[QPointF] = []
        self._draft: Optional[PolygonItem] = None
        self._on_committed: Optional[Callable[[PolygonItem], None]] = None

    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if event.button().value != 1:
            return
        self._points.append(scene_pos)
        if self._draft is None:
            self._draft = PolygonItem([scene_pos])
            scene.addItem(self._draft)
        else:
            pts = list(self._points)
            self._draft.set_polygon(pts)

    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if self._draft is None or not self._points:
            return
        pts = list(self._points) + [scene_pos]
        self._draft.set_polygon(pts)

    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        # 单击松开不做额外处理
        return

    def cancel(self, scene: QGraphicsScene) -> None:
        if self._draft is not None:
            scene.removeItem(self._draft)
        self._draft = None
        self._points = []

    def double_click(self, scene: QGraphicsScene) -> None:
        if self._draft is not None and len(self._points) >= 3:
            if self._on_committed is not None:
                self._on_committed(self._draft)
        else:
            if self._draft is not None:
                scene.removeItem(self._draft)
        self._draft = None
        self._points = []

    def is_active(self) -> bool:
        return self._draft is not None and len(self._points) > 0

    def on_committed(self, cb: Callable[[PolygonItem], None]) -> None:
        self._on_committed = cb


