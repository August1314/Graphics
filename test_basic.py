#!/usr/bin/env python3
"""基础功能测试（不需要 Qt 应用）

测试日志、异常处理等基础功能。
"""

import sys
import logging
from pathlib import Path

# 确保可以导入 app 模块
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试模块导入"""
    print("\n" + "="*60)
    print("测试 1: 模块导入")
    print("="*60)
    
    try:
        from app.utils.logging_config import setup_logging, get_logger
        print("✅ logging_config 导入成功")
        
        from app.utils.exceptions import (
            DrawingAppException,
            SerializationError,
            FileOperationError,
            ValidationError
        )
        print("✅ exceptions 导入成功")
        
        from app.utils.error_handler import handle_errors
        print("✅ error_handler 导入成功")
        
        from app.core.document import Document
        print("✅ document 导入成功")
        
        from app.core.selection import SelectionManager, SelectionMode
        print("✅ selection 导入成功")
        
        from app.core.styles import StyleManager, Style
        print("✅ styles 导入成功")
        
        from app.core.serializer import Serializer
        print("✅ serializer 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logging():
    """测试日志系统"""
    print("\n" + "="*60)
    print("测试 2: 日志系统")
    print("="*60)
    
    try:
        from app.utils.logging_config import setup_logging, get_logger
        
        # 初始化日志
        logger = setup_logging(
            level=logging.DEBUG,
            log_file="test_basic.log",
            log_to_console=False
        )
        
        # 测试不同级别的日志
        logger.debug("调试信息")
        logger.info("普通信息")
        logger.warning("警告信息")
        logger.error("错误信息")
        
        # 获取模块日志器
        module_logger = get_logger('test_module')
        module_logger.info("模块日志器工作正常")
        
        # 检查日志文件
        log_file = Path("test_basic.log")
        if log_file.exists():
            content = log_file.read_text()
            if "调试信息" in content and "普通信息" in content:
                print("✅ 日志写入文件成功")
                print(f"   日志文件: {log_file}")
                return True
            else:
                print("❌ 日志内容不完整")
                return False
        else:
            print("❌ 日志文件未创建")
            return False
            
    except Exception as e:
        print(f"❌ 日志系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exceptions():
    """测试异常处理"""
    print("\n" + "="*60)
    print("测试 3: 异常处理")
    print("="*60)
    
    try:
        from app.utils.exceptions import (
            DrawingAppException,
            SerializationError,
            FileOperationError
        )
        from app.utils.logging_config import get_logger
        
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
        
        # 测试异常层次
        try:
            raise SerializationError("测试")
        except DrawingAppException:
            print("✅ 异常层次结构正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_style_dataclass():
    """测试 Style 数据类"""
    print("\n" + "="*60)
    print("测试 4: Style 数据类")
    print("="*60)
    
    try:
        from app.core.styles import Style
        from PySide6.QtGui import QColor
        from PySide6.QtCore import Qt
        
        # 创建样式
        style = Style(
            pen_color=QColor("#FF0000"),
            pen_width=5.0,
            pen_style=Qt.PenStyle.SolidLine,
            brush_color=QColor("#00FF0080"),
            opacity=0.8
        )
        
        print(f"✅ Style 创建成功")
        print(f"   pen_color: {style.pen_color.name()}")
        print(f"   pen_width: {style.pen_width}")
        print(f"   opacity: {style.opacity}")
        
        # 测试序列化
        data = style.to_dict()
        print(f"✅ Style.to_dict() 成功")
        
        # 测试反序列化
        style2 = Style.from_dict(data)
        print(f"✅ Style.from_dict() 成功")
        
        # 验证
        assert style2.pen_width == style.pen_width
        assert style2.opacity == style.opacity
        print(f"✅ 序列化/反序列化验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ Style 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_serializer_class():
    """测试 Serializer 类（不需要场景）"""
    print("\n" + "="*60)
    print("测试 5: Serializer 类")
    print("="*60)
    
    try:
        from app.core.serializer import Serializer
        
        # 创建序列化器
        serializer = Serializer()
        print("✅ Serializer 初始化成功")
        
        # 检查类型注册
        assert len(serializer._type_registry) > 0
        print(f"✅ 注册了 {len(serializer._type_registry)} 个图形类型")
        
        # 测试版本迁移
        old_data = {
            "version": "1.0",
            "shapes": [
                {"type": "circle", "cx": 100, "cy": 100, "r": 50}
            ]
        }
        
        migrated = serializer._migrate_version(old_data, "1.0")
        assert migrated["version"] == "2.0"
        assert "metadata" in migrated
        print("✅ 版本迁移功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ Serializer 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Phase 1 & Phase 2 基础功能测试")
    print("="*60)
    
    results = []
    
    # 运行所有测试
    try:
        results.append(("模块导入", test_imports()))
        results.append(("日志系统", test_logging()))
        results.append(("异常处理", test_exceptions()))
        results.append(("Style 数据类", test_style_dataclass()))
        results.append(("Serializer 类", test_serializer_class()))
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
        print("\n🎉 所有基础测试通过！")
        print("\n提示：要测试完整功能（包括 Qt 场景），请运行：")
        print("  python -m app.main")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
