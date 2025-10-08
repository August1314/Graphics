"""测试 Document 模块

验证文档管理功能是否正常工作。
"""

from __future__ import annotations

import pytest
from pathlib import Path

from app.core.document import Document
from app.core.shapes.circle_item import CircleItem
from app.core.shapes.rect_item import RectItem
from PySide6.QtGui import QPen, QColor


class TestDocument:
    """测试 Document 类"""
    
    def test_document_initialization(self, scene, undo_stack):
        """测试文档初始化"""
        doc = Document(scene, undo_stack)
        
        assert doc.scene == scene
        assert doc.undo_stack == undo_stack
        assert not doc.is_modified()
        assert doc.get_file_path() is None
    
    def test_new_document(self, scene, undo_stack):
        """测试创建新文档"""
        doc = Document(scene, undo_stack)
        
        # 添加一些图形
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        doc.mark_modified()
        
        # 创建新文档应该清空所有内容
        doc.new()
        
        assert len(scene.items()) == 0
        assert not doc.is_modified()
        assert doc.get_file_path() is None
    
    def test_save_and_load(self, scene, undo_stack, tmp_path):
        """测试保存和加载"""
        doc = Document(scene, undo_stack)
        
        # 添加图形
        circle = CircleItem(100, 100, 50)
        circle.setPen(QPen(QColor("#FF0000"), 3.0))
        scene.addItem(circle)
        
        rect = RectItem(200, 200, 100, 80)
        rect.setPen(QPen(QColor("#00FF00"), 2.0))
        scene.addItem(rect)
        
        # 保存
        save_path = tmp_path / "test.json"
        assert doc.save(str(save_path))
        assert save_path.exists()
        assert not doc.is_modified()
        
        # 清空场景
        scene.clear()
        assert len(scene.items()) == 0
        
        # 加载
        assert doc.load(str(save_path))
        assert len(scene.items()) == 2
        assert not doc.is_modified()
    
    def test_modified_state(self, scene, undo_stack):
        """测试修改状态管理"""
        doc = Document(scene, undo_stack)
        
        # 初始状态
        assert not doc.is_modified()
        
        # 标记为已修改
        doc.mark_modified()
        assert doc.is_modified()
        
        # 标记为未修改
        doc.mark_modified(False)
        assert not doc.is_modified()
    
    def test_file_path(self, scene, undo_stack):
        """测试文件路径管理"""
        doc = Document(scene, undo_stack)
        
        # 初始无路径
        assert doc.get_file_path() is None
        
        # 设置路径
        doc.set_file_path("/path/to/file.json")
        assert doc.get_file_path() == "/path/to/file.json"
    
    def test_metadata(self, scene, undo_stack):
        """测试元数据管理"""
        doc = Document(scene, undo_stack)
        
        # 设置元数据
        doc.set_metadata("author", "Test User")
        doc.set_metadata("version", "1.0")
        
        # 获取元数据
        assert doc.get_metadata("author") == "Test User"
        assert doc.get_metadata("version") == "1.0"
        assert doc.get_metadata("nonexistent", "default") == "default"
    
    def test_add_remove_shape(self, scene, undo_stack):
        """测试添加和移除图形"""
        doc = Document(scene, undo_stack)
        
        # 添加图形
        circle = CircleItem(100, 100, 50)
        doc.add_shape(circle)
        
        assert len(doc.get_all_shapes()) == 1
        assert doc.get_shape_count() == 1
        assert doc.is_modified()
        
        # 移除图形
        doc.mark_modified(False)
        doc.remove_shape(circle)
        
        assert len(doc.get_all_shapes()) == 0
        assert doc.get_shape_count() == 0
        assert doc.is_modified()
    
    def test_export_png(self, scene, undo_stack, tmp_path):
        """测试导出 PNG"""
        doc = Document(scene, undo_stack)
        
        # 添加图形
        circle = CircleItem(100, 100, 50)
        scene.addItem(circle)
        
        # 导出
        export_path = tmp_path / "test.png"
        assert doc.export_png(str(export_path))
        assert export_path.exists()
        assert export_path.stat().st_size > 0
    
    def test_signals(self, scene, undo_stack, qtbot):
        """测试信号发射"""
        doc = Document(scene, undo_stack)
        
        # 测试 modified_changed 信号
        with qtbot.waitSignal(doc.modified_changed, timeout=1000):
            doc.mark_modified()
        
        # 测试 file_path_changed 信号
        with qtbot.waitSignal(doc.file_path_changed, timeout=1000):
            doc.set_file_path("/test/path.json")
