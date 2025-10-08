"""测试异常类

验证自定义异常类的层次结构。
"""

from __future__ import annotations

import pytest

from app.utils.exceptions import (
    DrawingAppException,
    SerializationError,
    FileOperationError,
    ValidationError,
    ToolError,
    StateError
)


class TestExceptions:
    """测试异常类"""
    
    def test_base_exception(self):
        """测试基础异常类"""
        exc = DrawingAppException("测试错误")
        assert str(exc) == "测试错误"
        assert isinstance(exc, Exception)
    
    def test_serialization_error(self):
        """测试序列化错误"""
        exc = SerializationError("序列化失败")
        assert isinstance(exc, DrawingAppException)
        assert isinstance(exc, Exception)
    
    def test_file_operation_error(self):
        """测试文件操作错误"""
        exc = FileOperationError("文件读取失败")
        assert isinstance(exc, DrawingAppException)
    
    def test_validation_error(self):
        """测试验证错误"""
        exc = ValidationError("数据格式错误")
        assert isinstance(exc, DrawingAppException)
    
    def test_tool_error(self):
        """测试工具错误"""
        exc = ToolError("工具执行失败")
        assert isinstance(exc, DrawingAppException)
    
    def test_state_error(self):
        """测试状态错误"""
        exc = StateError("状态不一致")
        assert isinstance(exc, DrawingAppException)
    
    def test_exception_can_be_raised(self):
        """测试异常可以被抛出和捕获"""
        with pytest.raises(SerializationError) as exc_info:
            raise SerializationError("测试")
        
        assert "测试" in str(exc_info.value)
    
    def test_exception_hierarchy(self):
        """测试异常层次结构"""
        # 可以用基类捕获子类异常
        try:
            raise SerializationError("测试")
        except DrawingAppException:
            pass  # 应该能捕获
        else:
            pytest.fail("应该捕获 SerializationError")
