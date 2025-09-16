from __future__ import annotations

from PySide6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSizePolicy

from app.core.commands.update_style_cmd import UpdateStyleCommand


class CenterProperty(QWidget):
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self.item = item
        self.scene = scene
        self.undo_stack = undo_stack
        self.form = QFormLayout(self)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.spin_x = QDoubleSpinBox(); self.spin_x.setRange(-1e6, 1e6); self.spin_x.setDecimals(1)
        self.spin_y = QDoubleSpinBox(); self.spin_y.setRange(-1e6, 1e6); self.spin_y.setDecimals(1)
        for w in (self.spin_x, self.spin_y):
            w.setMinimumWidth(140)
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.form.addRow("中心X", self.spin_x)
        self.form.addRow("中心Y", self.spin_y)
        self.spin_x.valueChanged.connect(self._apply)
        self.spin_y.valueChanged.connect(self._apply)

    def sync_from_item(self) -> None:
        from app.core.shapes.circle_item import CircleItem
        from app.core.shapes.point_item import PointItem
        self.spin_x.blockSignals(True)
        self.spin_y.blockSignals(True)
        if isinstance(self.item, CircleItem):
            cx, cy, _ = self.item.center_radius()
        elif isinstance(self.item, PointItem):
            pos = self.item.pos(); cx, cy = pos.x(), pos.y()
        else:
            cx = cy = 0.0
        self.spin_x.setValue(cx)
        self.spin_y.setValue(cy)
        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(False)

    def _apply(self) -> None:
        from app.core.shapes.circle_item import CircleItem
        from app.core.shapes.point_item import PointItem
        cx = self.spin_x.value(); cy = self.spin_y.value()
        if isinstance(self.item, CircleItem):
            ox, oy, r = self.item.center_radius()
            def do():
                self.item.set_center_radius(cx, cy, r); self.scene.update_base_style(self.item)
            def undo():
                self.item.set_center_radius(ox, oy, r); self.scene.update_base_style(self.item)
            self.undo_stack.push(UpdateStyleCommand.make("修改中心", do, undo))
        elif isinstance(self.item, PointItem):
            pos = self.item.pos(); ox, oy = pos.x(), pos.y()
            def do():
                self.item.setPos(cx, cy); self.scene.update_base_style(self.item)
            def undo():
                self.item.setPos(ox, oy); self.scene.update_base_style(self.item)
            self.undo_stack.push(UpdateStyleCommand.make("移动点", do, undo))


