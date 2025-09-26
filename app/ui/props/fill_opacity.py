from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QFormLayout, QPushButton, QSlider, QColorDialog, QSizePolicy
from PySide6.QtCore import Qt

from app.core.commands.update_style_cmd import UpdateStyleCommand


class FillAndOpacityProperty(QWidget):
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self.item = item
        self.scene = scene
        self.undo_stack = undo_stack
        self.form = QFormLayout(self)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.btn_fill = QPushButton("选择填充")
        self.slider_opacity = QSlider(Qt.Horizontal); self.slider_opacity.setRange(0, 100)
        for w in (self.btn_fill, self.slider_opacity):
            w.setMinimumWidth(140)
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.form.addRow("填充颜色", self.btn_fill)
        self.form.addRow("不透明度", self.slider_opacity)
        self.btn_fill.clicked.connect(self._pick_fill)
        self.slider_opacity.valueChanged.connect(self._apply_opacity)

    def sync_from_item(self) -> None:
        from PySide6.QtGui import QBrush
        self.btn_fill.setStyleSheet(f"background-color: {self.item.brush().color().name(QColor.HexArgb)};")
        self.slider_opacity.blockSignals(True)
        self.slider_opacity.setValue(int(round(self.item.opacity() * 100)))
        self.slider_opacity.blockSignals(False)

    def _pick_fill(self) -> None:
        from PySide6.QtGui import QBrush
        old = self.item.brush().color()
        color = QColorDialog.getColor(old, self, "选择填充颜色")
        if not color.isValid():
            return
        def do():
            self.item.setBrush(QBrush(color)); self.scene.update_base_style(self.item)
        def undo():
            self.item.setBrush(QBrush(old)); self.scene.update_base_style(self.item)
        self.undo_stack.push(UpdateStyleCommand.make("修改填充颜色", do, undo))
        self.sync_from_item()

    def _apply_opacity(self, v: int) -> None:
        old = self.item.opacity(); new = max(0.0, min(1.0, v / 100.0))
        def do():
            self.item.setOpacity(new); self.scene.update_base_style(self.item)
        def undo():
            self.item.setOpacity(old); self.scene.update_base_style(self.item)
        self.undo_stack.push(UpdateStyleCommand.make("修改不透明度", do, undo))


