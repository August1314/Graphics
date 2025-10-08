"""测试 PropertyController 模块

验证属性控制器功能是否正常工作。
"""

from __future__ import annotations

import pytest
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import Qt

from app.controllers.property_controller import PropertyController
from app.core.selection import SelectionManager
from app.core.styles import StyleManager
from app.core.shapes.circle_item import CircleItem
from app.core.shapes.line_item import LineItem


class TestPropertyController:
    """测试 PropertyController 类"""
    
    def test_initialization(self, scene, undo_stack):
        """测试初始化"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        assert controller.selection_manager == selection_mgr
        assert controller.style_manager == style_mgr
        assert controller.undo_stack == undo_stack
    
    def test_update_pen_color(self, scene, undo_stack):
        """测试更新画笔颜色"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        # 创建并选中图形
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        selection_mgr.select([circle])
        
        # 更新颜色
        new_color = QColor("#FF0000")
        assert controller.update_pen_color(new_color)
        
        # 验证
        assert circle.pen().color() == new_color
        
        # 验证撤销
        undo_stack.undo()
        assert circle.pen().color() != new_color
    
    def test_update_pen_width(self, scene, undo_stack):
        """测试更新画笔宽度"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        selection_mgr.select([circle])
        
        # 更新宽度
        new_width = 5.0
        assert controller.update_pen_width(new_width)
        
        # 验证
        assert circle.pen().widthF() == new_width
    
    def test_update_opacity(self, scene, undo_stack):
        """测试更新不透明度"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        selection_mgr.select([circle])
        
        # 更新不透明度
        new_opacity = 0.5
        assert controller.update_opacity(new_opacity)
        
        # 验证
        assert circle.opacity() == new_opacity
    
    def test_update_center(self, scene, undo_stack):
        """测试更新中心点"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        selection_mgr.select([circle])
        
        # 更新中心
        new_cx, new_cy = 200.0, 200.0
        assert controller.update_center(new_cx, new_cy)
        
        # 验证
        cx, cy, r = circle.center_radius()
        assert cx == new_cx
        assert cy == new_cy
    
    def test_update_radius(self, scene, undo_stack):
        """测试更新半径"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        selection_mgr.select([circle])
        
        # 更新半径
        new_radius = 75.0
        assert controller.update_radius(new_radius)
        
        # 验证
        cx, cy, r = circle.center_radius()
        assert r == new_radius
    
    def test_no_selection(self, scene, undo_stack):
        """测试无选择时的行为"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        # 没有选中任何图形
        assert not controller.update_pen_color(QColor("#FF0000"))
        assert not controller.update_pen_width(5.0)
    
    def test_signals(self, scene, undo_stack, qtbot):
        """测试信号发射"""
        selection_mgr = SelectionManager(scene)
        style_mgr = StyleManager()
        controller = PropertyController(selection_mgr, style_mgr, undo_stack)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        selection_mgr.select([circle])
        
        # 测试 property_updated 信号
        with qtbot.waitSignal(controller.property_updated, timeout=1000):
            controller.update_pen_color(QColor("#FF0000"))
