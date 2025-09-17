from __future__ import annotations

from typing import Optional, List, Callable
from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QMouseEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPathItem
from app.core.shapes.brush_path_item import BrushPathItem

from app.core.tools.base_tool import BaseTool


class BrushTool(BaseTool):
    """画笔工具基类 - 支持多种画笔效果"""
    
    # 画笔类型枚举
    class BrushType:
        PEN = "pen"           # 普通画笔
        MARKER = "marker"     # 马克笔
        CALLIGRAPHY = "calligraphy"  # 书法笔
        SPRAY = "spray"       # 喷枪
        ERASER = "eraser"     # 橡皮擦
    
    def __init__(self, brush_type: str = BrushType.PEN) -> None:
        super().__init__()
        self._brush_type = brush_type
        self._active = False
        self._current_path: Optional[QPainterPath] = None
        self._current_item: Optional[BrushPathItem] = None
        self._points: List[QPointF] = []
        self._on_committed: Optional[Callable[[BrushPathItem], None]] = None
        
        # 画笔属性
        self._pen = QPen(QColor("#000000"), 3.0)
        self._brush = QBrush(QColor("#000000"))
        self._opacity = 1.0
        self._smoothing = True
        self._pressure_sensitive = False
        
        # 路径平滑参数
        self._smoothing_factor = 0.5
        self._min_distance = 2.0  # 最小点间距
        
        # 定时器用于路径优化
        self._optimize_timer = QTimer()
        self._optimize_timer.setSingleShot(True)
        self._optimize_timer.timeout.connect(self._optimize_path)
        
    def set_brush_type(self, brush_type: str) -> None:
        """设置画笔类型"""
        self._brush_type = brush_type
        self._update_brush_properties()
    
    def set_pen(self, pen: QPen) -> None:
        """设置画笔笔触"""
        self._pen = pen
    
    def set_brush(self, brush: QBrush) -> None:
        """设置画笔填充"""
        self._brush = brush
    
    def set_opacity(self, opacity: float) -> None:
        """设置透明度 (0.0-1.0)"""
        self._opacity = max(0.0, min(1.0, opacity))
    
    def set_smoothing(self, enabled: bool) -> None:
        """启用/禁用路径平滑"""
        self._smoothing = enabled
    
    def set_pressure_sensitive(self, enabled: bool) -> None:
        """启用/禁用压感"""
        self._pressure_sensitive = enabled
    
    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """开始绘制路径"""
        if event.button() == event.button().LeftButton:
            self._active = True
            self._current_path = QPainterPath()
            self._current_path.moveTo(scene_pos)
            self._points = [scene_pos]
            
            # 创建路径图元
            self._current_item = BrushPathItem(self._current_path)
            self._current_item.set_brush_type(self._brush_type)
            self._apply_brush_style()
            scene.addItem(self._current_item)
    
    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """继续绘制路径"""
        if self._active and self._current_path and self._current_item:
            # 检查最小距离，避免过于密集的点
            if self._points and self._distance_to_last_point(scene_pos) < self._min_distance:
                return
            
            self._points.append(scene_pos)
            
            if self._smoothing and len(self._points) >= 3:
                # 使用平滑算法
                smoothed_path = self._create_smooth_path()
                self._current_item.setPath(smoothed_path)
            else:
                # 直接连线
                self._current_path.lineTo(scene_pos)
                self._current_item.setPath(self._current_path)
    
    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """结束绘制路径"""
        if self._active and self._current_item:
            # 最终路径优化
            if self._smoothing and len(self._points) >= 3:
                self._optimize_timer.start(50)  # 50ms后优化路径
            else:
                self._finalize_path()
    
    def cancel(self, scene: QGraphicsScene) -> None:
        """取消当前绘制"""
        if self._current_item and self._current_item.scene():
            scene.removeItem(self._current_item)
        self._reset_state()
    
    def is_active(self) -> bool:
        return self._active
    
    def _update_brush_properties(self) -> None:
        """根据画笔类型更新属性"""
        if self._brush_type == self.BrushType.PEN:
            self._pen.setWidthF(3.0)
            self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        elif self._brush_type == self.BrushType.MARKER:
            self._pen.setWidthF(8.0)
            self._pen.setCapStyle(Qt.PenCapStyle.SquareCap)
            self._pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        elif self._brush_type == self.BrushType.CALLIGRAPHY:
            self._pen.setWidthF(5.0)
            self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        elif self._brush_type == self.BrushType.SPRAY:
            self._pen.setWidthF(12.0)
            self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        elif self._brush_type == self.BrushType.ERASER:
            self._pen.setColor(QColor("#FFFFFF"))
            self._pen.setWidthF(10.0)
            self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    
    def _apply_brush_style(self) -> None:
        """应用画笔样式到当前图元"""
        if self._current_item:
            pen = QPen(self._pen)
            pen.setColor(pen.color())
            pen.setWidthF(pen.widthF())
            self._current_item.setPen(pen)
            # 画笔路径应该只显示描边，不显示填充
            self._current_item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self._current_item.setOpacity(self._opacity)
    
    def _distance_to_last_point(self, point: QPointF) -> float:
        """计算到最后一个点的距离"""
        if not self._points:
            return float('inf')
        last_point = self._points[-1]
        return ((point.x() - last_point.x()) ** 2 + (point.y() - last_point.y()) ** 2) ** 0.5
    
    def _create_smooth_path(self) -> QPainterPath:
        """创建平滑路径"""
        if len(self._points) < 3:
            return self._current_path
        
        smooth_path = QPainterPath()
        smooth_path.moveTo(self._points[0])
        
        # 使用二次贝塞尔曲线平滑
        for i in range(1, len(self._points) - 1):
            current = self._points[i]
            next_point = self._points[i + 1]
            
            # 控制点
            control_x = (current.x() + next_point.x()) / 2
            control_y = (current.y() + next_point.y()) / 2
            
            smooth_path.quadTo(current, QPointF(control_x, control_y))
        
        # 最后一点
        if len(self._points) > 1:
            smooth_path.lineTo(self._points[-1])
        
        return smooth_path
    
    def _optimize_path(self) -> None:
        """优化路径（减少点数）"""
        if len(self._points) > 10:  # 只对复杂路径优化
            # 简单的道格拉斯-普克算法简化
            simplified_points = self._douglas_peucker(self._points, 1.0)
            if len(simplified_points) < len(self._points):
                self._points = simplified_points
                self._current_path = self._create_smooth_path()
                if self._current_item:
                    self._current_item.setPath(self._current_path)
        
        self._finalize_path()
    
    def _douglas_peucker(self, points: List[QPointF], tolerance: float) -> List[QPointF]:
        """道格拉斯-普克算法简化路径"""
        if len(points) <= 2:
            return points
        
        # 找到距离起点和终点连线最远的点
        max_distance = 0
        max_index = 0
        start = points[0]
        end = points[-1]
        
        for i in range(1, len(points) - 1):
            distance = self._point_to_line_distance(points[i], start, end)
            if distance > max_distance:
                max_distance = distance
                max_index = i
        
        # 如果最大距离大于容差，递归处理
        if max_distance > tolerance:
            left_points = self._douglas_peucker(points[:max_index + 1], tolerance)
            right_points = self._douglas_peucker(points[max_index:], tolerance)
            return left_points[:-1] + right_points
        else:
            return [start, end]
    
    def _point_to_line_distance(self, point: QPointF, line_start: QPointF, line_end: QPointF) -> float:
        """计算点到直线的距离"""
        A = line_end.y() - line_start.y()
        B = line_start.x() - line_end.x()
        C = line_end.x() * line_start.y() - line_start.x() * line_end.y()
        
        return abs(A * point.x() + B * point.y() + C) / (A * A + B * B) ** 0.5
    
    def _finalize_path(self) -> None:
        """完成路径绘制"""
        if self._current_item and self._on_committed:
            self._on_committed(self._current_item)
            self._reset_state()
    
    def on_committed(self, cb: Callable[[BrushPathItem], None]) -> None:
        """设置提交回调"""
        self._on_committed = cb
    
    def _reset_state(self) -> None:
        """重置工具状态"""
        self._active = False
        self._current_path = None
        self._current_item = None
        self._points = []
        self._optimize_timer.stop()
