"""选择管理模块

统一管理图形的选择状态和选择相关操作。
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import List, Optional

from PySide6.QtCore import QObject, Signal, QRectF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import Qt

logger = logging.getLogger('drawing_app.selection')


class SelectionMode(Enum):
    """选择模式"""
    REPLACE = "replace"  # 替换当前选择
    ADD = "add"          # 添加到选择
    TOGGLE = "toggle"    # 切换选择状态
    REMOVE = "remove"    # 从选择中移除


class SelectionManager(QObject):
    """选择管理器
    
    统一处理图形的选择逻辑，提供选择反馈和选择状态查询。
    
    Signals:
        selection_changed: 选择变化时发出 (List[QGraphicsItem])
    """
    
    selection_changed = Signal(list)
    
    def __init__(self, scene: QGraphicsScene, parent: Optional[QObject] = None):
        """初始化选择管理器
        
        Args:
            scene: 图形场景
            parent: 父对象
        """
        super().__init__(parent)
        
        self._scene = scene
        self._selected_items: List[QGraphicsItem] = []
        self._selection_feedback_enabled = True
        
        # 监听场景的选择变化
        self._scene.selectionChanged.connect(self._on_scene_selection_changed)
        
        logger.debug("选择管理器初始化完成")
    
    # ==================== 选择操作 ====================
    
    def select(
        self,
        items: List[QGraphicsItem],
        mode: SelectionMode = SelectionMode.REPLACE
    ) -> None:
        """选择图形
        
        Args:
            items: 要选择的图形列表
            mode: 选择模式
        """
        if mode == SelectionMode.REPLACE:
            # 替换选择：先清空，再选中
            self.clear_selection()
            for item in items:
                if item.scene() == self._scene:
                    item.setSelected(True)
        
        elif mode == SelectionMode.ADD:
            # 添加到选择
            for item in items:
                if item.scene() == self._scene:
                    item.setSelected(True)
        
        elif mode == SelectionMode.TOGGLE:
            # 切换选择状态
            for item in items:
                if item.scene() == self._scene:
                    item.setSelected(not item.isSelected())
        
        elif mode == SelectionMode.REMOVE:
            # 从选择中移除
            for item in items:
                if item.scene() == self._scene and item.isSelected():
                    item.setSelected(False)
        
        logger.debug(f"选择操作: mode={mode.value}, items={len(items)}")
    
    def select_all(self) -> None:
        """选择所有图形"""
        all_items = list(self._scene.items())
        self.select(all_items, SelectionMode.REPLACE)
        logger.debug(f"选择所有图形: {len(all_items)} 个")
    
    def clear_selection(self) -> None:
        """清空选择"""
        self._scene.clearSelection()
        logger.debug("清空选择")
    
    def toggle_selection(self, item: QGraphicsItem) -> None:
        """切换图形的选择状态
        
        Args:
            item: 图形项
        """
        if item.scene() == self._scene:
            item.setSelected(not item.isSelected())
            logger.debug(f"切换选择: {type(item).__name__}")
    
    def select_in_rect(self, rect: QRectF, mode: SelectionMode = SelectionMode.REPLACE) -> None:
        """选择矩形区域内的图形
        
        Args:
            rect: 选择矩形
            mode: 选择模式
        """
        items = self._scene.items(rect)
        self.select(items, mode)
        logger.debug(f"矩形选择: {len(items)} 个图形")
    
    # ==================== 查询 ====================
    
    def get_selected_items(self) -> List[QGraphicsItem]:
        """获取选中的图形
        
        Returns:
            选中的图形列表
        """
        return list(self._scene.selectedItems())
    
    def has_selection(self) -> bool:
        """是否有选中的图形
        
        Returns:
            是否有选择
        """
        return len(self._scene.selectedItems()) > 0
    
    def get_selection_count(self) -> int:
        """获取选中图形的数量
        
        Returns:
            选中数量
        """
        return len(self._scene.selectedItems())
    
    def get_selection_bounds(self) -> QRectF:
        """获取选中图形的包围盒
        
        Returns:
            包围盒矩形
        """
        selected = self.get_selected_items()
        if not selected:
            return QRectF()
        
        # 计算所有选中图形的联合包围盒
        bounds = selected[0].sceneBoundingRect()
        for item in selected[1:]:
            bounds = bounds.united(item.sceneBoundingRect())
        
        return bounds
    
    def is_selected(self, item: QGraphicsItem) -> bool:
        """检查图形是否被选中
        
        Args:
            item: 图形项
        
        Returns:
            是否被选中
        """
        return item.isSelected()
    
    # ==================== 选择反馈 ====================
    
    def set_selection_feedback_enabled(self, enabled: bool) -> None:
        """设置是否启用选择反馈
        
        Args:
            enabled: 是否启用
        """
        self._selection_feedback_enabled = enabled
        if enabled:
            self.update_selection_feedback()
        logger.debug(f"选择反馈: {enabled}")
    
    def update_selection_feedback(self) -> None:
        """更新选择反馈
        
        为选中的图形显示视觉反馈（虚线边框）。
        """
        if not self._selection_feedback_enabled:
            return
        
        # 选择反馈由各个图形类的 paint() 方法处理
        # 这里只需要触发重绘
        for item in self.get_selected_items():
            item.update()
        
        logger.debug("更新选择反馈")
    
    # ==================== 内部方法 ====================
    
    def _on_scene_selection_changed(self) -> None:
        """场景选择变化的回调"""
        selected = self.get_selected_items()
        self._selected_items = selected
        
        # 更新选择反馈
        if self._selection_feedback_enabled:
            self.update_selection_feedback()
        
        # 发出信号
        self.selection_changed.emit(selected)
        
        logger.debug(f"选择变化: {len(selected)} 个图形")
    
    # ==================== 属性访问 ====================
    
    @property
    def scene(self) -> QGraphicsScene:
        """获取场景"""
        return self._scene
    
    @property
    def selected_items(self) -> List[QGraphicsItem]:
        """获取选中的图形（属性访问）"""
        return self._selected_items.copy()
