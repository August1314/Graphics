from __future__ import annotations

from PySide6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSizePolicy

from app.core.commands.update_style_cmd import UpdateStyleCommand


class RadiusProperty(QWidget):
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self.item = item
        self.scene = scene
        self.undo_stack = undo_stack
        self.form = QFormLayout(self)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.spin_r = QDoubleSpinBox(); self.spin_r.setRange(0.0, 1e6); self.spin_r.setDecimals(1)
        self.spin_r.setMinimumWidth(140)
        self.spin_r.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.form.addRow("半径", self.spin_r)
        self.spin_r.valueChanged.connect(self._apply)

    def sync_from_item(self) -> None:
        from app.core.shapes.circle_item import CircleItem
        from app.core.shapes.point_item import PointItem
        self.spin_r.blockSignals(True)
        if isinstance(self.item, CircleItem):
            _, _, r = self.item.center_radius()
        elif isinstance(self.item, PointItem):
            rect = self.item.rect(); r = rect.width() / 2.0
        else:
            r = 0.0
        self.spin_r.setValue(r)
        self.spin_r.blockSignals(False)

    def _apply(self) -> None:
        from app.core.shapes.circle_item import CircleItem
        from app.core.shapes.point_item import PointItem
        nr = max(0.1, float(self.spin_r.value()))
        if isinstance(self.item, CircleItem):
            cx, cy, old_r = self.item.center_radius()
            def do():
                self.item.set_center_radius(cx, cy, nr); self.scene.update_base_style(self.item)
            def undo():
                self.item.set_center_radius(cx, cy, old_r); self.scene.update_base_style(self.item)
            self.undo_stack.push(UpdateStyleCommand.make("修改半径", do, undo))
        elif isinstance(self.item, PointItem):
            rect = self.item.rect(); old_r = rect.width() / 2.0
            def do():
                self.item.setRect(-nr, -nr, 2*nr, 2*nr); self.scene.update_base_style(self.item)
            def undo():
                self.item.setRect(-old_r, -old_r, 2*old_r, 2*old_r); self.scene.update_base_style(self.item)
            self.undo_stack.push(UpdateStyleCommand.make("修改点半径", do, undo))


