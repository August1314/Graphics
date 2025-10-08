"""场景序列化模块（重构版）

提供场景数据的序列化和反序列化功能，支持版本迁移。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Type, Optional

from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem

from app.utils.exceptions import SerializationError

logger = logging.getLogger('drawing_app.serializer')


class Serializer:
    """场景序列化器
    
    负责将场景数据序列化为 JSON 格式，以及从 JSON 反序列化。
    支持版本迁移以保持向后兼容。
    """
    
    VERSION = "2.0"
    
    def __init__(self):
        """初始化序列化器"""
        self._type_registry: Dict[str, Type] = {}
        self._register_types()
        logger.debug("序列化器初始化完成")
    
    def _register_types(self) -> None:
        """注册可序列化的图形类型"""
        try:
            from app.core.shapes.circle_item import CircleItem
            from app.core.shapes.line_item import LineItem
            from app.core.shapes.rect_item import RectItem
            from app.core.shapes.polygon_item import PolygonItem
            from app.core.shapes.point_item import PointItem
            from app.core.shapes.brush_path_item import BrushPathItem
            
            self._type_registry['circle'] = CircleItem
            self._type_registry['line'] = LineItem
            self._type_registry['rect'] = RectItem
            self._type_registry['polygon'] = PolygonItem
            self._type_registry['point'] = PointItem
            self._type_registry['brush_path'] = BrushPathItem
            
            logger.debug(f"注册了 {len(self._type_registry)} 个图形类型")
        except ImportError as e:
            logger.error(f"注册图形类型失败: {e}")
    
    def serialize(self, scene: QGraphicsScene) -> Dict[str, Any]:
        """序列化场景
        
        Args:
            scene: 要序列化的场景
        
        Returns:
            序列化后的数据字典
        
        Raises:
            SerializationError: 序列化失败
        """
        logger.debug("开始序列化场景")
        
        try:
            shapes: List[Dict[str, Any]] = []
            items = list(scene.items())
            
            # 保存前取消所有选中状态
            selected_items = scene.selectedItems()
            for item in selected_items:
                item.setSelected(False)
            
            # 序列化每个图形
            for item in items:
                try:
                    shape_data = self._serialize_item(item)
                    if shape_data:
                        shapes.append(shape_data)
                except Exception as e:
                    logger.warning(f"序列化图形失败: {type(item).__name__}, {e}")
                    continue
            
            # 恢复选中状态
            for item in selected_items:
                if item.scene() == scene:
                    item.setSelected(True)
            
            result = {
                "version": self.VERSION,
                "canvas": {
                    "width": int(scene.sceneRect().width()),
                    "height": int(scene.sceneRect().height())
                },
                "shapes": shapes
            }
            
            logger.info(f"场景序列化完成，共 {len(shapes)} 个图形")
            return result
            
        except Exception as e:
            raise SerializationError(f"场景序列化失败: {e}")
    
    def _serialize_item(self, item: QGraphicsItem) -> Optional[Dict[str, Any]]:
        """序列化单个图形
        
        Args:
            item: 图形项
        
        Returns:
            序列化后的数据，如果无法序列化则返回 None
        """
        # 检查是否有 to_dict 方法
        if hasattr(item, 'to_dict') and callable(item.to_dict):
            try:
                data = item.to_dict()
                if data and isinstance(data, dict):
                    # 确保有 type 字段
                    if 'type' not in data:
                        logger.warning(f"图形 {type(item).__name__} 的 to_dict() 缺少 type 字段")
                    return data
            except Exception as e:
                logger.error(f"调用 to_dict() 失败: {type(item).__name__}, {e}")
        
        # 尝试通过类型识别
        type_name = type(item).__name__
        
        # 使用 isinstance 检查已注册的类型
        for registered_type_name, registered_class in self._type_registry.items():
            if isinstance(item, registered_class):
                if hasattr(item, 'to_dict'):
                    try:
                        data = item.to_dict()
                        if data:
                            return data
                    except Exception as e:
                        logger.error(f"序列化 {registered_type_name} 失败: {e}")
                break
        
        logger.debug(f"无法序列化图形: {type_name}")
        return None
    
    def deserialize(
        self,
        data: Dict[str, Any],
        scene: QGraphicsScene
    ) -> List[QGraphicsItem]:
        """反序列化场景
        
        Args:
            data: 序列化的数据
            scene: 目标场景
        
        Returns:
            创建的图形列表
        
        Raises:
            SerializationError: 反序列化失败
        """
        logger.debug("开始反序列化场景")
        
        try:
            # 检查版本并迁移
            version = data.get("version", "1.0")
            if version != self.VERSION:
                logger.info(f"检测到旧版本数据 ({version})，进行迁移")
                data = self._migrate_version(data, version)
            
            # 临时阻止场景信号
            scene.blockSignals(True)
            
            created: List[QGraphicsItem] = []
            shapes = data.get("shapes", [])
            
            for shape_data in shapes:
                try:
                    item = self._deserialize_item(shape_data, scene)
                    if item:
                        created.append(item)
                except Exception as e:
                    logger.warning(f"反序列化图形失败: {e}")
                    continue
            
            # 恢复场景信号
            scene.blockSignals(False)
            
            # 取消所有选中状态
            for item in created:
                item.setSelected(False)
            
            logger.info(f"场景反序列化完成，创建了 {len(created)} 个图形")
            return created
            
        except Exception as e:
            scene.blockSignals(False)
            raise SerializationError(f"场景反序列化失败: {e}")
    
    def _deserialize_item(
        self,
        data: Dict[str, Any],
        scene: QGraphicsScene
    ) -> Optional[QGraphicsItem]:
        """反序列化单个图形
        
        Args:
            data: 图形数据
            scene: 目标场景
        
        Returns:
            创建的图形项，如果失败则返回 None
        """
        shape_type = data.get("type")
        if not shape_type:
            logger.warning("图形数据缺少 type 字段")
            return None
        
        # 查找对应的类
        shape_class = self._type_registry.get(shape_type)
        if not shape_class:
            logger.warning(f"未注册的图形类型: {shape_type}")
            return None
        
        # 使用 from_dict 创建图形
        if hasattr(shape_class, 'from_dict') and callable(shape_class.from_dict):
            try:
                item = shape_class.from_dict(data)
                scene.addItem(item)
                
                # 应用样式（如果 from_dict 没有处理）
                if "pen" in data and hasattr(item, 'setPen'):
                    self._apply_pen(item, data["pen"])
                
                return item
            except Exception as e:
                logger.error(f"从字典创建 {shape_type} 失败: {e}")
        else:
            logger.warning(f"图形类 {shape_class.__name__} 没有 from_dict 方法")
        
        return None
    
    def _migrate_version(
        self,
        data: Dict[str, Any],
        from_version: str
    ) -> Dict[str, Any]:
        """迁移数据版本
        
        Args:
            data: 原始数据
            from_version: 源版本
        
        Returns:
            迁移后的数据
        """
        if from_version == "1.0":
            logger.debug("从 v1.0 迁移到 v2.0")
            data = self._migrate_v1_to_v2(data)
        
        return data
    
    def _migrate_v1_to_v2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """从 v1.0 迁移到 v2.0
        
        Args:
            data: v1.0 数据
        
        Returns:
            v2.0 数据
        """
        # 更新版本号
        data["version"] = "2.0"
        
        # 确保有 metadata 字段
        if "metadata" not in data:
            data["metadata"] = {}
        
        # 为每个图形添加 ID（如果没有）
        import uuid
        for shape in data.get("shapes", []):
            if "id" not in shape:
                shape["id"] = str(uuid.uuid4())
        
        return data
    
    # ==================== 辅助方法 ====================
    
    @staticmethod
    def _encode_color(color: QColor) -> str:
        """编码颜色为字符串"""
        return color.name(QColor.NameFormat.HexArgb)
    
    @staticmethod
    def _decode_color(color_str: str) -> QColor:
        """解码颜色字符串"""
        try:
            return QColor(color_str)
        except Exception:
            return QColor("#FF000000")
    
    @staticmethod
    def _encode_pen(pen: QPen) -> Dict[str, Any]:
        """编码画笔为字典"""
        return {
            "color": Serializer._encode_color(pen.color()),
            "width": float(pen.widthF()),
            "style": int(pen.style().value)
        }
    
    @staticmethod
    def _apply_pen(item: QGraphicsItem, pen_data: Dict[str, Any]) -> None:
        """应用画笔数据到图形"""
        if not hasattr(item, 'pen') or not hasattr(item, 'setPen'):
            return
        
        pen = item.pen()
        
        if "color" in pen_data:
            pen.setColor(Serializer._decode_color(str(pen_data["color"])))
        
        if "width" in pen_data:
            try:
                pen.setWidthF(float(pen_data["width"]))
            except (ValueError, TypeError):
                pass
        
        if "style" in pen_data:
            try:
                pen.setStyle(Qt.PenStyle(int(pen_data["style"])))
            except (ValueError, TypeError):
                pass
        
        item.setPen(pen)
