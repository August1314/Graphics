"""文档控制器

处理文档相关的操作（保存、加载、导出等）。
"""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from app.core.document import Document
from app.utils.error_handler import handle_errors

logger = logging.getLogger('drawing_app.controllers.document')


class DocumentController(QObject):
    """文档控制器
    
    统一处理文档操作，简化 MainWindow 的职责。
    
    Signals:
        document_saved: 文档保存成功时发出 (str)
        document_loaded: 文档加载成功时发出 (str)
        status_message: 状态消息 (str)
    """
    
    document_saved = Signal(str)
    document_loaded = Signal(str)
    status_message = Signal(str)
    
    def __init__(
        self,
        document: Document,
        parent_widget: Optional[QWidget] = None,
        parent: Optional[QObject] = None
    ):
        """初始化文档控制器
        
        Args:
            document: 文档对象
            parent_widget: 父窗口（用于对话框）
            parent: 父对象
        """
        super().__init__(parent)
        
        self._document = document
        self._parent_widget = parent_widget
        
        # 连接文档信号
        self._document.saved.connect(self._on_document_saved)
        self._document.loaded.connect(self._on_document_loaded)
        
        logger.debug("文档控制器初始化完成")
    
    # ==================== 文档操作 ====================
    
    def new_document(self) -> None:
        """创建新文档"""
        # 检查是否需要保存
        if self._document.is_modified():
            reply = QMessageBox.question(
                self._parent_widget,
                "保存更改",
                "文档已修改，是否保存？",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                if not self.save_document():
                    return
            elif reply == QMessageBox.Cancel:
                return
        
        self._document.new()
        self.status_message.emit("新建文档")
        logger.info("创建新文档")
    
    def save_document(self, path: Optional[str] = None) -> bool:
        """保存文档
        
        Args:
            path: 保存路径，如果为 None 则使用当前路径或弹出对话框
        
        Returns:
            是否保存成功
        """
        # 确定保存路径
        save_path = path or self._document.get_file_path()
        
        if not save_path:
            save_path, _ = QFileDialog.getSaveFileName(
                self._parent_widget,
                "保存文件",
                "scene.json",
                "JSON 文件 (*.json)"
            )
            
            if not save_path:
                return False
        
        # 保存
        success = self._document.save(save_path)
        
        if success:
            self.status_message.emit(f"已保存: {save_path}")
        
        return success
    
    def save_document_as(self) -> bool:
        """另存为
        
        Returns:
            是否保存成功
        """
        path, _ = QFileDialog.getSaveFileName(
            self._parent_widget,
            "另存为",
            "scene.json",
            "JSON 文件 (*.json)"
        )
        
        if not path:
            return False
        
        return self.save_document(path)
    
    def load_document(self, path: Optional[str] = None) -> bool:
        """加载文档
        
        Args:
            path: 文件路径，如果为 None 则弹出对话框
        
        Returns:
            是否加载成功
        """
        # 检查是否需要保存当前文档
        if self._document.is_modified():
            reply = QMessageBox.question(
                self._parent_widget,
                "保存更改",
                "当前文档已修改，是否保存？",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                if not self.save_document():
                    return False
            elif reply == QMessageBox.Cancel:
                return False
        
        # 选择文件
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self._parent_widget,
                "打开文件",
                "",
                "JSON 文件 (*.json)"
            )
            
            if not path:
                return False
        
        # 加载
        success = self._document.load(path)
        
        if success:
            self.status_message.emit(f"已加载: {path}")
        
        return success
    
    def export_png(self, path: Optional[str] = None) -> bool:
        """导出为 PNG
        
        Args:
            path: 导出路径，如果为 None 则弹出对话框
        
        Returns:
            是否导出成功
        """
        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self._parent_widget,
                "导出 PNG",
                "scene.png",
                "PNG 文件 (*.png)"
            )
            
            if not path:
                return False
        
        success = self._document.export_png(path)
        
        if success:
            self.status_message.emit(f"已导出: {path}")
        
        return success
    
    # ==================== 内部方法 ====================
    
    def _on_document_saved(self, path: str) -> None:
        """文档保存成功的回调"""
        self.document_saved.emit(path)
        logger.info(f"文档已保存: {path}")
    
    def _on_document_loaded(self, path: str) -> None:
        """文档加载成功的回调"""
        self.document_loaded.emit(path)
        logger.info(f"文档已加载: {path}")
    
    # ==================== 属性访问 ====================
    
    @property
    def document(self) -> Document:
        """获取文档对象"""
        return self._document
