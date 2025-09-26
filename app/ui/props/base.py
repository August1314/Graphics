from __future__ import annotations

from typing import Protocol, Any


class PropertyComponent(Protocol):
    """属性组件协议：未来用于真正的独立控件。当前阶段仅用于装配占位。"""

    def key(self) -> str:  # 唯一键
        ...

    def mount(self, panel: Any) -> None:  # 将组件挂载到现有 PropertyPanel（可复用内置控件）
        ...

    def unmount(self, panel: Any) -> None:
        ...

    def sync_from_item(self, item: Any) -> None:
        ...


