"""Pytest 配置和共享 fixtures

提供测试所需的通用 fixtures 和配置。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QGraphicsScene
from PySide6.QtGui import QUndoStack

# 确保可以导入 app 模块
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope='session')
def qapp():
    """Qt 应用实例（会话级别）
    
    整个测试会话只创建一次 QApplication。
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def scene():
    """创建一个空的 QGraphicsScene
    
    每个测试函数都会获得一个新的场景实例。
    """
    return QGraphicsScene()


@pytest.fixture
def undo_stack():
    """创建一个 QUndoStack
    
    用于测试撤销/重做功能。
    """
    return QUndoStack()


@pytest.fixture
def sample_shapes(scene):
    """创建一些示例图形
    
    返回包含多个图形的场景。
    """
    from app.core.shapes.circle_item import CircleItem
    from app.core.shapes.rect_item import RectItem
    from app.core.shapes.line_item import LineItem
    from PySide6.QtGui import QPen, QColor
    
    # 创建圆形
    circle = CircleItem(100, 100, 50)
    circle.setPen(QPen(QColor("#FF0000"), 2.0))
    scene.addItem(circle)
    
    # 创建矩形
    rect = RectItem(200, 200, 100, 80)
    rect.setPen(QPen(QColor("#00FF00"), 3.0))
    scene.addItem(rect)
    
    # 创建直线
    line = LineItem(50, 50, 150, 150)
    line.setPen(QPen(QColor("#0000FF"), 1.5))
    scene.addItem(line)
    
    return scene


def create_test_scene(num_shapes: int = 10) -> QGraphicsScene:
    """创建包含指定数量图形的测试场景
    
    Args:
        num_shapes: 要创建的图形数量
    
    Returns:
        包含图形的场景
    """
    from app.core.shapes.circle_item import CircleItem
    from PySide6.QtGui import QPen, QColor
    
    scene = QGraphicsScene()
    
    for i in range(num_shapes):
        x = (i % 5) * 100 + 50
        y = (i // 5) * 100 + 50
        radius = 20 + (i * 5)
        
        circle = CircleItem(x, y, radius)
        circle.setPen(QPen(QColor(f"#{i*20:02x}{i*15:02x}{i*10:02x}"), 2.0))
        scene.addItem(circle)
    
    return scene
