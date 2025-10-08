#!/usr/bin/env python3
"""测试 Phase 3 的功能

验证 PropertyController、ToolManager、ViewStateMachine 是否正常工作。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QGraphicsScene
from PySide6.QtGui import QUndoStack, QColor

from app.controllers.property_controller import PropertyController
from app.managers.tool_manager import ToolManager
from app.state.view_state import ViewStateMachine, ViewState
from app.core.selection import SelectionManager
from app.core.styles import StyleManager
from app.core.shapes.circle_item import CircleItem
from app.utils.logging_config import setup_logging, get_logger


def test_property_controller():
    """测试 PropertyController"""
    print("\n" + "="*60)
    print("测试 1: PropertyController")
    print("="*60)
    
    logger = get_logger('test_property_controller')
    
    # 创建依赖
    scene = QGraphicsScene()
    undo_stack = QUndoStack()
    selection_mgr = SelectionManager(scene)
    style_mgr = StyleManager()
    
    # 创建控制器
    controller = PropertyController(selection_mgr, style_mgr, undo_stack)
    logger.info("PropertyController 创建成功")
    print("✅ PropertyController 初始化")
    
    # 创建并选中图形
    circle = CircleItem(100, 100, 50)
    scene.addItem(circle)
    selection_mgr.select([circle])
    
    # 测试更新颜色
    new_color = QColor("#FF0000")
    assert controller.update_pen_color(new_color)
    assert circle.pen().color() == new_color
    print("✅ 更新画笔颜色")
    
    # 测试撤销
    undo_stack.undo()
    assert circle.pen().color() != new_color
    print("✅ 撤销功能")
    
    # 测试重做
    undo_stack.redo()
    assert circle.pen().color() == new_color
    print("✅ 重做功能")
    
    # 测试更新宽度
    assert controller.update_pen_width(5.0)
    assert circle.pen().widthF() == 5.0
    print("✅ 更新画笔宽度")
    
    # 测试更新不透明度
    assert controller.update_opacity(0.5)
    assert circle.opacity() == 0.5
    print("✅ 更新不透明度")
    
    logger.info("PropertyController 所有功能测试通过")
    print("✅ PropertyController 模块测试通过")
    return True


def test_tool_manager():
    """测试 ToolManager"""
    print("\n" + "="*60)
    print("测试 2: ToolManager")
    print("="*60)
    
    logger = get_logger('test_tool_manager')
    
    # 创建管理器
    tool_mgr = ToolManager()
    logger.info("ToolManager 创建成功")
    print("✅ ToolManager 初始化")
    
    # 测试工具切换
    assert tool_mgr.set_tool("circle")
    assert tool_mgr.get_current_tool_name() == "circle"
    print("✅ 切换到圆形工具")
    
    assert tool_mgr.set_tool("brush_pen")
    assert tool_mgr.get_current_tool_name() == "brush_pen"
    print("✅ 切换到画笔工具")
    
    assert tool_mgr.set_tool("select")
    assert tool_mgr.get_current_tool_name() == "select"
    assert tool_mgr.get_current_tool() is None
    print("✅ 切换到选择工具")
    
    # 测试工具查询
    circle_tool = tool_mgr.get_tool("circle")
    assert circle_tool is not None
    print("✅ 获取工具实例")
    
    # 测试工具数量
    tools = tool_mgr.tools
    assert len(tools) > 0
    print(f"✅ 注册了 {len(tools)} 个工具")
    
    logger.info("ToolManager 所有功能测试通过")
    print("✅ ToolManager 模块测试通过")
    return True


def test_view_state_machine():
    """测试 ViewStateMachine"""
    print("\n" + "="*60)
    print("测试 3: ViewStateMachine")
    print("="*60)
    
    logger = get_logger('test_view_state_machine')
    
    # 创建状态机
    state_machine = ViewStateMachine()
    logger.info("ViewStateMachine 创建成功")
    print("✅ ViewStateMachine 初始化")
    
    # 测试初始状态
    assert state_machine.get_current_state() == ViewState.IDLE
    assert state_machine.is_idle()
    print("✅ 初始状态为 IDLE")
    
    # 测试状态转换
    assert state_machine.start_drawing()
    assert state_machine.is_in_state(ViewState.DRAWING)
    assert state_machine.is_busy()
    print("✅ 转换到 DRAWING 状态")
    
    assert state_machine.finish_operation()
    assert state_machine.is_idle()
    print("✅ 返回 IDLE 状态")
    
    # 测试其他状态
    assert state_machine.start_dragging()
    assert state_machine.is_in_state(ViewState.DRAGGING)
    print("✅ 转换到 DRAGGING 状态")
    
    assert state_machine.finish_operation()
    
    assert state_machine.start_rubber_band()
    assert state_machine.is_in_state(ViewState.RUBBER_BAND)
    print("✅ 转换到 RUBBER_BAND 状态")
    
    # 测试非法转换
    state_machine.reset()
    state_machine.start_drawing()
    # DRAWING 不能直接转到 DRAGGING
    assert not state_machine.start_dragging()
    print("✅ 非法转换被阻止")
    
    # 测试强制转换
    state_machine.force_transition_to(ViewState.IDLE)
    assert state_machine.is_idle()
    print("✅ 强制转换")
    
    # 测试处理器注册
    entered = []
    exited = []
    
    def on_enter():
        entered.append(True)
    
    def on_exit():
        exited.append(True)
    
    state_machine.register_enter_handler(ViewState.DRAWING, on_enter)
    state_machine.register_exit_handler(ViewState.DRAWING, on_exit)
    
    state_machine.start_drawing()
    assert len(entered) == 1
    print("✅ 进入处理器执行")
    
    state_machine.finish_operation()
    assert len(exited) == 1
    print("✅ 退出处理器执行")
    
    logger.info("ViewStateMachine 所有功能测试通过")
    print("✅ ViewStateMachine 模块测试通过")
    return True


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Phase 3 功能测试")
    print("="*60)
    
    # 初始化日志
    setup_logging(log_file="test_phase3.log", log_to_console=False)
    
    # 创建 Qt 应用
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    results = []
    
    # 运行所有测试
    try:
        results.append(("PropertyController", test_property_controller()))
        results.append(("ToolManager", test_tool_manager()))
        results.append(("ViewStateMachine", test_view_state_machine()))
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
        print("\n🎉 所有测试通过！Phase 3 的新模块功能正常。")
        print("\n下一步: 完成任务 11 - 重构 MainWindow")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
