"""样式管理模块

统一管理图形样式的应用和更新。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List

from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import QGraphicsItem

logger = logging.getLogger('drawing_app.styles')


@dataclass
class Style:
    """样式数据类
    
    包含图形的所有样式属性。
    """
    pen_color: QColor = field(default_factory=lambda: QColor("#000000"))
    pen_width: float = 2.0
    pen_style: Qt.PenStyle = Qt.PenStyle.SolidLine
    brush_color: QColor = field(default_factory=lambda: QColor("#00000000"))
    opacity: float = 1.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "pen_color": self.pen_color.name(QColor.NameFormat.HexArgb),
            "pen_width": self.pen_width,
            "pen_style": int(self.pen_style.value),
            "brush_color": self.brush_color.name(QColor.NameFormat.HexArgb),
            "opacity": self.opacity
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Style':
        """从字典创建"""
        return cls(
            pen_color=QColor(data.get("pen_color", "#000000")),
            pen_width=float(data.get("pen_width", 2.0)),
            pen_style=Qt.PenStyle(int(data.get("pen_style", 1))),
            brush_color=QColor(data.get("brush_color", "#00000000")),
            opacity=float(data.get("opacity", 1.0))
        )


class StyleManager(QObject):
    """样式管理器
    
    统一样式应用逻辑，提供默认样式和样式缓存。
    
    Signals:
        style_changed: 样式变化时发出 (QGraphicsItem, Style)
    """
    
    style_changed = Signal(object, object)
    
    def __init__(self, parent: Optional[QObject] = None):
        """初始化样式管理器
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        
        self._default_styles: Dict[str, Style] = {}
        self._style_cache: Dict[int, Style] = {}  # item id -> style
        
        self._init_default_styles()
        
        logger.debug("样式管理器初始化完成")
    
    def _init_default_styles(self) -> None:
        """初始化默认样式"""
        # 圆形默认样式
        self._default_styles['circle'] = Style(
            pen_color=QColor("#0066cc"),
            pen_width=2.0,
            pen_style=Qt.PenStyle.SolidLine,
            brush_color=QColor("#00000000"),
            opacity=1.0
        )
        
        # 矩形默认样式
        self._default_styles['rect'] = Style(
            pen_color=QColor("#333333"),
            pen_width=2.0,
            pen_style=Qt.PenStyle.SolidLine,
            brush_color=QColor("#00000000"),
            opacity=1.0
        )
        
        # 直线默认样式
        self._default_styles['line'] = Style(
            pen_color=QColor("#333333"),
            pen_width=2.0,
            pen_style=Qt.PenStyle.SolidLine,
            brush_color=QColor("#00000000"),
            opacity=1.0
        )
        
        # 画笔默认样式
        self._default_styles['brush'] = Style(
            pen_color=QColor("#000000"),
            pen_width=3.0,
            pen_style=Qt.PenStyle.SolidLine,
            brush_color=QColor("#00000000"),
            opacity=1.0
        )
        
        logger.debug(f"初始化了 {len(self._default_styles)} 个默认样式")
    
    # ==================== 样式应用 ====================
    
    def apply_style(self, item: QGraphicsItem, style: Style) -> None:
        """应用样式到图形
        
        Args:
            item: 图形项
            style: 样式
        """
        # 应用画笔
        if hasattr(item, 'setPen'):
            pen = QPen(style.pen_color, style.pen_width)
            pen.setStyle(style.pen_style)
            item.setPen(pen)
        
        # 应用画刷
        if hasattr(item, 'setBrush'):
            brush = QBrush(style.brush_color)
            item.setBrush(brush)
        
        # 应用透明度
        if hasattr(item, 'setOpacity'):
            item.setOpacity(style.opacity)
        
        # 缓存样式
        self._style_cache[id(item)] = style
        
        # 发出信号
        self.style_changed.emit(item, style)
        
        logger.debug(f"应用样式到 {type(item).__name__}")
    
    def apply_pen(self, item: QGraphicsItem, pen: QPen) -> None:
        """应用画笔到图形
        
        Args:
            item: 图形项
            pen: 画笔
        """
        if hasattr(item, 'setPen'):
            item.setPen(pen)
            
            # 更新缓存
            item_id = id(item)
            if item_id in self._style_cache:
                style = self._style_cache[item_id]
                style.pen_color = pen.color()
                style.pen_width = pen.widthF()
                style.pen_style = pen.style()
            
            logger.debug(f"应用画笔到 {type(item).__name__}")
    
    def apply_brush(self, item: QGraphicsItem, brush: QBrush) -> None:
        """应用画刷到图形
        
        Args:
            item: 图形项
            brush: 画刷
        """
        if hasattr(item, 'setBrush'):
            item.setBrush(brush)
            
            # 更新缓存
            item_id = id(item)
            if item_id in self._style_cache:
                style = self._style_cache[item_id]
                style.brush_color = brush.color()
            
            logger.debug(f"应用画刷到 {type(item).__name__}")
    
    def apply_style_to_selection(
        self,
        items: List[QGraphicsItem],
        style: Style
    ) -> None:
        """批量应用样式到选中的图形
        
        Args:
            items: 图形列表
            style: 样式
        """
        for item in items:
            self.apply_style(item, style)
        
        logger.info(f"批量应用样式到 {len(items)} 个图形")
    
    # ==================== 样式获取 ====================
    
    def get_style(self, item: QGraphicsItem) -> Style:
        """获取图形的当前样式
        
        Args:
            item: 图形项
        
        Returns:
            样式对象
        """
        # 先查缓存
        item_id = id(item)
        if item_id in self._style_cache:
            return self._style_cache[item_id]
        
        # 从图形提取样式
        style = Style()
        
        if hasattr(item, 'pen'):
            pen = item.pen()
            style.pen_color = pen.color()
            style.pen_width = pen.widthF()
            style.pen_style = pen.style()
        
        if hasattr(item, 'brush'):
            brush = item.brush()
            style.brush_color = brush.color()
        
        if hasattr(item, 'opacity'):
            style.opacity = item.opacity()
        
        # 缓存
        self._style_cache[item_id] = style
        
        return style
    
    def get_default_style(self, shape_type: str) -> Style:
        """获取指定类型的默认样式
        
        Args:
            shape_type: 图形类型
        
        Returns:
            默认样式
        """
        return self._default_styles.get(shape_type, Style())
    
    def set_default_style(self, shape_type: str, style: Style) -> None:
        """设置默认样式
        
        Args:
            shape_type: 图形类型
            style: 样式
        """
        self._default_styles[shape_type] = style
        logger.debug(f"设置 {shape_type} 的默认样式")
    
    # ==================== 缓存管理 ====================
    
    def clear_cache(self) -> None:
        """清空样式缓存"""
        self._style_cache.clear()
        logger.debug("清空样式缓存")
    
    def remove_from_cache(self, item: QGraphicsItem) -> None:
        """从缓存中移除图形
        
        Args:
            item: 图形项
        """
        item_id = id(item)
        if item_id in self._style_cache:
            del self._style_cache[item_id]
