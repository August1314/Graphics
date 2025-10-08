"""测试日志系统

验证日志配置和功能是否正常工作。
"""

from __future__ import annotations

import logging
import pytest
from pathlib import Path

from app.utils.logging_config import setup_logging, get_logger


class TestLoggingConfig:
    """测试日志配置"""
    
    def test_setup_logging_creates_logger(self, tmp_path):
        """测试 setup_logging 创建日志器"""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level=logging.DEBUG,
            log_file=str(log_file),
            log_to_console=False,
            log_to_file=True
        )
        
        assert logger is not None
        assert logger.name == 'drawing_app'
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_creates_log_file(self, tmp_path):
        """测试日志文件创建"""
        log_file = tmp_path / "test.log"
        logger = setup_logging(
            level=logging.INFO,
            log_file=str(log_file),
            log_to_console=False,
            log_to_file=True
        )
        
        # 写入一条日志
        logger.info("测试日志")
        
        # 验证文件存在且包含内容
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "测试日志" in content
    
    def test_get_logger_returns_child_logger(self):
        """测试 get_logger 返回子日志器"""
        logger = get_logger('test_module')
        
        assert logger is not None
        assert logger.name == 'drawing_app.test_module'
    
    def test_logging_levels(self, tmp_path):
        """测试不同日志级别"""
        log_file = tmp_path / "levels.log"
        logger = setup_logging(
            level=logging.WARNING,
            log_file=str(log_file),
            log_to_console=False,
            log_to_file=True
        )
        
        # 写入不同级别的日志
        logger.debug("调试信息")  # 不应记录
        logger.info("信息")  # 不应记录
        logger.warning("警告")  # 应记录
        logger.error("错误")  # 应记录
        
        content = log_file.read_text(encoding='utf-8')
        assert "调试信息" not in content
        assert "信息" not in content
        assert "警告" in content
        assert "错误" in content
