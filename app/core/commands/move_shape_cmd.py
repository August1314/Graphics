from __future__ import annotations

from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QGraphicsItem


class MoveShapeCommand(QUndoCommand):
    def __init__(self, item: QGraphicsItem, old_pos, new_pos, text: str = "移动图形") -> None:
        super().__init__(text)
        self._item = item
        self._old = old_pos
        self._new = new_pos

    def undo(self) -> None:  # type: ignore[override]
        self._item.setPos(self._old)

    def redo(self) -> None:  # type: ignore[override]
        self._item.setPos(self._new)

