from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QDoubleSpinBox, QSlider, QComboBox, 
                               QPushButton, QColorDialog)

from app.core.shapes.brush_path_item import BrushPathItem
from app.core.commands.update_style_cmd import UpdateStyleCommand


class BrushTypeProperty(QWidget):
    """画笔类型属性组件"""
    
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self._item: BrushPathItem = item
        self.scene = scene
        self.undo_stack = undo_stack
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 画笔类型选择
        type_label = QLabel("画笔类型:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["普通画笔", "马克笔", "书法笔", "喷枪", "橡皮擦"])
        
        # 映射显示名称到内部类型
        self.type_mapping = {
            "普通画笔": "pen",
            "马克笔": "marker", 
            "书法笔": "calligraphy",
            "喷枪": "spray",
            "橡皮擦": "eraser"
        }
        
        # 反向映射
        self.reverse_mapping = {v: k for k, v in self.type_mapping.items()}
        
        # 设置当前值
        current_type = self._item.brush_type()
        if current_type in self.reverse_mapping:
            self.type_combo.setCurrentText(self.reverse_mapping[current_type])
        
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)
    
    def _on_type_changed(self, text: str) -> None:
        if text in self.type_mapping:
            brush_type = self.type_mapping[text]
            self._item.set_brush_type(brush_type)
            self._item.update()
            self.scene.update_base_style(self._item)


class BrushStrokeProperty(QWidget):
    """画笔笔触属性组件"""
    
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self._item: BrushPathItem = item
        self.scene = scene
        self.undo_stack = undo_stack
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 笔触颜色
        color_layout = QHBoxLayout()
        color_label = QLabel("笔触颜色:")
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 25)
        self._update_color_button()
        self.color_button.clicked.connect(self._on_color_clicked)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        # 笔触宽度
        width_layout = QHBoxLayout()
        width_label = QLabel("笔触宽度:")
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.5, 50.0)
        self.width_spin.setSingleStep(0.5)
        self.width_spin.setValue(self._item.pen().widthF())
        self.width_spin.valueChanged.connect(self._on_width_changed)
        
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_spin)
        
        # 笔触样式
        style_layout = QHBoxLayout()
        style_label = QLabel("笔触样式:")
        self.style_combo = QComboBox()
        self.style_combo.addItems(["实线", "虚线", "点线", "点划线", "双点划线"])
        
        # 样式映射
        self.style_mapping = {
            "实线": Qt.PenStyle.SolidLine,
            "虚线": Qt.PenStyle.DashLine,
            "点线": Qt.PenStyle.DotLine,
            "点划线": Qt.PenStyle.DashDotLine,
            "双点划线": Qt.PenStyle.DashDotDotLine
        }
        
        # 设置当前值
        current_style = self._item.pen().style()
        for name, style in self.style_mapping.items():
            if style == current_style:
                self.style_combo.setCurrentText(name)
                break
        
        self.style_combo.currentTextChanged.connect(self._on_style_changed)
        
        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_combo)
        
        layout.addLayout(color_layout)
        layout.addLayout(width_layout)
        layout.addLayout(style_layout)
    
    def _update_color_button(self) -> None:
        color = self._item.pen().color()
        self.color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
    
    def _on_color_clicked(self) -> None:
        current_color = self._item.pen().color()
        color = QColorDialog.getColor(current_color, self.color_button, "选择笔触颜色")
        if color.isValid():
            pen = self._item.pen()
            pen.setColor(color)
            self._item.setPen(pen)
            self._update_color_button()
            self.scene.update_base_style(self._item)
    
    def _on_width_changed(self, value: float) -> None:
        pen = self._item.pen()
        pen.setWidthF(value)
        self._item.setPen(pen)
        self.scene.update_base_style(self._item)
    
    def _on_style_changed(self, text: str) -> None:
        if text in self.style_mapping:
            pen = self._item.pen()
            pen.setStyle(self.style_mapping[text])
            self._item.setPen(pen)
            self.scene.update_base_style(self._item)


class BrushOpacityProperty(QWidget):
    """画笔透明度属性组件"""
    
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self._item: BrushPathItem = item
        self.scene = scene
        self.undo_stack = undo_stack
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 透明度
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度:")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self._item.opacity() * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        
        self.opacity_label = QLabel(f"{int(self._item.opacity() * 100)}%")
        self.opacity_label.setMinimumWidth(40)
        
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        layout.addLayout(opacity_layout)
    
    def _on_opacity_changed(self, value: int) -> None:
        opacity = value / 100.0
        self._item.setOpacity(opacity)
        self.opacity_label.setText(f"{value}%")
        self.scene.update_base_style(self._item)


class BrushSmoothingProperty:  # 已移除（占位）
    pass

class BrushEditProperty:  # 已移除（占位）
    pass
