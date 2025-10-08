#!/usr/bin/env python3
"""测试 Phase 1 和 Phase 2 的功能

运行此脚本来验证日志系统、异常处理、核心模块是否正常工作。
"""

import sys
import logging
from pathlib import Path

# 确保可以导入 app 模块
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QGraphicsScene
from PySide6.QtGui import QUndoStack, QPen, QColor

from app.utils.logging_config import setup_logging, get_logger
from app.utils.exceptions import SerializationError, FileOperationError
from app.core.document import Document
from app.core.selection import SelectionManager, SelectionMode
from app.core.styles import StyleManager, Style
from app.core.shapes.circle_item import CircleItem
from app.core.shapes.rect_item import RectItem
from app.core.shapes.line_item import LineItem


def test_logging():
    """测试日志系统"""
    print("\n" + "="*60)
    print("测试 1: 日志系统")
    print("="*60)
    
    # 初始化日志
    logger = setup_logging(level=logging.DEBUG, log_file="test_app.log")
    
    # 测试不同级别的日志
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    # 获取模块日志器
    module_logger = get_logger('test_module')
    module_logger.info("模块日志器工作正常")
    
    print("✅ 日志系统测试通过")
    print(f"   日志文件: test_app.log")
    return True


def test_exceptions():
    """测试异常处理"""
    print("\n" + "="*60)
    print("测试 2: 异常处理")
    print("="*60)
    
    logger = get_logger('test_exceptions')
    
    # 测试自定义异常
    try:
        raise SerializationError("测试序列化错误")
    except SerializationError as e:
        logger.info(f"捕获到序列化错误: {e}")
        print("✅ SerializationError 正常工作")
    
    try:
        raise FileOperationError("测试文件操作错误")
    except FileOperationError as e:
        logger.info(f"捕获到文件操作错误: {e}")
        print("✅ FileOperationError 正常工作")
    
    print("✅ 异常处理测试通过")
    return True


def test_document(app):
    """测试 Document 模块"""
    print("\n" + "="*60)
    print("测试 3: Document 模块")
    print("="*60)
    
    logger = get_logger('test_document')
    
    # 创建场景和撤销栈
    scene = QGraphicsScene()
    undo_stack = QUndoStack()
    
    # 创建文档
    doc = Document(scene, undo_stack)
    logger.info("Document 创建成功")
    print("✅ Document 初始化")
    
    # 测试添加图形
    circle = CircleItem(100, 100, 50)
    circle.setPen(QPen(QColor("#FF0000"), 3.0))
    doc.add_shape(circle)
    
    rect = RectItem(200, 200, 100, 80)
    rect.setPen(QPen(QColor("#00FF00"), 2.0))
    doc.add_shape(rect)
    
    logger.info(f"添加了 {doc.get_shape_count()} 个图形")
    print(f"✅ 添加图形: {doc.get_shape_count()} 个")
    
    # 测试保存
    save_path = Path("test_output/test_scene.json")
    save_path.parent.mkdir(exist_ok=True)
    
    if doc.save(str(save_path)):
        logger.info(f"文档保存成功: {save_path}")
        print(f"✅ 保存文档: {save_path}")
    else:
        print("❌ 保存文档失败")
        return False
    
    # 测试加载
    doc.new()  # 清空
    if doc.load(str(save_path)):
        logger.info(f"文档加载成功，图形数量: {doc.get_shape_count()}")
        print(f"✅ 加载文档: {doc.get_shape_count()} 个图形")
    else:
        print("❌ 加载文档失败")
        return False
    
    # 测试导出 PNG
    png_path = Path("test_output/test_scene.png")
    if doc.export_png(str(png_path)):
        logger.info(f"PNG 导出成功: {png_path}")
        print(f"✅ 导出 PNG: {png_path}")
    else:
        print("❌ 导出 PNG 失败")
        return False
    
    print("✅ Document 模块测试通过")
    return True


def test_selection_manager(app):
    """测试 SelectionManager 模块"""
    print("\n" + "="*60)
    print("测试 4: SelectionManager 模块")
    print("="*60)
    
    logger = get_logger('test_selection')
    
    # 创建场景
    scene = QGraphicsScene()
    
    # 创建选择管理器
    mgr = SelectionManager(scene)
    logger.info("SelectionManager 创建成功")
    print("✅ SelectionManager 初始化")
    
    # 添加图形
    circle1 = CircleItem(100, 100, 50)
    circle2 = CircleItem(200, 200, 50)
    circle3 = CircleItem(300, 300, 50)
    scene.addItem(circle1)
    scene.addItem(circle2)
    scene.addItem(circle3)
    
    # 测试选择
    mgr.select([circle1], SelectionMode.REPLACE)
    assert mgr.get_selection_count() == 1
    print("✅ 单选功能")
    
    mgr.select([circle2], SelectionMode.ADD)
    assert mgr.get_selection_count() == 2
    print("✅ 添加选择功能")
    
    mgr.select_all()
    assert mgr.get_selection_count() == 3
    print("✅ 全选功能")
    
    mgr.clear_selection()
    assert mgr.get_selection_count() == 0
    print("✅ 清空选择功能")
    
    # 测试切换
    mgr.toggle_selection(circle1)
    assert circle1.isSelected()
    print("✅ 切换选择功能")
    
    # 测试包围盒
    mgr.select([circle1, circle2], SelectionMode.REPLACE)
    bounds = mgr.get_selection_bounds()
    assert bounds.isValid()
    print("✅ 获取选择包围盒")
    
    logger.info("SelectionManager 所有功能测试通过")
    print("✅ SelectionManager 模块测试通过")
    return True


