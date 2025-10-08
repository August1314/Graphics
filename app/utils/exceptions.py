"""自定义异常类

定义应用程序的异常层次结构，便于精确的错误处理和日志记录。
"""

from __future__ import annotations


class DrawingAppException(Exception):
    """应用基础异常类
    
    所有应用特定的异常都应继承此类。
    """
    pass


class SerializationError(DrawingAppException):
    """序列化/反序列化错误
    
    当保存或加载场景数据失败时抛出。
    """
    pass


class FileOperationError(DrawingAppException):
    """文件操作错误
    
    当文件读写操作失败时抛出。
    """
    pass


class ValidationError(DrawingAppException):
    """数据验证错误
    
    当数据格式或内容不符合预期时抛出。
    """
    pass


class ToolError(DrawingAppException):
    """工具操作错误
    
    当工具执行过程中发生错误时抛出。
    """
    pass


class StateError(DrawingAppException):
    """状态错误
    
    当应用状态不一致或状态转换非法时抛出。
    """
    pass
