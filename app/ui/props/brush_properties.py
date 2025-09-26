from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtCore import QTimer
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
        
        # 先连接信号
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        
        # 设置当前值（临时阻止信号，避免触发 _on_type_changed）
        current_type = self._item.brush_type()
        if current_type in self.reverse_mapping:
            self.type_combo.blockSignals(True)
            self.type_combo.setCurrentText(self.reverse_mapping[current_type])
            self.type_combo.blockSignals(False)
        
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)
    
    def _on_type_changed(self, text: str) -> None:
        # 调试：进入类型切换
        try:
            import sys
            curw = float(self._item.pen().widthF()) if hasattr(self._item, 'pen') else -1
            curst = int(self._item.pen().style()) if hasattr(self._item, 'pen') else -1
            print(f"DEBUG: _on_type_changed enter text={text} width={curw} style={curst}")
            sys.stdout.flush()
        except Exception:
            pass
        if text in self.type_mapping:
            brush_type = self.type_mapping[text]
            # 如果是从加载来的对象，不要调用 set_brush_type
            if hasattr(self._item, '_loaded_from_dict') and self._item._loaded_from_dict:
                print(f"DEBUG: _on_type_changed 跳过 set_brush_type，因为是从加载来的对象")
                return
            def apply():
                # 保存当前宽度，避免被 _update_brush_style 覆盖
                current_width = self._item.pen().widthF()
                self._item.set_brush_type(brush_type)
                # 恢复宽度
                pen = self._item.pen(); pen.setWidthF(current_width); self._item.setPen(pen)
                self._item.update()
                try:
                    self.scene.blockSignals(True)
                    self.scene.update_base_style(self._item)
                finally:
                    self.scene.blockSignals(False)
                # 调试：应用完成
                try:
                    import sys
                    curw2 = float(self._item.pen().widthF())
                    curst2 = int(self._item.pen().style())
                    print(f"DEBUG: _on_type_changed applied type={brush_type} width={curw2} style={curst2}")
                    sys.stdout.flush()
                except Exception:
                    pass
            # 推迟到事件循环空闲时执行，避开当前信号栈
            QTimer.singleShot(0, apply)


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
        
        # 笔触宽度（去掉“应用”按钮，改为数值变更即应用）
        width_layout = QHBoxLayout()
        width_label = QLabel("笔触宽度:")
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.5, 50.0)
        self.width_spin.setSingleStep(0.5)
        self.width_spin.setValue(self._item.pen().widthF())
        self._last_width = float(self._item.pen().widthF())
        # 直接应用，必要时可做轻微延迟防抖
        self.width_spin.valueChanged.connect(lambda _v: QTimer.singleShot(0, self._commit_width))
        
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
        color = QColorDialog.getColor(self._item.pen().color(), self, "选择颜色")
        if color.isValid():
            p = self._item.pen(); p.setColor(color); self._item.setPen(p)
            try:
                self.scene.update_base_style(self._item)
            except Exception:
                pass
            self._update_color_button()

    def _commit_width(self) -> None:
        w = float(self.width_spin.value())
        if abs(w - self._last_width) < 1e-6:
            return
        p = self._item.pen(); p.setWidthF(w); self._item.setPen(p)
        try:
            self.scene.update_base_style(self._item)
        except Exception:
            pass
        self._last_width = w

    def _on_style_changed(self, text: str) -> None:
        style = self.style_mapping.get(text)
        if style is None:
            return
        p = self._item.pen(); p.setStyle(style); self._item.setPen(p)
        try:
            self.scene.update_base_style(self._item)
        except Exception:
            pass


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
        self._last_opacity = float(self._item.opacity())
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        try:
            self.opacity_slider.sliderReleased.connect(self._commit_opacity)
        except Exception:
            pass
        
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

    def _commit_opacity(self) -> None:
        new_op = float(self._item.opacity())
        old_op = float(self._last_opacity)
        if abs(new_op - old_op) < 1e-6:
            return
        def do():
            self._item.setOpacity(new_op); self.scene.update_base_style(self._item)
        def undo():
            self._item.setOpacity(old_op); self.scene.update_base_style(self._item)
        self.undo_stack.push(UpdateStyleCommand.make("修改透明度", do, undo))
        self._last_opacity = new_op


class BrushSmoothingProperty:  # 已移除（占位）
    pass

class BrushEditProperty:  # 已移除（占位）
    pass
