from __future__ import annotations

from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene


class AddShapeCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, item: QGraphicsItem, text: str = "添加图形") -> None:
        super().__init__(text)
        self._scene = scene
        self._item = item

    def undo(self) -> None:  # type: ignore[override]
        self._scene.removeItem(self._item)

    def redo(self) -> None:  # type: ignore[override]
        if self._item.scene() is None:
            self._scene.addItem(self._item)

