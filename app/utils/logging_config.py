"""日志配置模块

提供统一的日志配置和管理功能。
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    log_to_file: bool = True
) -> logging.Logger:
    """配置应用日志系统
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，默认为 'drawing_app.log'
        log_to_console: 是否输出到控制台
        log_to_file: 是否输出到文件
    
    Returns:
        配置好的根日志器
    """
    # 获取根日志器
    logger = logging.getLogger('drawing_app')
    logger.setLevel(level)
    
    # 清除已有的处理器（避免重复配置）
    logger.handlers.clear()
    
    # 日志格式
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_to_file:
        if log_file is None:
            log_file = 'drawing_app.log'
        
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # 记录日志系统初始化
    logger.info("日志系统初始化完成")
    logger.debug(f"日志级别: {logging.getLevelName(level)}")
    logger.debug(f"控制台输出: {log_to_console}")
    logger.debug(f"文件输出: {log_to_file}")
    if log_to_file:
        logger.debug(f"日志文件: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器
    
    Args:
        name: 日志器名称，通常使用模块名
    
    Returns:
        日志器实例
    
    Example:
        logger = get_logger(__name__)
        logger.info("这是一条信息")
    """
    return logging.getLogger(f'drawing_app.{name}')
