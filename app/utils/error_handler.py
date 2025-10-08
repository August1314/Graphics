"""错误处理工具

提供统一的错误处理装饰器和工具函数。
"""

from __future__ import annotations

import logging
import traceback
from functools import wraps
from typing import Callable, Optional, Any, TypeVar

from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.exceptions import DrawingAppException

logger = logging.getLogger('drawing_app.error_handler')

# 类型变量用于保持函数签名
F = TypeVar('F', bound=Callable[..., Any])


def handle_errors(
    error_msg: str,
    show_dialog: bool = True,
    parent: Optional[QWidget] = None,
    return_value: Any = None
) -> Callable[[F], F]:
    """统一错误处理装饰器
    
    捕获函数执行过程中的异常，记录日志并可选地显示错误对话框。
    
    Args:
        error_msg: 错误消息前缀
        show_dialog: 是否显示错误对话框
        parent: 对话框的父窗口
        return_value: 发生错误时的返回值
    
    Returns:
        装饰器函数
    
    Example:
        @handle_errors("保存文件失败")
        def save_file(self, path: str) -> bool:
            # 实现
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except DrawingAppException as e:
                # 应用特定异常
                logger.error(f"{error_msg}: {e}", exc_info=True)
                if show_dialog:
                    _show_error_dialog(
                        parent or _get_parent_from_args(args),
                        "错误",
                        f"{error_msg}\n\n{str(e)}"
                    )
                return return_value
            except Exception as e:
                # 未预期的异常
                logger.critical(
                    f"未预期的错误 - {error_msg}: {e}",
                    exc_info=True
                )
                if show_dialog:
                    _show_error_dialog(
                        parent or _get_parent_from_args(args),
                        "严重错误",
                        f"{error_msg}\n\n发生未预期的错误，请查看日志文件获取详细信息。"
                    )
                return return_value
        return wrapper  # type: ignore
    return decorator


def handle_errors_silent(
    error_msg: str,
    return_value: Any = None
) -> Callable[[F], F]:
    """静默错误处理装饰器
    
    只记录日志，不显示对话框。适用于后台操作。
    
    Args:
        error_msg: 错误消息前缀
        return_value: 发生错误时的返回值
    
    Returns:
        装饰器函数
    """
    return handle_errors(
        error_msg=error_msg,
        show_dialog=False,
        return_value=return_value
    )


def log_exception(
    msg: str,
    exc: Exception,
    level: int = logging.ERROR
) -> None:
    """记录异常日志
    
    Args:
        msg: 日志消息
        exc: 异常对象
        level: 日志级别
    """
    logger.log(
        level,
        f"{msg}: {exc}",
        exc_info=True
    )


def format_exception(exc: Exception) -> str:
    """格式化异常信息
    
    Args:
        exc: 异常对象
    
    Returns:
        格式化的异常字符串
    """
    return ''.join(traceback.format_exception(
        type(exc),
        exc,
        exc.__traceback__
    ))


def _show_error_dialog(
    parent: Optional[QWidget],
    title: str,
    message: str
) -> None:
    """显示错误对话框
    
    Args:
        parent: 父窗口
        title: 对话框标题
        message: 错误消息
    """
    try:
        QMessageBox.critical(parent, title, message)
    except Exception as e:
        # 如果显示对话框失败，至少记录日志
        logger.error(f"无法显示错误对话框: {e}")


def _get_parent_from_args(args: tuple) -> Optional[QWidget]:
    """从函数参数中尝试获取父窗口
    
    Args:
        args: 函数参数元组
    
    Returns:
        父窗口或 None
    """
    # 尝试从 self 参数获取
    if args and hasattr(args[0], 'window'):
        try:
            return args[0].window()
        except Exception:
            pass
    
    # 尝试直接使用第一个参数（如果是 QWidget）
    if args and isinstance(args[0], QWidget):
        return args[0]
    
    return None
