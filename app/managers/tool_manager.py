"""工具管理器

统一管理工具的切换和状态。
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtCore import Qt

from app.core.tools.base_tool import BaseTool
from app.core.tools.circle_tool import CircleTool
from app.core.tools.point_tool import PointTool
from app.core.tools.line_tool import LineTool
from app.core.tools.rect_tool import RectTool
from app.core.tools.polygon_tool import PolygonTool
from app.core.tools.brush_tool import BrushTool
from app.core.tools.eraser_tool import EraserTool

logger = logging.getLogger('drawing_app.managers.tool')


class ToolManager(QObject):
    """工具管理器
    
    管理所有绘图工具的创建、切换和状态。
    
    Signals:
        tool_changed: 工具变化时发出 (str, BaseTool)
    """
    
    tool_changed = Signal(str, object)
    
    def __init__(self, view=None, parent: Optional[QObject] = None):
        """初始化工具管理器
        
        Args:
            view: 画布视图
            parent: 父对象
        """
        super().__init__(parent)
        
        self._view = view
        self._current_tool: Optional[BaseTool] = None
        self._current_tool_name: str = "select"
        self._tools: Dict[str, BaseTool] = {}
        
        self._register_tools()
        
        logger.debug("工具管理器初始化完成")
    
    def _register_tools(self) -> None:
        """注册所有工具"""
        # 基础工具
        self._tools['circle'] = CircleTool()
        self._tools['point'] = PointTool()
        self._tools['line'] = LineTool()
        self._tools['rect'] = RectTool()
        self._tools['polygon'] = PolygonTool()
        
        # 画笔工具
        self._tools['brush_pen'] = BrushTool(BrushTool.BrushType.PEN)
        self._tools['brush_marker'] = BrushTool(BrushTool.BrushType.MARKER)
        self._tools['brush_calligraphy'] = BrushTool(BrushTool.BrushType.CALLIGRAPHY)
        self._tools['brush_spray'] = BrushTool(BrushTool.BrushType.SPRAY)
        
        # 橡皮擦工具
        self._tools['eraser'] = EraserTool()
        
        logger.debug(f"注册了 {len(self._tools)} 个工具")
    
    def set_tool(self, tool_name: str) -> bool:
        """设置当前工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            是否成功切换
        """
        # 选择工具（无工具）
        if tool_name == "select" or tool_name is None:
            self._current_tool = None
            self._current_tool_name = "select"
            self.tool_changed.emit("select", None)
            logger.debug("切换到选择工具")
            return True
        
        # 获取工具
        tool = self._tools.get(tool_name)
        if tool is None:
            logger.warning(f"未知的工具: {tool_name}")
            return False
        
        # 取消当前工具
        if self._current_tool is not None:
            try:
                if hasattr(self._current_tool, 'cancel') and self._view:
                    self._current_tool.cancel(self._view.scene())
            except Exception as e:
                logger.error(f"取消工具失败: {e}")
        
        # 切换工具
        self._current_tool = tool
        self._current_tool_name = tool_name
        
        # 发出信号
        self.tool_changed.emit(tool_name, tool)
        
        logger.debug(f"切换到工具: {tool_name}")
        return True
    
    def get_current_tool(self) -> Optional[BaseTool]:
        """获取当前工具
        
        Returns:
            当前工具，如果是选择模式则返回 None
        """
        return self._current_tool
    
    def get_current_tool_name(self) -> str:
        """获取当前工具名称
        
        Returns:
            工具名称
        """
        return self._current_tool_name
    
    def cancel_current_tool(self) -> None:
        """取消当前工具"""
        if self._current_tool is not None and self._view is not None:
            try:
                if hasattr(self._current_tool, 'cancel'):
                    self._current_tool.cancel(self._view.scene())
                logger.debug(f"取消工具: {self._current_tool_name}")
            except Exception as e:
                logger.error(f"取消工具失败: {e}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """获取指定工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具实例，如果不存在则返回 None
        """
        return self._tools.get(tool_name)
    
    def is_tool_active(self) -> bool:
        """当前是否有激活的工具
        
        Returns:
            是否有工具激活
        """
        if self._current_tool is None:
            return False
        
        # 检查工具是否处于激活状态
        if hasattr(self._current_tool, 'is_active'):
            return self._current_tool.is_active()
        
        return False
    
    def set_view(self, view) -> None:
        """设置视图
        
        Args:
            view: 画布视图
        """
        self._view = view
        logger.debug("设置视图")
    
    # ==================== 工具配置 ====================
    
    def configure_brush_tool(self, brush_type: str, pen=None) -> None:
        """配置画笔工具
        
        Args:
            brush_type: 画笔类型
            pen: 画笔样式
        """
        tool_name = f"brush_{brush_type}"
        tool = self._tools.get(tool_name)
        
        if tool is not None and isinstance(tool, BrushTool):
            if pen is not None:
                tool.set_pen(pen)
            logger.debug(f"配置画笔工具: {brush_type}")
    
    def configure_eraser_tool(self, size: float = None, mode: str = None) -> None:
        """配置橡皮擦工具
        
        Args:
            size: 橡皮擦大小
            mode: 橡皮擦模式
        """
        tool = self._tools.get('eraser')
        
        if tool is not None and isinstance(tool, EraserTool):
            if size is not None:
                tool.set_size(size)
            if mode is not None:
                tool.set_mode(mode)
            logger.debug(f"配置橡皮擦工具: size={size}, mode={mode}")
    
    # ==================== 属性访问 ====================
    
    @property
    def view(self):
        """获取视图"""
        return self._view
    
    @property
    def tools(self) -> Dict[str, BaseTool]:
        """获取所有工具"""
        return self._tools.copy()
