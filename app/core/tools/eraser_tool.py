from __future__ import annotations

from typing import Optional, List, Callable, Set
from PySide6.QtCore import QPointF, QTimer, Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QMouseEvent, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPathItem, QGraphicsItem, QGraphicsEllipseItem

from app.core.tools.base_tool import BaseTool


class EraserTool(BaseTool):
    """专业橡皮擦工具 - 支持两种擦除模式"""
    
    # 擦除模式枚举
    class EraserMode:
        PATH_ERASER = "path_eraser"    # 普通橡皮擦：路径减法擦除
        OBJECT_ERASER = "object_eraser"  # 对象橡皮擦：直接删除对象
    
    def __init__(self, mode: str = EraserMode.PATH_ERASER) -> None:
        super().__init__()
        self._mode = mode
        self._active = False
        self._current_path: Optional[QPainterPath] = None
        self._eraser_preview: Optional[QGraphicsEllipseItem] = None
        self._points: List[QPointF] = []
        self._on_committed: Optional[Callable[[List[QGraphicsItem]], None]] = None
        
        # 橡皮擦属性
        self._size = 20.0  # 橡皮擦大小
        self._color = QColor("#FF0000")  # 预览颜色（红色）
        self._opacity = 0.3  # 预览透明度
        
        # 路径平滑参数
        self._smoothing = True
        self._min_distance = 3.0  # 最小点间距
        
        # 定时器用于路径优化
        self._optimize_timer = QTimer()
        self._optimize_timer.setSingleShot(True)
        self._optimize_timer.timeout.connect(self._optimize_erasing)
        
        # 存储被擦除的对象
        self._erased_items: Set[QGraphicsItem] = set()
        
    def set_mode(self, mode: str) -> None:
        """设置擦除模式"""
        self._mode = mode
        self._update_eraser_properties()
    
    def set_size(self, size: float) -> None:
        """设置橡皮擦大小"""
        self._size = max(1.0, min(100.0, size))
        if self._eraser_preview:
            self._update_preview_size()
    
    def get_size(self) -> float:
        """获取橡皮擦大小"""
        return self._size
    
    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """开始擦除"""
        if event.button() == event.button().LeftButton:
            self._active = True
            self._points = [scene_pos]
            self._erased_items.clear()
            
            if self._mode == self.EraserMode.PATH_ERASER:
                # 普通橡皮擦：创建擦除路径
                self._current_path = QPainterPath()
                self._current_path.moveTo(scene_pos)
                self._start_path_erasing(scene, scene_pos)
            else:
                # 对象橡皮擦：直接删除对象
                self._start_object_erasing(scene, scene_pos)
    
    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """继续擦除"""
        if not self._active:
            return
        
        # 检查最小距离，避免过于密集的点
        if self._points and self._distance_to_last_point(scene_pos) < self._min_distance:
            return
        
        self._points.append(scene_pos)
        
        if self._mode == self.EraserMode.PATH_ERASER:
            # 普通橡皮擦：更新擦除路径
            if self._current_path:
                self._current_path.lineTo(scene_pos)
                self._continue_path_erasing(scene, scene_pos)
        else:
            # 对象橡皮擦：继续删除对象
            self._continue_object_erasing(scene, scene_pos)
    
    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """结束擦除"""
        if self._active:
            if self._mode == self.EraserMode.PATH_ERASER:
                # 普通橡皮擦：最终优化
                if self._smoothing and len(self._points) >= 3:
                    self._optimize_timer.start(50)  # 50ms后优化路径
                else:
                    self._finalize_erasing()
            else:
                # 对象橡皮擦：直接完成
                self._finalize_erasing()
    
    def cancel(self, scene: QGraphicsScene) -> None:
        """取消擦除"""
        self._cleanup_preview(scene)
        self._reset_state()
    
    def is_active(self) -> bool:
        return self._active
    
    def _start_path_erasing(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        """开始路径擦除"""
        # 创建橡皮擦预览
        self._create_eraser_preview(scene, scene_pos)
        
        # 查找并处理被擦除的对象
        self._process_erased_items(scene, scene_pos)
    
    def _continue_path_erasing(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        """继续路径擦除"""
        # 更新橡皮擦预览位置
        if self._eraser_preview:
            self._eraser_preview.setPos(scene_pos.x() - self._size/2, scene_pos.y() - self._size/2)
        
        # 处理新擦除的对象
        self._process_erased_items(scene, scene_pos)
    
    def _start_object_erasing(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        """开始对象擦除"""
        # 创建橡皮擦预览
        self._create_eraser_preview(scene, scene_pos)
        
        # 查找并删除对象
        self._delete_objects_at_position(scene, scene_pos)
    
    def _continue_object_erasing(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        """继续对象擦除"""
        # 更新橡皮擦预览位置
        if self._eraser_preview:
            self._eraser_preview.setPos(scene_pos.x() - self._size/2, scene_pos.y() - self._size/2)
        
        # 继续删除对象
        self._delete_objects_at_position(scene, scene_pos)
    
    def _create_eraser_preview(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        """创建橡皮擦预览"""
        if self._eraser_preview:
            scene.removeItem(self._eraser_preview)
        
        self._eraser_preview = QGraphicsEllipseItem(0, 0, self._size, self._size)
        self._eraser_preview.setPos(scene_pos.x() - self._size/2, scene_pos.y() - self._size/2)
        self._eraser_preview.setPen(QPen(self._color, 2))
        self._eraser_preview.setBrush(QBrush(self._color, Qt.BrushStyle.NoBrush))
        self._eraser_preview.setOpacity(self._opacity)
        self._eraser_preview.setZValue(1000)  # 确保在最上层
        scene.addItem(self._eraser_preview)
    
    def _update_preview_size(self) -> None:
        """更新预览大小"""
        if self._eraser_preview:
            self._eraser_preview.setRect(0, 0, self._size, self._size)
            pos = self._eraser_preview.pos()
            self._eraser_preview.setPos(pos.x() + (self._eraser_preview.rect().width() - self._size)/2,
                                      pos.y() + (self._eraser_preview.rect().height() - self._size)/2)
    
    def _process_erased_items(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        """处理被擦除的对象（路径减法）"""
        eraser_rect = QRectF(scene_pos.x() - self._size/2, scene_pos.y() - self._size/2, 
                           self._size, self._size)
        
        # 查找与橡皮擦相交的对象
        items = scene.items(eraser_rect)
        for item in items:
            if item == self._eraser_preview or item in self._erased_items:
                continue
            
            # 检查对象类型并应用擦除
            if self._can_erase_item(item):
                # 避免重复处理同一个对象
                if item not in self._erased_items:
                    self._apply_path_erasing_to_item(item, scene_pos)
                    self._erased_items.add(item)
    
    def _delete_objects_at_position(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        """删除指定位置的对象"""
        eraser_rect = QRectF(scene_pos.x() - self._size/2, scene_pos.y() - self._size/2, 
                           self._size, self._size)
        
        # 查找与橡皮擦相交的对象
        items = scene.items(eraser_rect)
        for item in items:
            if item == self._eraser_preview or item in self._erased_items:
                continue
            
            # 检查对象类型并删除
            if self._can_erase_item(item):
                self._erased_items.add(item)
    
    def _can_erase_item(self, item: QGraphicsItem) -> bool:
        """检查对象是否可以被擦除"""
        # 排除橡皮擦预览和其他工具对象
        if item == self._eraser_preview:
            return False
        
        # 只擦除图形对象，不擦除UI元素
        from app.core.shapes.circle_item import CircleItem
        from app.core.shapes.point_item import PointItem
        from app.core.shapes.line_item import LineItem
        from app.core.shapes.rect_item import RectItem
        from app.core.shapes.polygon_item import PolygonItem
        from app.core.shapes.brush_path_item import BrushPathItem
        
        return isinstance(item, (CircleItem, PointItem, LineItem, RectItem, 
                               PolygonItem, BrushPathItem, QGraphicsEllipseItem, 
                               QGraphicsPathItem))
    
    def _apply_path_erasing_to_item(self, item: QGraphicsItem, scene_pos: QPointF) -> None:
        """对对象应用路径擦除"""
        # 这里实现路径减法逻辑
        # 对于不同类型的对象，需要不同的处理方式
        
        if isinstance(item, QGraphicsPathItem):
            # 对路径对象进行减法操作
            self._subtract_path_from_item(item, scene_pos)
        elif hasattr(item, 'setOpacity'):
            # 对于其他对象，降低透明度模拟擦除效果
            current_opacity = item.opacity()
            new_opacity = max(0.0, current_opacity - 0.2)
            item.setOpacity(new_opacity)
            
            # 如果透明度太低，标记为已擦除
            if new_opacity < 0.1:
                self._erased_items.add(item)
    
    def _subtract_path_from_item(self, item: QGraphicsPathItem, scene_pos: QPointF) -> None:
        """从路径对象中减去橡皮擦路径"""
        # 创建橡皮擦圆形路径
        eraser_path = QPainterPath()
        eraser_path.addEllipse(scene_pos.x() - self._size/2, scene_pos.y() - self._size/2, 
                             self._size, self._size)
        
        # 获取原路径
        original_path = item.path()
        
        # 检查路径是否为空或无效
        if original_path.isEmpty():
            return
        
        # 执行路径减法
        try:
            subtracted_path = original_path.subtracted(eraser_path)
            
            # 检查减法结果是否有效
            if not subtracted_path.isEmpty():
                # 临时禁用更新以避免闪烁
                item.setUpdatesEnabled(False)
                item.setPath(subtracted_path)
                item.setUpdatesEnabled(True)
            else:
                # 如果路径被完全擦除，降低透明度而不是删除
                current_opacity = item.opacity()
                new_opacity = max(0.0, current_opacity - 0.1)
                item.setOpacity(new_opacity)
                
        except Exception:
            # 如果路径减法失败，降低透明度
            current_opacity = item.opacity()
            new_opacity = max(0.0, current_opacity - 0.1)
            item.setOpacity(new_opacity)
    
    def _optimize_erasing(self) -> None:
        """优化擦除路径"""
        if len(self._points) > 10:  # 只对复杂路径优化
            # 简单的道格拉斯-普克算法简化
            simplified_points = self._douglas_peucker(self._points, 2.0)
            if len(simplified_points) < len(self._points):
                self._points = simplified_points
        
        self._finalize_erasing()
    
    def _finalize_erasing(self) -> None:
        """完成擦除"""
        if self._on_committed and self._erased_items:
            # 发出擦除完成信号
            self._on_committed(list(self._erased_items))
        
        self._reset_state()
    
    def _cleanup_preview(self, scene: QGraphicsScene) -> None:
        """清理预览对象"""
        if self._eraser_preview and self._eraser_preview.scene():
            scene.removeItem(self._eraser_preview)
        self._eraser_preview = None
    
    def _reset_state(self) -> None:
        """重置工具状态"""
        self._active = False
        self._current_path = None
        self._points = []
        self._erased_items.clear()
        self._optimize_timer.stop()
    
    def _distance_to_last_point(self, point: QPointF) -> float:
        """计算到最后一个点的距离"""
        if not self._points:
            return float('inf')
        last_point = self._points[-1]
        return ((point.x() - last_point.x()) ** 2 + (point.y() - last_point.y()) ** 2) ** 0.5
    
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
    
    def _update_eraser_properties(self) -> None:
        """根据模式更新橡皮擦属性"""
        if self._mode == self.EraserMode.PATH_ERASER:
            self._color = QColor("#FF0000")  # 红色预览
            self._opacity = 0.3
        else:
            self._color = QColor("#FF6600")  # 橙色预览
            self._opacity = 0.4
    
    def on_committed(self, cb: Callable[[List[QGraphicsItem]], None]) -> None:
        """设置擦除完成回调"""
        self._on_committed = cb
