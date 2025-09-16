from __future__ import annotations

from PySide6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSizePolicy

from app.core.commands.update_style_cmd import UpdateStyleCommand


class LineEndpointsProperty(QWidget):
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self.item = item
        self.scene = scene
        self.undo_stack = undo_stack
        self.form = QFormLayout(self)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.x1 = QDoubleSpinBox(); self.x1.setRange(-1e6, 1e6); self.x1.setDecimals(1)
        self.y1 = QDoubleSpinBox(); self.y1.setRange(-1e6, 1e6); self.y1.setDecimals(1)
        self.x2 = QDoubleSpinBox(); self.x2.setRange(-1e6, 1e6); self.x2.setDecimals(1)
        self.y2 = QDoubleSpinBox(); self.y2.setRange(-1e6, 1e6); self.y2.setDecimals(1)
        for w in (self.x1, self.y1, self.x2, self.y2):
            w.setMinimumWidth(140)
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.form.addRow("起点X", self.x1)
        self.form.addRow("起点Y", self.y1)
        self.form.addRow("终点X", self.x2)
        self.form.addRow("终点Y", self.y2)
        for s in (self.x1, self.y1, self.x2, self.y2):
            s.valueChanged.connect(self._apply)

    def sync_from_item(self) -> None:
        ln = self.item.line()
        for s, v in ((self.x1, ln.x1()), (self.y1, ln.y1()), (self.x2, ln.x2()), (self.y2, ln.y2())):
            s.blockSignals(True); s.setValue(v); s.blockSignals(False)

    def _apply(self) -> None:
        ln = self.item.line(); old = (ln.x1(), ln.y1(), ln.x2(), ln.y2())
        x1, y1, x2, y2 = self.x1.value(), self.y1.value(), self.x2.value(), self.y2.value()
        def do():
            self.item.set_points(x1, y1, x2, y2); self.scene.update_base_style(self.item)
        def undo():
            self.item.set_points(old[0], old[1], old[2], old[3]); self.scene.update_base_style(self.item)
        self.undo_stack.push(UpdateStyleCommand.make("修改直线端点", do, undo))


