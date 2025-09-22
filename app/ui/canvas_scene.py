from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsScene, QGraphicsItem


class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # 设定一个默认场景大小
        self.setSceneRect(QRectF(0, 0, 1200, 800))
        # 初始不放置任何示例图元，由用户通过工具创建

        # 选择变化监听
        self.selectionChanged.connect(self._on_selection_changed)

    # 自定义数据键保存原样式
    _DATA_BASE_COLOR = int(Qt.ItemDataRole.UserRole) + 1
    _DATA_BASE_WIDTH = int(Qt.ItemDataRole.UserRole) + 2

    def _tag_base_style(self, item: QGraphicsItem) -> None:
        pen = getattr(item, "pen", None)
        if callable(pen):
            p = item.pen()
            item.setData(self._DATA_BASE_COLOR, p.color())
            item.setData(self._DATA_BASE_WIDTH, p.widthF())

    # 公共方法：将当前样式设为基础样式
    def update_base_style(self, item: QGraphicsItem) -> None:
        self._tag_base_style(item)

    # 公共方法：根据当前选择状态，刷新高亮/还原
    def refresh_selection_styles(self) -> None:
        self._on_selection_changed()

    def _restore_style(self, item: QGraphicsItem) -> None:
        pen = getattr(item, "pen", None)
        set_pen = getattr(item, "setPen", None)
        if callable(pen) and callable(set_pen):
            base_color = item.data(self._DATA_BASE_COLOR)
            base_width = item.data(self._DATA_BASE_WIDTH)
            if base_color is not None and base_width is not None:
                p = item.pen()
                p.setColor(base_color)
                p.setWidthF(float(base_width))
                item.setPen(p)

    def _highlight_style(self, item: QGraphicsItem) -> None:
        pen = getattr(item, "pen", None)
        set_pen = getattr(item, "setPen", None)
        if callable(pen) and callable(set_pen):
            p = item.pen()
            base_color = item.data(self._DATA_BASE_COLOR) or p.color()
            base_width = float(item.data(self._DATA_BASE_WIDTH) or p.widthF())
            print(f"DEBUG: _highlight_style 被调用，基础宽度: {base_width}, 当前宽度: {p.widthF()}")
            # 加深颜色，不改变线宽，避免反复触发时越选越粗/越大
            color = QColor(base_color)
            color = color.darker(125)
            p.setColor(color)
            try:
                p.setCosmetic(True)
            except Exception:
                pass
            p.setWidthF(base_width)
            print(f"DEBUG: 设置高亮宽度为: {base_width}")
            item.setPen(p)

    def _on_selection_changed(self) -> None:
        # 遍历所有可选项，根据选中状态应用样式
        for item in self.items():
            if not (item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
                continue
            
            # 跳过 BrushPathItem，因为它自己处理高亮效果
            if item.__class__.__name__ == "BrushPathItem":
                continue
                
            # 每次选中时，以当前样式为基础样式
            if item.isSelected():
                self._tag_base_style(item)
                self._highlight_style(item)
            else:
                self._restore_style(item)