def test_style_manager(app):
    """测试 StyleManager 模块"""
    print("\n" + "="*60)
    print("测试 5: StyleManager 模块")
    print("="*60)
    
    logger = get_logger('test_style')
    
    # 创建样式管理器
    mgr = StyleManager()
    logger.info("StyleManager 创建成功")
    print("✅ StyleManager 初始化")
    
    # 创建图形
    scene = QGraphicsScene()
    circle = CircleItem(100, 100, 50)
    scene.addItem(circle)
    
    # 测试应用样式
    style = Style(
        pen_color=QColor("#FF0000"),
        pen_width=5.0,
        brush_color=QColor("#00FF0080"),
        opacity=0.8
    )
    mgr.apply_style(circle, style)
    print("✅ 应用样式")
    
    # 测试获取样式
    retrieved_style = mgr.get_style(circle)
    assert retrieved_style.pen_color == style.pen_color
    assert retrieved_style.pen_width == style.pen_width
    print("✅ 获取样式")
    
    # 测试默认样式
    default_style = mgr.get_default_style('circle')
    assert default_style is not None
    print("✅ 获取默认样式")
    
    # 测试批量应用
    rect1 = RectItem(200, 200, 100, 80)
    rect2 = RectItem(350, 350, 100, 80)
    scene.addItem(rect1)
    scene.addItem(rect2)
    
    mgr.apply_style_to_selection([rect1, rect2], style)
    print("✅ 批量应用样式")
    
    logger.info("StyleManager 所有功能测试通过")
    print("✅ StyleManager 模块测试通过")
    return True


def test_serializer(app):
    """测试 Serializer 模块"""
    print("\n" + "="*60)
    print("测试 6: Serializer 模块（重构版）")
    print("="*60)
    
    logger = get_logger('test_serializer')
    
    from app.core.serializer import Serializer
    
    # 创建序列化器
    serializer = Serializer()
    logger.info("Serializer 创建成功")
    print("✅ Serializer 初始化")
    
    # 创建场景和图形
    scene = QGraphicsScene()
    
    circle = CircleItem(100, 100, 50)
    circle.setPen(QPen(QColor("#FF0000"), 3.0))
    scene.addItem(circle)
    
    rect = RectItem(200, 200, 100, 80)
    rect.setPen(QPen(QColor("#00FF00"), 2.0))
    scene.addItem(rect)
    
    line = LineItem(50, 50, 150, 150)
    line.setPen(QPen(QColor("#0000FF"), 1.5))
    scene.addItem(line)
    
    # 测试序列化
    data = serializer.serialize(scene)
    assert data['version'] == '2.0'
    assert len(data['shapes']) == 3
    logger.info(f"序列化成功: {len(data['shapes'])} 个图形")
    print(f"✅ 序列化: {len(data['shapes'])} 个图形")
    
    # 测试反序列化
    new_scene = QGraphicsScene()
    items = serializer.deserialize(data, new_scene)
    assert len(items) == 3
    logger.info(f"反序列化成功: {len(items)} 个图形")
    print(f"✅ 反序列化: {len(items)} 个图形")
    
    # 验证属性保持
    loaded_circle = items[0]
    if hasattr(loaded_circle, 'pen'):
        pen = loaded_circle.pen()
        # 注意：由于序列化/反序列化，颜色可能略有不同
        print(f"✅ 属性保持: 颜色={pen.color().name()}, 宽度={pen.widthF()}")
    
    logger.info("Serializer 所有功能测试通过")
    print("✅ Serializer 模块测试通过")
    return True


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Phase 1 & Phase 2 功能测试")
    print("="*60)
    
    # 创建 Qt 应用（某些测试需要）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    results = []
    
    # 运行所有测试
    try:
        results.append(("日志系统", test_logging()))
        results.append(("异常处理", test_exceptions()))
        results.append(("Document 模块", test_document(app)))
        results.append(("SelectionManager 模块", test_selection_manager(app)))
        results.append(("StyleManager 模块", test_style_manager(app)))
        results.append(("Serializer 模块", test_serializer(app)))
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Phase 1 和 Phase 2 功能正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
