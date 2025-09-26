from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsScene


class BaseTool:
    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:  # noqa: D401
        """Handle mouse press in scene coordinates."""

    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:  # noqa: D401
        """Handle mouse move in scene coordinates."""

    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:  # noqa: D401
        """Handle mouse release in scene coordinates."""

    def cancel(self, scene: QGraphicsScene) -> None:
        pass


