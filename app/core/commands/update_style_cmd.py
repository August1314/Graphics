from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtGui import QUndoCommand


@dataclass
class _Setter:
    do: Callable[[], None]
    undo: Callable[[], None]


class UpdateStyleCommand(QUndoCommand):
    def __init__(self, text: str, setter: _Setter) -> None:
        super().__init__(text)
        self._setter = setter

    def undo(self) -> None:  # type: ignore[override]
        self._setter.undo()

    def redo(self) -> None:  # type: ignore[override]
        self._setter.do()

    @staticmethod
    def make(text: str, apply_fn: Callable[[], None], revert_fn: Callable[[], None]) -> "UpdateStyleCommand":
        return UpdateStyleCommand(text, _Setter(do=apply_fn, undo=revert_fn))

