"""测试 SelectionManager 模块

验证选择管理功能是否正常工作。
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QRectF

from app.core.selection import SelectionManager, SelectionMode
from app.core.shapes.circle_item import CircleItem
from app.core.shapes.rect_item import RectItem


class TestSelectionManager:
    """测试 SelectionManager 类"""
    
    def test_initialization(self, scene):
        """测试初始化"""
        mgr = SelectionManager(scene)
        
        assert mgr.scene == scene
        assert not mgr.has_selection()
        assert mgr.get_selection_count() == 0
    
    def test_select_replace(self, scene):
        """测试替换选择"""
        mgr = SelectionManager(scene)
        
        # 添加图形
        circle1 = CircleItem(100, 100, 50)
        circle2 = CircleItem(200, 200, 50)
        scene.addItem(circle1)
        scene.addItem(circle2)
        
        # 选择第一个
        mgr.select([circle1], SelectionMode.REPLACE)
        assert mgr.get_selection_count() == 1
        assert circle1.isSelected()
        assert not circle2.isSelected()
        
        # 替换为第二个
        mgr.select([circle2], SelectionMode.REPLACE)
        assert mgr.get_selection_count() == 1
        assert not circle1.isSelected()
        assert circle2.isSelected()
    
    def test_select_add(self, scene):
        """测试添加选择"""
        mgr = SelectionManager(scene)
        
        circle1 = CircleItem(100, 100, 50)
        circle2 = CircleItem(200, 200, 50)
        scene.addItem(circle1)
        scene.addItem(circle2)
        
        # 选择第一个
        mgr.select([circle1], SelectionMode.REPLACE)
        assert mgr.get_selection_count() == 1
        
        # 添加第二个
        mgr.select([circle2], SelectionMode.ADD)
        assert mgr.get_selection_count() == 2
        assert circle1.isSelected()
        assert circle2.isSelected()
    
    def test_select_toggle(self, scene):
        """测试切换选择"""
        mgr = SelectionManager(scene)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        
        # 初始未选中
        assert not circle.isSelected()
        
        # 切换为选中
        mgr.select([circle], SelectionMode.TOGGLE)
        assert circle.isSelected()
        
        # 再次切换为未选中
        mgr.select([circle], SelectionMode.TOGGLE)
        assert not circle.isSelected()
    
    def test_select_remove(self, scene):
        """测试移除选择"""
        mgr = SelectionManager(scene)
        
        circle1 = CircleItem(100, 100, 50)
        circle2 = CircleItem(200, 200, 50)
        scene.addItem(circle1)
        scene.addItem(circle2)
        
        # 选择两个
        mgr.select([circle1, circle2], SelectionMode.REPLACE)
        assert mgr.get_selection_count() == 2
        
        # 移除一个
        mgr.select([circle1], SelectionMode.REMOVE)
        assert mgr.get_selection_count() == 1
        assert not circle1.isSelected()
        assert circle2.isSelected()
    
    def test_select_all(self, scene):
        """测试选择所有"""
        mgr = SelectionManager(scene)
        
        # 添加多个图形
        for i in range(5):
            circle = CircleItem(i * 100, 100, 50)
            scene.addItem(circle)
        
        # 选择所有
        mgr.select_all()
        assert mgr.get_selection_count() == 5
    
    def test_clear_selection(self, scene):
        """测试清空选择"""
        mgr = SelectionManager(scene)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        
        # 选中
        mgr.select([circle], SelectionMode.REPLACE)
        assert mgr.has_selection()
        
        # 清空
        mgr.clear_selection()
        assert not mgr.has_selection()
        assert not circle.isSelected()
    
    def test_toggle_selection(self, scene):
        """测试切换单个图形选择"""
        mgr = SelectionManager(scene)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        
        # 切换
        mgr.toggle_selection(circle)
        assert circle.isSelected()
        
        mgr.toggle_selection(circle)
        assert not circle.isSelected()
    
    def test_select_in_rect(self, scene):
        """测试矩形选择"""
        mgr = SelectionManager(scene)
        
        # 添加图形在不同位置
        circle1 = CircleItem(50, 50, 20)   # 在矩形内
        circle2 = CircleItem(150, 150, 20)  # 在矩形内
        circle3 = CircleItem(300, 300, 20)  # 在矩形外
        scene.addItem(circle1)
        scene.addItem(circle2)
        scene.addItem(circle3)
        
        # 选择矩形区域
        rect = QRectF(0, 0, 200, 200)
        mgr.select_in_rect(rect, SelectionMode.REPLACE)
        
        # 验证只有矩形内的被选中
        assert circle1.isSelected()
        assert circle2.isSelected()
        assert not circle3.isSelected()
    
    def test_get_selection_bounds(self, scene):
        """测试获取选择包围盒"""
        mgr = SelectionManager(scene)
        
        circle1 = CircleItem(100, 100, 50)
        circle2 = CircleItem(300, 300, 50)
        scene.addItem(circle1)
        scene.addItem(circle2)
        
        # 选择两个
        mgr.select([circle1, circle2], SelectionMode.REPLACE)
        
        # 获取包围盒
        bounds = mgr.get_selection_bounds()
        assert bounds.isValid()
        assert bounds.contains(circle1.sceneBoundingRect())
        assert bounds.contains(circle2.sceneBoundingRect())
    
    def test_signals(self, scene, qtbot):
        """测试信号发射"""
        mgr = SelectionManager(scene)
        
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        
        # 测试 selection_changed 信号
        with qtbot.waitSignal(mgr.selection_changed, timeout=1000):
            mgr.select([circle], SelectionMode.REPLACE)
    
    def test_selection_feedback(self, scene):
        """测试选择反馈"""
        mgr = SelectionManager(scene)
        
        # 默认启用
        assert mgr._selection_feedback_enabled
        
        # 禁用
        mgr.set_selection_feedback_enabled(False)
        assert not mgr._selection_feedback_enabled
        
        # 启用
        mgr.set_selection_feedback_enabled(True)
        assert mgr._selection_feedback_enabled
