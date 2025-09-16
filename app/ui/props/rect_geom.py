from __future__ import annotations

from PySide6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSizePolicy

from app.core.commands.update_style_cmd import UpdateStyleCommand


class RectGeomProperty(QWidget):
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self.item = item
        self.scene = scene
        self.undo_stack = undo_stack
        self.form = QFormLayout(self)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.x = QDoubleSpinBox(); self.x.setRange(-1e6, 1e6); self.x.setDecimals(1)
        self.y = QDoubleSpinBox(); self.y.setRange(-1e6, 1e6); self.y.setDecimals(1)
        self.w = QDoubleSpinBox(); self.w.setRange(0.0, 1e6); self.w.setDecimals(1)
        self.h = QDoubleSpinBox(); self.h.setRange(0.0, 1e6); self.h.setDecimals(1)
        for s in (self.x, self.y, self.w, self.h):
            s.setMinimumWidth(140)
            s.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            s.valueChanged.connect(self._apply)
        self.form.addRow("X", self.x)
        self.form.addRow("Y", self.y)
        self.form.addRow("宽度", self.w)
        self.form.addRow("高度", self.h)

    def sync_from_item(self) -> None:
        r = self.item.rect()
        vals = (r.x(), r.y(), r.width(), r.height())
        for s, v in zip((self.x, self.y, self.w, self.h), vals):
            s.blockSignals(True); s.setValue(v); s.blockSignals(False)

    def _apply(self) -> None:
        r = self.item.rect()
        old = (r.x(), r.y(), r.width(), r.height())
        x, y, w, h = self.x.value(), self.y.value(), max(0.1, self.w.value()), max(0.1, self.h.value())
        def do():
            self.item.set_geometry(x, y, w, h); self.scene.update_base_style(self.item)
        def undo():
            self.item.set_geometry(old[0], old[1], old[2], old[3]); self.scene.update_base_style(self.item)
        self.undo_stack.push(UpdateStyleCommand.make("修改矩形几何", do, undo))


