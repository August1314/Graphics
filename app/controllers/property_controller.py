"""属性控制器

统一处理属性面板和图形属性的交互，消除 MainWindow 中的重复代码。
"""

from __future__ import annotations

import logging
from typing import Optional, Callable, Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPen, QBrush, QUndoStack
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsItem

from app.core.selection import SelectionManager
from app.core.styles import StyleManager
from app.core.commands.update_style_cmd import UpdateStyleCommand

logger = logging.getLogger('drawing_app.controllers.property')


class PropertyController(QObject):
    """属性控制器
    
    统一处理属性更新，自动创建撤销命令，避免代码重复。
    
    Signals:
        property_updated: 属性更新时发出 (str, Any)
    """
    
    property_updated = Signal(str, object)
    
    def __init__(
        self,
        selection_mgr: SelectionManager,
        style_mgr: StyleManager,
        undo_stack: QUndoStack,
        parent: Optional[QObject] = None
    ):
        """初始化属性控制器
        
        Args:
            selection_mgr: 选择管理器
            style_mgr: 样式管理器
            undo_stack: 撤销栈
            parent: 父对象
        """
        super().__init__(parent)
        
        self._selection_mgr = selection_mgr
        self._style_mgr = style_mgr
        self._undo_stack = undo_stack
        
        logger.debug("属性控制器初始化完成")
    
    # ==================== 通用属性更新 ====================
    
    def update_property(
        self,
        property_name: str,
        new_value: Any,
        apply_func: Callable[[QGraphicsItem, Any], None],
        get_old_value_func: Callable[[QGraphicsItem], Any],
        description: str = "修改属性"
    ) -> bool:
        """通用属性更新方法（模板方法）
        
        Args:
            property_name: 属性名称
            new_value: 新值
            apply_func: 应用函数 (item, value) -> None
            get_old_value_func: 获取旧值函数 (item) -> value
            description: 操作描述
        
        Returns:
            是否成功更新
        """
        selected = self._selection_mgr.get_selected_items()
        if not selected:
            logger.debug("没有选中的图形，跳过属性更新")
            return False
        
        # 为每个选中的图形创建撤销命令
        for item in selected:
            try:
                old_value = get_old_value_func(item)
                
                def apply():
                    apply_func(item, new_value)
                
                def revert():
                    apply_func(item, old_value)
                
                cmd = UpdateStyleCommand.make(description, apply, revert)
                self._undo_stack.push(cmd)
                
            except Exception as e:
                logger.error(f"更新属性失败: {property_name}, {e}")
                continue
        
        self.property_updated.emit(property_name, new_value)
        logger.debug(f"属性更新: {property_name} = {new_value}")
        return True
    
    # ==================== 具体属性更新方法 ====================
    
    def update_pen_color(self, color: QColor) -> bool:
        """更新画笔颜色
        
        Args:
            color: 新颜色
        
        Returns:
            是否成功
        """
        def apply(item: QGraphicsItem, value: QColor):
            if hasattr(item, 'pen') and hasattr(item, 'setPen'):
                pen = item.pen()
                pen.setColor(value)
                item.setPen(pen)
                # 更新基础样式
                if hasattr(item.scene(), 'update_base_style'):
                    item.scene().update_base_style(item)
        
        def get_old(item: QGraphicsItem) -> QColor:
            if hasattr(item, 'pen'):
                return item.pen().color()
            return QColor("#000000")
        
        return self.update_property(
            "pen_color",
            color,
            apply,
            get_old,
            "修改描边颜色"
        )
    
    def update_pen_width(self, width: float) -> bool:
        """更新画笔宽度
        
        Args:
            width: 新宽度
        
        Returns:
            是否成功
        """
        width = max(0.1, width)
        
        def apply(item: QGraphicsItem, value: float):
            if hasattr(item, 'pen') and hasattr(item, 'setPen'):
                pen = item.pen()
                pen.setWidthF(value)
                item.setPen(pen)
                if hasattr(item.scene(), 'update_base_style'):
                    item.scene().update_base_style(item)
        
        def get_old(item: QGraphicsItem) -> float:
            if hasattr(item, 'pen'):
                return item.pen().widthF()
            return 2.0
        
        return self.update_property(
            "pen_width",
            width,
            apply,
            get_old,
            "修改线宽"
        )
    
    def update_pen_style(self, style: Qt.PenStyle) -> bool:
        """更新画笔样式
        
        Args:
            style: 新样式
        
        Returns:
            是否成功
        """
        def apply(item: QGraphicsItem, value: Qt.PenStyle):
            if hasattr(item, 'pen') and hasattr(item, 'setPen'):
                pen = item.pen()
                pen.setStyle(value)
                item.setPen(pen)
                if hasattr(item.scene(), 'update_base_style'):
                    item.scene().update_base_style(item)
        
        def get_old(item: QGraphicsItem) -> Qt.PenStyle:
            if hasattr(item, 'pen'):
                return item.pen().style()
            return Qt.PenStyle.SolidLine
        
        return self.update_property(
            "pen_style",
            style,
            apply,
            get_old,
            "修改线型"
        )
    
    def update_brush_color(self, color: QColor) -> bool:
        """更新填充颜色
        
        Args:
            color: 新颜色
        
        Returns:
            是否成功
        """
        def apply(item: QGraphicsItem, value: QColor):
            if hasattr(item, 'setBrush'):
                item.setBrush(QBrush(value))
                if hasattr(item.scene(), 'update_base_style'):
                    item.scene().update_base_style(item)
        
        def get_old(item: QGraphicsItem) -> QColor:
            if hasattr(item, 'brush'):
                return item.brush().color()
            return QColor("#00000000")
        
        return self.update_property(
            "brush_color",
            color,
            apply,
            get_old,
            "修改填充颜色"
        )
    
    def update_opacity(self, opacity: float) -> bool:
        """更新不透明度
        
        Args:
            opacity: 新不透明度 (0.0-1.0)
        
        Returns:
            是否成功
        """
        opacity = max(0.0, min(1.0, opacity))
        
        def apply(item: QGraphicsItem, value: float):
            if hasattr(item, 'setOpacity'):
                item.setOpacity(value)
                if hasattr(item.scene(), 'update_base_style'):
                    item.scene().update_base_style(item)
        
        def get_old(item: QGraphicsItem) -> float:
            if hasattr(item, 'opacity'):
                return item.opacity()
            return 1.0
        
        return self.update_property(
            "opacity",
            opacity,
            apply,
            get_old,
            "修改不透明度"
        )
    
    # ==================== 几何属性更新 ====================
    
    def update_center(self, cx: float, cy: float) -> bool:
        """更新中心点（圆形、点）
        
        Args:
            cx: 中心 X 坐标
            cy: 中心 Y 坐标
        
        Returns:
            是否成功
        """
        selected = self._selection_mgr.get_selected_items()
        if not selected:
            return False
        
        item = selected[0]  # 只处理第一个
        
        # 圆形
        if hasattr(item, 'center_radius'):
            ox, oy, r = item.center_radius()
            
            def apply():
                item.set_center_radius(cx, cy, r)
            
            def revert():
                item.set_center_radius(ox, oy, r)
            
            self._undo_stack.push(UpdateStyleCommand.make("修改中心", apply, revert))
            return True
        
        # 点（使用 pos）
        if hasattr(item, 'pos') and hasattr(item, 'setPos'):
            old_pos = item.pos()
            
            def apply():
                item.setPos(cx, cy)
            
            def revert():
                item.setPos(old_pos)
            
            self._undo_stack.push(UpdateStyleCommand.make("移动点", apply, revert))
            return True
        
        return False
    
    def update_radius(self, radius: float) -> bool:
        """更新半径（圆形、点）
        
        Args:
            radius: 新半径
        
        Returns:
            是否成功
        """
        radius = max(0.1, radius)
        selected = self._selection_mgr.get_selected_items()
        if not selected:
            return False
        
        item = selected[0]
        
        # 圆形
        if hasattr(item, 'center_radius'):
            cx, cy, old_r = item.center_radius()
            
            def apply():
                item.set_center_radius(cx, cy, radius)
            
            def revert():
                item.set_center_radius(cx, cy, old_r)
            
            self._undo_stack.push(UpdateStyleCommand.make("修改半径", apply, revert))
            return True
        
        # 点（使用 rect）
        if hasattr(item, 'rect') and hasattr(item, 'setRect'):
            old_rect = item.rect()
            old_r = old_rect.width() / 2.0
            
            def apply():
                item.setRect(-radius, -radius, 2*radius, 2*radius)
            
            def revert():
                item.setRect(-old_r, -old_r, 2*old_r, 2*old_r)
            
            self._undo_stack.push(UpdateStyleCommand.make("修改点半径", apply, revert))
            return True
        
        return False
    
    def update_line_points(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """更新直线端点
        
        Args:
            x1, y1: 起点坐标
            x2, y2: 终点坐标
        
        Returns:
            是否成功
        """
        selected = self._selection_mgr.get_selected_items()
        if not selected:
            return False
        
        item = selected[0]
        
        if hasattr(item, 'line') and hasattr(item, 'set_points'):
            line = item.line()
            old = (line.x1(), line.y1(), line.x2(), line.y2())
            
            def apply():
                item.set_points(x1, y1, x2, y2)
            
            def revert():
                item.set_points(old[0], old[1], old[2], old[3])
            
            self._undo_stack.push(UpdateStyleCommand.make("修改直线", apply, revert))
            return True
        
        return False
    
    # ==================== 属性访问 ====================
    
    @property
    def selection_manager(self) -> SelectionManager:
        """获取选择管理器"""
        return self._selection_mgr
    
    @property
    def style_manager(self) -> StyleManager:
        """获取样式管理器"""
        return self._style_mgr
    
    @property
    def undo_stack(self) -> QUndoStack:
        """获取撤销栈"""
        return self._undo_stack
