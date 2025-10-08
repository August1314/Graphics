#!/usr/bin/env python3
"""
集成测试：完整的绘图工作流

测试从创建文档到保存的完整流程
"""

import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from PySide6.QtWidgets import QApplication, QGraphicsScene
from PySide6.QtGui import QUndoStack, QColor, QPen
from PySide6.QtCore import QPointF

from app.core.document import Document
from app.core.selection import SelectionManager
from app.core.styles import StyleManager, Style
from app.core.shapes.circle_item import CircleItem
from app.core.shapes.rect_item import RectItem
from app.core.shapes.line_item import LineItem


@pytest.fixture(scope="module")
def qapp():
    """创建 Qt 应用"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def document(qapp):
    """创建测试文档"""
    scene = QGraphicsScene()
    undo_stack = QUndoStack()
    doc = Document(scene, undo_stack)
    return doc


@pytest.fixture
def selection_manager(document):
    """创建选择管理器"""
    return SelectionManager(document.scene)


@pytest.fixture
def style_manager():
    """创建样式管理器"""
    return StyleManager()


class TestDrawingWorkflow:
    """测试完整的绘图工作流"""
    
    def test_create_and_save_document(self, document):
        """测试创建和保存文档"""
        # 1. 创建新文档
        document.new()
        assert not document.is_modified()
        
        # 2. 添加图形
        circle = CircleItem(100, 100, 50)
        document.add_shape(circle)
        assert document.is_modified()
        
        rect = RectItem(200, 200, 100, 80)
        document.add_shape(rect)
        
        # 3. 保存文档
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            document.save(temp_path)
            assert not document.is_modified()
            assert document.file_path == temp_path
            
            # 4. 验证文件存在
            assert Path(temp_path).exists()
        finally:
            # 清理
            Path(temp_path).unlink(missing_ok=True)
    
    def test_load_document(self, document):
        """测试加载文档"""
        # 1. 创建并保存文档
        document.new()
        circle = CircleItem(100, 100, 50)
        document.add_shape(circle)
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            document.save(temp_path)
            
            # 2. 创建新文档并加载
            document.new()
            assert len(document.get_all_shapes()) == 0
            
            document.load(temp_path)
            
            # 3. 验证加载的图形
            shapes = document.get_all_shapes()
            assert len(shapes) == 1
            assert isinstance(shapes[0], CircleItem)
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_undo_redo_workflow(self, document):
        """测试撤销/重做工作流"""
        document.new()
        
        # 1. 添加图形
        circle = CircleItem(100, 100, 50)
        document.add_shape(circle)
        assert len(document.get_all_shapes()) == 1
        
        # 2. 撤销添加
        document.undo_stack.undo()
        assert len(document.get_all_shapes()) == 0
        
        # 3. 重做添加
        document.undo_stack.redo()
        assert len(document.get_all_shapes()) == 1
        
        # 4. 删除图形
        document.remove_shape(circle)
        assert len(document.get_all_shapes()) == 0
        
        # 5. 撤销删除
        document.undo_stack.undo()
        assert len(document.get_all_shapes()) == 1
    
    def test_selection_workflow(self, document, selection_manager):
        """测试选择工作流"""
        document.new()
        
        # 1. 添加多个图形
        circle = CircleItem(100, 100, 50)
        rect = RectItem(200, 200, 100, 80)
        line = LineItem(300, 300, 400, 400)
        
        document.add_shape(circle)
        document.add_shape(rect)
        document.add_shape(line)
        
        # 2. 选择单个图形
        selection_manager.select([circle])
        assert selection_manager.has_selection()
        assert len(selection_manager.get_selected_items()) == 1
        assert circle.isSelected()
        
        # 3. 选择多个图形
        selection_manager.select([circle, rect])
        assert len(selection_manager.get_selected_items()) == 2
        
        # 4. 选择所有图形
        selection_manager.select_all()
        assert len(selection_manager.get_selected_items()) == 3
        
        # 5. 清空选择
        selection_manager.clear_selection()
        assert not selection_manager.has_selection()
    
    def test_style_workflow(self, document, style_manager):
        """测试样式工作流"""
        document.new()
        
        # 1. 创建图形
        circle = CircleItem(100, 100, 50)
        document.add_shape(circle)
        
        # 2. 创建样式
        style = Style(
            pen_color=QColor("#FF0000"),
            pen_width=5.0,
            pen_style=QPen.SolidLine,
            brush_color=QColor("#00FF00"),
            brush_style=QPen.SolidPattern,
            opacity=0.8
        )
        
        # 3. 应用样式
        style_manager.apply_style(circle, style)
        
        # 4. 验证样式
        applied_style = style_manager.get_style(circle)
        assert applied_style.pen_color.name() == "#ff0000"
        assert applied_style.pen_width == 5.0
    
    def test_export_workflow(self, document):
        """测试导出工作流"""
        document.new()
        
        # 1. 添加图形
        circle = CircleItem(100, 100, 50)
        rect = RectItem(200, 200, 100, 80)
        document.add_shape(circle)
        document.add_shape(rect)
        
        # 2. 导出为 PNG
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            document.export_png(temp_path, 800, 600)
            
            # 3. 验证文件存在
            assert Path(temp_path).exists()
            
            # 4. 验证文件大小
            assert Path(temp_path).stat().st_size > 0
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_complex_workflow(self, document, selection_manager, style_manager):
        """测试复杂的工作流"""
        # 1. 创建新文档
        document.new()
        
        # 2. 添加多个图形
        shapes = [
            CircleItem(100, 100, 50),
            RectItem(200, 200, 100, 80),
            LineItem(300, 300, 400, 400),
        ]
        
        for shape in shapes:
            document.add_shape(shape)
        
        # 3. 选择部分图形
        selection_manager.select(shapes[:2])
        
        # 4. 批量应用样式
        style = Style(
            pen_color=QColor("#0000FF"),
            pen_width=3.0,
            pen_style=QPen.SolidLine,
            brush_color=QColor("#FFFF00"),
            brush_style=QPen.SolidPattern,
            opacity=1.0
        )
        
        for item in selection_manager.get_selected_items():
            style_manager.apply_style(item, style)
        
        # 5. 保存文档
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            document.save(temp_path)
            
            # 6. 加载文档
            document.new()
            document.load(temp_path)
            
            # 7. 验证
            loaded_shapes = document.get_all_shapes()
            assert len(loaded_shapes) == 3
            
            # 8. 导出
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                png_path = f.name
            
            try:
                document.export_png(png_path, 800, 600)
                assert Path(png_path).exists()
            finally:
                Path(png_path).unlink(missing_ok=True)
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
