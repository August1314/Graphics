from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QFormLayout, QPushButton, QSpinBox, QComboBox, QColorDialog, QSizePolicy

from app.core.commands.update_style_cmd import UpdateStyleCommand


class StrokeProperty(QWidget):
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self.item = item
        self.scene = scene
        self.undo_stack = undo_stack
        self.form = QFormLayout(self)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.btn_color = QPushButton("选择颜色")
        self.spin_width = QSpinBox(); self.spin_width.setRange(1, 50)
        self.combo_dash = QComboBox(); self.combo_dash.addItems(["实线", "虚线"])
        for w in (self.btn_color, self.spin_width, self.combo_dash):
            w.setMinimumWidth(140)
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.form.addRow("描边颜色", self.btn_color)
        self.form.addRow("线宽", self.spin_width)
        self.form.addRow("线型", self.combo_dash)
        self.btn_color.clicked.connect(self._pick)
        self.spin_width.valueChanged.connect(self._apply_width)
        self.combo_dash.currentIndexChanged.connect(self._apply_dash)

    def sync_from_item(self) -> None:
        p = self.item.pen()
        self.btn_color.setStyleSheet(f"background-color: {p.color().name(QColor.HexArgb)};")
        self.spin_width.blockSignals(True); self.combo_dash.blockSignals(True)
        self.spin_width.setValue(int(round(p.widthF())))
        self.combo_dash.setCurrentIndex(0 if p.style() == Qt.PenStyle.SolidLine else 1)
        self.spin_width.blockSignals(False); self.combo_dash.blockSignals(False)

    def _pick(self) -> None:
        p = self.item.pen(); old = p.color()
        color = QColorDialog.getColor(old, self, "选择描边颜色")
        if not color.isValid():
            return
        def do():
            pen = self.item.pen(); pen.setColor(color); self.item.setPen(pen); self.scene.update_base_style(self.item)
        def undo():
            pen = self.item.pen(); pen.setColor(old); self.item.setPen(pen); self.scene.update_base_style(self.item)
        self.undo_stack.push(UpdateStyleCommand.make("修改描边颜色", do, undo))
        # 不再在此处强制刷新 UI，避免撤销/重做导致属性面板重建后触发已销毁控件访问

    def _apply_width(self, v: int) -> None:
        nw = max(0.1, float(v)); old = self.item.pen().widthF()
        def do():
            pen = self.item.pen(); pen.setWidthF(nw); self.item.setPen(pen); self.scene.update_base_style(self.item)
        def undo():
            pen = self.item.pen(); pen.setWidthF(old); self.item.setPen(pen); self.scene.update_base_style(self.item)
        self.undo_stack.push(UpdateStyleCommand.make("修改线宽", do, undo))

    def _apply_dash(self, idx: int) -> None:
        from PySide6.QtCore import Qt as _Qt
        new = _Qt.PenStyle.SolidLine if idx == 0 else _Qt.PenStyle.DashLine
        old = self.item.pen().style()
        def do():
            pen = self.item.pen(); pen.setStyle(new); self.item.setPen(pen); self.scene.update_base_style(self.item)
        def undo():
            pen = self.item.pen(); pen.setStyle(old); self.item.setPen(pen); self.scene.update_base_style(self.item)
        self.undo_stack.push(UpdateStyleCommand.make("修改线型", do, undo))


