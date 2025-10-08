"""文档管理模块

管理绘图文档的完整生命周期，包括创建、保存、加载和状态管理。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide6.QtGui import QUndoStack, QImage, QPainter
from PySide6.QtCore import QObject, Signal, QRectF

from app.core.serializer import Serializer
from app.utils.exceptions import FileOperationError, SerializationError
from app.utils.error_handler import handle_errors

logger = logging.getLogger('drawing_app.document')


class Document(QObject):
    """文档管理类
    
    负责管理场景数据和操作历史，提供文档的保存、加载、导出等功能。
    
    Signals:
        modified_changed: 文档修改状态变化时发出 (bool)
        file_path_changed: 文件路径变化时发出 (str)
        saved: 文档保存成功时发出 (str)
        loaded: 文档加载成功时发出 (str)
    """
    
    modified_changed = Signal(bool)
    file_path_changed = Signal(str)
    saved = Signal(str)
    loaded = Signal(str)
    
    def __init__(
        self,
        scene: QGraphicsScene,
        undo_stack: QUndoStack,
        parent: Optional[QObject] = None
    ):
        """初始化文档
        
        Args:
            scene: 图形场景
            undo_stack: 撤销栈
            parent: 父对象
        """
        super().__init__(parent)
        
        self._scene = scene
        self._undo_stack = undo_stack
        self._serializer = Serializer()
        
        self._file_path: Optional[str] = None
        self._modified = False
        self._metadata: Dict[str, Any] = {}
        
        # 监听撤销栈变化，自动标记文档为已修改
        self._undo_stack.indexChanged.connect(self._on_undo_index_changed)
        
        logger.debug("文档初始化完成")
    
    # ==================== 文档操作 ====================
    
    def new(self) -> None:
        """创建新文档
        
        清空场景和撤销历史，重置文档状态。
        """
        logger.info("创建新文档")
        
        # 清空场景
        self._scene.clear()
        
        # 清空撤销历史
        self._undo_stack.clear()
        
        # 重置状态
        self._file_path = None
        self._modified = False
        self._metadata = {}
        
        self.file_path_changed.emit("")
        self.modified_changed.emit(False)
        
        logger.debug("新文档创建完成")
    
    @handle_errors("保存文档失败", show_dialog=True)
    def save(self, path: Optional[str] = None) -> bool:
        """保存文档
        
        Args:
            path: 保存路径，如果为 None 则使用当前文件路径
        
        Returns:
            是否保存成功
        
        Raises:
            FileOperationError: 文件操作失败
            SerializationError: 序列化失败
        """
        # 确定保存路径
        save_path = path or self._file_path
        if not save_path:
            raise FileOperationError("未指定保存路径")
        
        logger.info(f"保存文档到: {save_path}")
        
        try:
            # 序列化场景
            data = self._serializer.serialize(self._scene)
            
            # 添加元数据
            data['metadata'] = self._metadata
            
            # 写入文件
            save_path_obj = Path(save_path)
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path_obj, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 更新状态
            self._file_path = save_path
            self._modified = False
            
            self.file_path_changed.emit(save_path)
            self.modified_changed.emit(False)
            self.saved.emit(save_path)
            
            logger.info(f"文档保存成功: {save_path}")
            return True
            
        except json.JSONEncodeError as e:
            raise SerializationError(f"JSON 编码失败: {e}")
        except OSError as e:
            raise FileOperationError(f"文件写入失败: {e}")
    
    @handle_errors("加载文档失败", show_dialog=True)
    def load(self, path: str) -> bool:
        """加载文档
        
        Args:
            path: 文件路径
        
        Returns:
            是否加载成功
        
        Raises:
            FileOperationError: 文件操作失败
            SerializationError: 反序列化失败
        """
        logger.info(f"加载文档: {path}")
        
        try:
            # 读取文件
            path_obj = Path(path)
            if not path_obj.exists():
                raise FileOperationError(f"文件不存在: {path}")
            
            with open(path_obj, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清空当前场景
            self._scene.clear()
            self._undo_stack.clear()
            
            # 反序列化
            items = self._serializer.deserialize(data, self._scene)
            
            # 加载元数据
            self._metadata = data.get('metadata', {})
            
            # 更新状态
            self._file_path = path
            self._modified = False
            
            self.file_path_changed.emit(path)
            self.modified_changed.emit(False)
            self.loaded.emit(path)
            
            logger.info(f"文档加载成功: {path}, 加载了 {len(items)} 个图形")
            return True
            
        except json.JSONDecodeError as e:
            raise SerializationError(f"JSON 解码失败: {e}")
        except OSError as e:
            raise FileOperationError(f"文件读取失败: {e}")
    
    @handle_errors("导出 PNG 失败", show_dialog=True)
    def export_png(self, path: str, rect: Optional[QRectF] = None) -> bool:
        """导出为 PNG 图片
        
        Args:
            path: 导出路径
            rect: 导出区域，如果为 None 则导出整个场景
        
        Returns:
            是否导出成功
        
        Raises:
            FileOperationError: 文件操作失败
        """
        logger.info(f"导出 PNG 到: {path}")
        
        try:
            # 确定导出区域
            export_rect = rect or self._scene.sceneRect()
            
            # 创建图像
            width = max(1, int(export_rect.width()))
            height = max(1, int(export_rect.height()))
            
            image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(0xFFFFFFFF)  # 白色背景
            
            # 渲染场景
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._scene.render(painter, target=QRectF(0, 0, width, height), source=export_rect)
            painter.end()
            
            # 保存图像
            path_obj = Path(path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            if not image.save(str(path_obj)):
                raise FileOperationError("图像保存失败")
            
            logger.info(f"PNG 导出成功: {path}")
            return True
            
        except Exception as e:
            raise FileOperationError(f"导出失败: {e}")
    
    # ==================== 状态管理 ====================
    
    def is_modified(self) -> bool:
        """文档是否已修改
        
        Returns:
            是否已修改
        """
        return self._modified
    
    def mark_modified(self, modified: bool = True) -> None:
        """标记文档为已修改
        
        Args:
            modified: 是否已修改
        """
        if self._modified != modified:
            self._modified = modified
            self.modified_changed.emit(modified)
            logger.debug(f"文档修改状态: {modified}")
    
    def get_file_path(self) -> Optional[str]:
        """获取文件路径
        
        Returns:
            文件路径，如果未保存则返回 None
        """
        return self._file_path
    
    def set_file_path(self, path: str) -> None:
        """设置文件路径
        
        Args:
            path: 文件路径
        """
        if self._file_path != path:
            self._file_path = path
            self.file_path_changed.emit(path)
            logger.debug(f"文件路径更新: {path}")
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据
        
        Args:
            key: 键
            default: 默认值
        
        Returns:
            元数据值
        """
        return self._metadata.get(key, default)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据
        
        Args:
            key: 键
            value: 值
        """
        self._metadata[key] = value
        self.mark_modified()
        logger.debug(f"元数据更新: {key} = {value}")
    
    # ==================== 图形管理 ====================
    
    def add_shape(self, shape: QGraphicsItem) -> None:
        """添加图形到场景
        
        Args:
            shape: 图形项
        """
        self._scene.addItem(shape)
        self.mark_modified()
        logger.debug(f"添加图形: {type(shape).__name__}")
    
    def remove_shape(self, shape: QGraphicsItem) -> None:
        """从场景移除图形
        
        Args:
            shape: 图形项
        """
        if shape.scene() == self._scene:
            self._scene.removeItem(shape)
            self.mark_modified()
            logger.debug(f"移除图形: {type(shape).__name__}")
    
    def get_all_shapes(self) -> List[QGraphicsItem]:
        """获取所有图形
        
        Returns:
            图形列表
        """
        return list(self._scene.items())
    
    def get_shape_count(self) -> int:
        """获取图形数量
        
        Returns:
            图形数量
        """
        return len(self._scene.items())
    
    # ==================== 内部方法 ====================
    
    def _on_undo_index_changed(self, index: int) -> None:
        """撤销栈索引变化时的回调
        
        Args:
            index: 新的索引
        """
        # 撤销/重做操作会改变文档状态
        if not self._modified:
            self.mark_modified()
    
    # ==================== 属性访问 ====================
    
    @property
    def scene(self) -> QGraphicsScene:
        """获取场景"""
        return self._scene
    
    @property
    def undo_stack(self) -> QUndoStack:
        """获取撤销栈"""
        return self._undo_stack
    
    @property
    def serializer(self) -> Serializer:
        """获取序列化器"""
        return self._serializer
