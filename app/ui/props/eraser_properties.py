from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QDoubleSpinBox, QSlider, QComboBox, 
                               QPushButton, QColorDialog, QCheckBox, QGroupBox)

from app.core.tools.eraser_tool import EraserTool


class EraserModeProperty(QWidget):
    """橡皮擦模式属性组件"""
    
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self._eraser_tool: EraserTool = item
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 橡皮擦模式选择
        mode_label = QLabel("擦除模式:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["普通橡皮擦", "对象橡皮擦"])
        
        # 映射显示名称到内部模式
        self.mode_mapping = {
            "普通橡皮擦": EraserTool.EraserMode.PATH_ERASER,
            "对象橡皮擦": EraserTool.EraserMode.OBJECT_ERASER
        }
        
        # 反向映射
        self.reverse_mapping = {v: k for k, v in self.mode_mapping.items()}
        
        # 设置当前值
        current_mode = self._eraser_tool._mode
        if current_mode in self.reverse_mapping:
            self.mode_combo.setCurrentText(self.reverse_mapping[current_mode])
        
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        
        # 模式说明
        self.mode_description = QLabel()
        self._update_mode_description()
        
        layout.addWidget(mode_label)
        layout.addWidget(self.mode_combo)
        layout.addWidget(self.mode_description)
    
    def _on_mode_changed(self, text: str) -> None:
        if text in self.mode_mapping:
            mode = self.mode_mapping[text]
            self._eraser_tool.set_mode(mode)
            self._update_mode_description()
    
    def _update_mode_description(self) -> None:
        current_mode = self._eraser_tool._mode
        if current_mode == EraserTool.EraserMode.PATH_ERASER:
            description = "通过路径减法擦除对象的部分区域"
        else:
            description = "直接删除整个对象"
        self.mode_description.setText(f"<small>{description}</small>")
        self.mode_description.setStyleSheet("color: #666; font-style: italic;")


class EraserSizeProperty(QWidget):
    """橡皮擦大小属性组件"""
    
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self._eraser_tool: EraserTool = item
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 橡皮擦大小
        size_layout = QHBoxLayout()
        size_label = QLabel("橡皮擦大小:")
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(1.0, 100.0)
        self.size_spin.setSingleStep(1.0)
        self.size_spin.setDecimals(1)
        self.size_spin.setValue(self._eraser_tool.get_size())
        self.size_spin.valueChanged.connect(self._on_size_changed)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        
        # 大小滑块
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 1000)  # 对应1.0-100.0
        self.size_slider.setValue(int(self._eraser_tool.get_size() * 10))
        self.size_slider.valueChanged.connect(self._on_slider_changed)
        
        layout.addLayout(size_layout)
        layout.addWidget(self.size_slider)
    
    def _on_size_changed(self, value: float) -> None:
        self._eraser_tool.set_size(value)
        # 同步滑块
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(int(value * 10))
        self.size_slider.blockSignals(False)
    
    def _on_slider_changed(self, value: int) -> None:
        size_value = value / 10.0
        self._eraser_tool.set_size(size_value)
        # 同步数值框
        self.size_spin.blockSignals(True)
        self.size_spin.setValue(size_value)
        self.size_spin.blockSignals(False)


class EraserPreviewProperty(QWidget):
    """橡皮擦预览属性组件"""
    
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self._eraser_tool: EraserTool = item
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 预览颜色
        color_layout = QHBoxLayout()
        color_label = QLabel("预览颜色:")
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 25)
        self._update_color_button()
        self.color_button.clicked.connect(self._on_color_clicked)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        # 预览透明度
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("预览透明度:")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(int(self._eraser_tool._opacity * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        
        self.opacity_label = QLabel(f"{int(self._eraser_tool._opacity * 100)}%")
        self.opacity_label.setMinimumWidth(40)
        
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        layout.addLayout(color_layout)
        layout.addLayout(opacity_layout)
    
    def _update_color_button(self) -> None:
        color = self._eraser_tool._color
        self.color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
    
    def _on_color_clicked(self) -> None:
        current_color = self._eraser_tool._color
        color = QColorDialog.getColor(current_color, self.color_button, "选择预览颜色")
        if color.isValid():
            self._eraser_tool._color = color
            self._update_color_button()
    
    def _on_opacity_changed(self, value: int) -> None:
        opacity = value / 100.0
        self._eraser_tool._opacity = opacity
        self.opacity_label.setText(f"{value}%")


class EraserAdvancedProperty(QWidget):
    """橡皮擦高级属性组件"""
    
    def __init__(self, item, scene, undo_stack) -> None:
        super().__init__()
        self._eraser_tool: EraserTool = item
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 平滑开关
        self.smoothing_check = QCheckBox("启用路径平滑")
        self.smoothing_check.setChecked(self._eraser_tool._smoothing)
        self.smoothing_check.toggled.connect(self._on_smoothing_toggled)
        
        # 最小距离
        distance_layout = QHBoxLayout()
        distance_label = QLabel("最小采样距离:")
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0.5, 10.0)
        self.distance_spin.setSingleStep(0.5)
        self.distance_spin.setDecimals(1)
        self.distance_spin.setValue(self._eraser_tool._min_distance)
        self.distance_spin.valueChanged.connect(self._on_distance_changed)
        
        distance_layout.addWidget(distance_label)
        distance_layout.addWidget(self.distance_spin)
        
        layout.addWidget(self.smoothing_check)
        layout.addLayout(distance_layout)
    
    def _on_smoothing_toggled(self, checked: bool) -> None:
        self._eraser_tool._smoothing = checked
    
    def _on_distance_changed(self, value: float) -> None:
        self._eraser_tool._min_distance = value
