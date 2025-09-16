from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QColorDialog,
    QPushButton,
    QSpinBox,
    QComboBox,
    QSlider,
    QDoubleSpinBox,
)


class PropertyPanel(QWidget):
    centerChanged = Signal(float, float)
    radiusChanged = Signal(float)
    strokeColorChanged = Signal(QColor)
    strokeWidthChanged = Signal(int)
    fillColorChanged = Signal(QColor)
    opacityChanged = Signal(int)
    # 直线
    lineP1Changed = Signal(float, float)
    lineP2Changed = Signal(float, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QFormLayout(self)

        # 中心坐标
        self.spin_cx = QDoubleSpinBox()
        self.spin_cx.setRange(-1e6, 1e6)
        self.spin_cx.setDecimals(1)
        self.spin_cx.valueChanged.connect(lambda v: self.centerChanged.emit(v, self.spin_cy.value()))
        layout.addRow("中心X", self.spin_cx)

        self.spin_cy = QDoubleSpinBox()
        self.spin_cy.setRange(-1e6, 1e6)
        self.spin_cy.setDecimals(1)
        self.spin_cy.valueChanged.connect(lambda v: self.centerChanged.emit(self.spin_cx.value(), v))
        layout.addRow("中心Y", self.spin_cy)

        # 半径
        self.spin_r = QDoubleSpinBox()
        self.spin_r.setRange(0.0, 1e6)
        self.spin_r.setDecimals(1)
        self.spin_r.valueChanged.connect(lambda v: self.radiusChanged.emit(float(v)))
        layout.addRow("半径", self.spin_r)

        # 直线端点
        self.spin_x1 = QDoubleSpinBox(); self.spin_x1.setRange(-1e6, 1e6); self.spin_x1.setDecimals(1)
        self.spin_y1 = QDoubleSpinBox(); self.spin_y1.setRange(-1e6, 1e6); self.spin_y1.setDecimals(1)
        self.spin_x2 = QDoubleSpinBox(); self.spin_x2.setRange(-1e6, 1e6); self.spin_x2.setDecimals(1)
        self.spin_y2 = QDoubleSpinBox(); self.spin_y2.setRange(-1e6, 1e6); self.spin_y2.setDecimals(1)
        self.spin_x1.valueChanged.connect(lambda v: self.lineP1Changed.emit(v, self.spin_y1.value()))
        self.spin_y1.valueChanged.connect(lambda v: self.lineP1Changed.emit(self.spin_x1.value(), v))
        self.spin_x2.valueChanged.connect(lambda v: self.lineP2Changed.emit(v, self.spin_y2.value()))
        self.spin_y2.valueChanged.connect(lambda v: self.lineP2Changed.emit(self.spin_x2.value(), v))
        layout.addRow("起点X", self.spin_x1)
        layout.addRow("起点Y", self.spin_y1)
        layout.addRow("终点X", self.spin_x2)
        layout.addRow("终点Y", self.spin_y2)

        # 描边颜色
        self.btn_stroke = QPushButton("选择颜色")
        self.btn_stroke.clicked.connect(self._pick_stroke)
        layout.addRow("描边颜色", self.btn_stroke)

        # 线宽
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1, 50)
        self.spin_width.setValue(3)
        self.spin_width.valueChanged.connect(lambda v: self.strokeWidthChanged.emit(int(v)))
        layout.addRow("线宽", self.spin_width)

        # 线型
        self.combo_dash = QComboBox()
        self.combo_dash.addItems(["实线", "虚线"])
        layout.addRow("线型", self.combo_dash)

        # 填充颜色
        self.btn_fill = QPushButton("选择填充")
        self.btn_fill.clicked.connect(self._pick_fill)
        layout.addRow("填充颜色", self.btn_fill)

        # 填充透明度
        self.slider_opacity = QSlider(Qt.Horizontal)
        self.slider_opacity.setRange(0, 100)
        self.slider_opacity.setValue(100)
        self.slider_opacity.valueChanged.connect(lambda v: self.opacityChanged.emit(int(v)))
        layout.addRow("不透明度", self.slider_opacity)

        self._stroke_color = QColor("#00AA00")
        self._fill_color = QColor(255, 255, 255, 0)
        self._update_button_color()

    def _pick_stroke(self) -> None:
        color = QColorDialog.getColor(self._stroke_color, self, "选择描边颜色")
        if color.isValid():
            self._stroke_color = color
            self._update_button_color()
            self.strokeColorChanged.emit(color)

    def _pick_fill(self) -> None:
        color = QColorDialog.getColor(self._fill_color, self, "选择填充颜色")
        if color.isValid():
            self._fill_color = color
            self._update_button_color()
            self.fillColorChanged.emit(color)

    def _update_button_color(self) -> None:
        self.btn_stroke.setStyleSheet(f"background-color: {self._stroke_color.name()};")
        self.btn_fill.setStyleSheet(f"background-color: {self._fill_color.name(QColor.HexArgb)};")

    def set_from_circle(self, cx: float, cy: float, r: float, stroke: QColor, width: float, fill: QColor, opacity_pct: int) -> None:
        self.spin_cx.blockSignals(True)
        self.spin_cy.blockSignals(True)
        self.spin_r.blockSignals(True)
        self.spin_width.blockSignals(True)
        self.slider_opacity.blockSignals(True)

        self.spin_cx.setValue(cx)
        self.spin_cy.setValue(cy)
        self.spin_r.setValue(r)
        self.spin_width.setValue(int(round(width)))
        self.slider_opacity.setValue(opacity_pct)
        self._stroke_color = QColor(stroke)
        self._fill_color = QColor(fill)
        self._update_button_color()

        self.spin_cx.blockSignals(False)
        self.spin_cy.blockSignals(False)
        self.spin_r.blockSignals(False)
        self.spin_width.blockSignals(False)
        self.slider_opacity.blockSignals(False)

    def set_from_point(self, x: float, y: float, r: float, stroke: QColor, width: float, fill: QColor, opacity_pct: int) -> None:
        self.set_from_circle(x, y, r, stroke, width, fill, opacity_pct)

    def set_from_line(self, x1: float, y1: float, x2: float, y2: float, stroke: QColor, width: float, opacity_pct: int, pen_style_index: int) -> None:
        # 仅填直线相关控件
        for w in (self.spin_cx, self.spin_cy, self.spin_r, self.btn_fill):
            w.blockSignals(True)
        self.spin_x1.blockSignals(True); self.spin_y1.blockSignals(True)
        self.spin_x2.blockSignals(True); self.spin_y2.blockSignals(True)
        self.spin_width.blockSignals(True); self.slider_opacity.blockSignals(True)
        self.combo_dash.blockSignals(True)

        self.spin_x1.setValue(x1); self.spin_y1.setValue(y1)
        self.spin_x2.setValue(x2); self.spin_y2.setValue(y2)
        self.spin_width.setValue(int(round(width)))
        self.slider_opacity.setValue(opacity_pct)
        self.combo_dash.setCurrentIndex(pen_style_index)
        self._stroke_color = QColor(stroke)
        self._update_button_color()

        self.spin_x1.blockSignals(False); self.spin_y1.blockSignals(False)
        self.spin_x2.blockSignals(False); self.spin_y2.blockSignals(False)
        self.spin_width.blockSignals(False); self.slider_opacity.blockSignals(False)
        self.combo_dash.blockSignals(False)

    def set_enabled(self, enabled: bool) -> None:
        for w in (
            self.spin_cx, self.spin_cy, self.spin_r, self.btn_stroke,
            self.spin_width, self.combo_dash, self.btn_fill, self.slider_opacity,
            self.spin_x1, self.spin_y1, self.spin_x2, self.spin_y2,
        ):
            w.setEnabled(enabled)


