"""视图状态机

使用状态机模式统一管理视图状态。
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, Set, Optional, Callable

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger('drawing_app.state.view')


class ViewState(Enum):
    """视图状态枚举"""
    IDLE = "idle"                      # 空闲（选择模式）
    DRAWING = "drawing"                # 正在绘制
    DRAGGING = "dragging"              # 正在拖动图形
    RUBBER_BAND = "rubber_band"        # 框选中
    PANNING = "panning"                # 平移中
    PASTE_PENDING = "paste_pending"    # 等待粘贴
    EDITING = "editing"                # 编辑模式


class ViewStateMachine(QObject):
    """视图状态机
    
    管理视图的状态转换，确保状态一致性。
    
    Signals:
        state_changed: 状态变化时发出 (ViewState, ViewState)  # (old, new)
        state_entered: 进入状态时发出 (ViewState)
        state_exited: 退出状态时发出 (ViewState)
    """
    
    state_changed = Signal(object, object)
    state_entered = Signal(object)
    state_exited = Signal(object)
    
    def __init__(self, parent: Optional[QObject] = None):
        """初始化状态机
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        
        self._current_state = ViewState.IDLE
        self._previous_state: Optional[ViewState] = None
        
        # 状态转换规则：当前状态 -> 允许转换到的状态集合
        self._transitions: Dict[ViewState, Set[ViewState]] = {
            ViewState.IDLE: {
                ViewState.DRAWING,
                ViewState.DRAGGING,
                ViewState.RUBBER_BAND,
                ViewState.PANNING,
                ViewState.PASTE_PENDING,
                ViewState.EDITING
            },
            ViewState.DRAWING: {ViewState.IDLE},
            ViewState.DRAGGING: {ViewState.IDLE},
            ViewState.RUBBER_BAND: {ViewState.IDLE},
            ViewState.PANNING: {ViewState.IDLE},
            ViewState.PASTE_PENDING: {ViewState.IDLE},
            ViewState.EDITING: {ViewState.IDLE}
        }
        
        # 状态进入/退出处理器
        self._enter_handlers: Dict[ViewState, list] = {}
        self._exit_handlers: Dict[ViewState, list] = {}
        
        logger.debug("视图状态机初始化完成")
    
    def transition_to(self, new_state: ViewState) -> bool:
        """转换到新状态
        
        Args:
            new_state: 目标状态
        
        Returns:
            是否成功转换
        """
        # 检查是否允许转换
        if not self._can_transition(self._current_state, new_state):
            logger.warning(
                f"不允许的状态转换: {self._current_state.value} -> {new_state.value}"
            )
            return False
        
        # 相同状态，不需要转换
        if self._current_state == new_state:
            return True
        
        old_state = self._current_state
        
        # 退出当前状态
        self._exit_state(old_state)
        
        # 更新状态
        self._previous_state = old_state
        self._current_state = new_state
        
        # 进入新状态
        self._enter_state(new_state)
        
        # 发出信号
        self.state_changed.emit(old_state, new_state)
        
        logger.debug(f"状态转换: {old_state.value} -> {new_state.value}")
        return True
    
    def force_transition_to(self, new_state: ViewState) -> None:
        """强制转换到新状态（忽略转换规则）
        
        Args:
            new_state: 目标状态
        """
        if self._current_state == new_state:
            return
        
        old_state = self._current_state
        
        self._exit_state(old_state)
        self._previous_state = old_state
        self._current_state = new_state
        self._enter_state(new_state)
        
        self.state_changed.emit(old_state, new_state)
        
        logger.warning(f"强制状态转换: {old_state.value} -> {new_state.value}")
    
    def reset(self) -> None:
        """重置到 IDLE 状态"""
        if self._current_state != ViewState.IDLE:
            self.force_transition_to(ViewState.IDLE)
            logger.debug("状态机重置到 IDLE")
    
    def get_current_state(self) -> ViewState:
        """获取当前状态
        
        Returns:
            当前状态
        """
        return self._current_state
    
    def get_previous_state(self) -> Optional[ViewState]:
        """获取前一个状态
        
        Returns:
            前一个状态，如果没有则返回 None
        """
        return self._previous_state
    
    def is_in_state(self, state: ViewState) -> bool:
        """检查是否处于指定状态
        
        Args:
            state: 要检查的状态
        
        Returns:
            是否处于该状态
        """
        return self._current_state == state
    
    def is_idle(self) -> bool:
        """是否处于空闲状态
        
        Returns:
            是否空闲
        """
        return self._current_state == ViewState.IDLE
    
    def is_busy(self) -> bool:
        """是否处于忙碌状态（非空闲）
        
        Returns:
            是否忙碌
        """
        return self._current_state != ViewState.IDLE
    
    # ==================== 状态处理器注册 ====================
    
    def register_enter_handler(
        self,
        state: ViewState,
        handler: Callable[[], None]
    ) -> None:
        """注册状态进入处理器
        
        Args:
            state: 状态
            handler: 处理函数
        """
        if state not in self._enter_handlers:
            self._enter_handlers[state] = []
        self._enter_handlers[state].append(handler)
        logger.debug(f"注册进入处理器: {state.value}")
    
    def register_exit_handler(
        self,
        state: ViewState,
        handler: Callable[[], None]
    ) -> None:
        """注册状态退出处理器
        
        Args:
            state: 状态
            handler: 处理函数
        """
        if state not in self._exit_handlers:
            self._exit_handlers[state] = []
        self._exit_handlers[state].append(handler)
        logger.debug(f"注册退出处理器: {state.value}")
    
    # ==================== 内部方法 ====================
    
    def _can_transition(self, from_state: ViewState, to_state: ViewState) -> bool:
        """检查是否允许状态转换
        
        Args:
            from_state: 源状态
            to_state: 目标状态
        
        Returns:
            是否允许转换
        """
        allowed_states = self._transitions.get(from_state, set())
        return to_state in allowed_states
    
    def _enter_state(self, state: ViewState) -> None:
        """进入状态
        
        Args:
            state: 状态
        """
        # 执行进入处理器
        handlers = self._enter_handlers.get(state, [])
        for handler in handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"状态进入处理器执行失败: {state.value}, {e}")
        
        # 发出信号
        self.state_entered.emit(state)
        
        logger.debug(f"进入状态: {state.value}")
    
    def _exit_state(self, state: ViewState) -> None:
        """退出状态
        
        Args:
            state: 状态
        """
        # 执行退出处理器
        handlers = self._exit_handlers.get(state, [])
        for handler in handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"状态退出处理器执行失败: {state.value}, {e}")
        
        # 发出信号
        self.state_exited.emit(state)
        
        logger.debug(f"退出状态: {state.value}")
    
    # ==================== 便捷方法 ====================
    
    def start_drawing(self) -> bool:
        """开始绘制"""
        return self.transition_to(ViewState.DRAWING)
    
    def start_dragging(self) -> bool:
        """开始拖动"""
        return self.transition_to(ViewState.DRAGGING)
    
    def start_rubber_band(self) -> bool:
        """开始框选"""
        return self.transition_to(ViewState.RUBBER_BAND)
    
    def start_panning(self) -> bool:
        """开始平移"""
        return self.transition_to(ViewState.PANNING)
    
    def start_paste_pending(self) -> bool:
        """开始等待粘贴"""
        return self.transition_to(ViewState.PASTE_PENDING)
    
    def start_editing(self) -> bool:
        """开始编辑"""
        return self.transition_to(ViewState.EDITING)
    
    def finish_operation(self) -> bool:
        """完成操作，返回 IDLE"""
        return self.transition_to(ViewState.IDLE)
