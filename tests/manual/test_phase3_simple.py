#!/usr/bin/env python3
"""Phase 3 简化测试（不需要 Qt 应用）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试模块导入"""
    print("\n" + "="*60)
    print("测试 1: Phase 3 模块导入")
    print("="*60)
    
    try:
        from app.controllers.property_controller import PropertyController
        print("✅ PropertyController 导入成功")
        
        from app.managers.tool_manager import ToolManager
        print("✅ ToolManager 导入成功")
        
        from app.state.view_state import ViewStateMachine, ViewState
        print("✅ ViewStateMachine 导入成功")
        print("✅ ViewState 枚举导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_view_state_enum():
    """测试 ViewState 枚举"""
    print("\n" + "="*60)
    print("测试 2: ViewState 枚举")
    print("="*60)
    
    try:
        from app.state.view_state import ViewState
        
        # 测试所有状态
        states = [
            ViewState.IDLE,
            ViewState.DRAWING,
            ViewState.DRAGGING,
            ViewState.RUBBER_BAND,
            ViewState.PANNING,
            ViewState.PASTE_PENDING,
            ViewState.EDITING
        ]
        
        print(f"✅ 定义了 {len(states)} 个状态")
        
        for state in states:
            print(f"   - {state.value}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_tool_manager_basic():
    """测试 ToolManager 基础功能"""
    print("\n" + "="*60)
    print("测试 3: ToolManager 基础功能")
    print("="*60)
    
    try:
        from app.managers.tool_manager import ToolManager
        
        # 创建管理器（不传入 view）
        tool_mgr = ToolManager()
        print("✅ ToolManager 创建成功")
        
        # 检查工具注册
        tools = tool_mgr.tools
        print(f"✅ 注册了 {len(tools)} 个工具")
        
        # 列出所有工具
        for tool_name in tools.keys():
            print(f"   - {tool_name}")
        
        # 测试工具切换
        assert tool_mgr.set_tool("select")
        print("✅ 切换到选择工具")
        
        assert tool_mgr.get_current_tool_name() == "select"
        print("✅ 获取当前工具名称")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Phase 3 简化测试")
    print("="*60)
    
    results = []
    
    try:
        results.append(("模块导入", test_imports()))
        results.append(("ViewState 枚举", test_view_state_enum()))
        results.append(("ToolManager 基础", test_tool_manager_basic()))
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
        print("\n🎉 所有测试通过！Phase 3 的新模块可以正常导入和使用。")
        print("\n📊 Phase 3 进度: 75% (3/4 任务完成)")
        print("   ✅ PropertyController")
        print("   ✅ ToolManager")
        print("   ✅ ViewStateMachine")
        print("   ⏳ MainWindow 重构（待完成）")
        print("\n下一步: 完成任务 11 - 重构 MainWindow")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
