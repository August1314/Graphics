from __future__ import annotations

from typing import Optional, List, Callable
import math
import random
from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QMouseEvent, QPainter, QImage, QPixmap
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
        self._pen = QPen(QColor("#000000"), 8.0)
        self._brush = QBrush(QColor("#000000"))
        self._opacity = 1.0
        self._smoothing = True
        self._pressure_sensitive = False
        
        # 路径平滑参数
        self._smoothing_factor = 0.5
        self._min_distance = 2.0  # 最小点间距
        # 喷枪离屏绘制（贴图）
        self._spray_pix: Optional[QImage] = None
        self._spray_origin: Optional[QPointF] = None
        self._spray_last_pos: Optional[QPointF] = None
        
        # 定时器用于路径优化
        self._optimize_timer = QTimer()
        self._optimize_timer.setSingleShot(True)
        self._optimize_timer.timeout.connect(self._optimize_path)
        # 初始化一次笔参数，确保默认宽度生效
        self._update_brush_properties()
        
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
            # 确保当前类型对应的笔参数在创建路径前生效
            self._update_brush_properties()
            self._current_path = QPainterPath()
            self._current_path.moveTo(scene_pos)
            self._points = [scene_pos]
            
            # 创建路径或喷枪图元
            self._current_item = BrushPathItem(self._current_path)
            self._current_item.set_brush_type(self._brush_type)
            self._apply_brush_style()
            scene.addItem(self._current_item)
            # 绘制期间关闭缓存，避免缓存不刷新导致“松开才出现”
            try:
                from PySide6.QtWidgets import QGraphicsItem
                self._current_item.setCacheMode(QGraphicsItem.CacheMode.NoCache)
            except Exception:
                pass
            # 初始化喷枪离屏图
            if self._brush_type == self.BrushType.SPRAY:
                self._spray_origin = QPointF(scene_pos)
                self._spray_pix = QImage(512, 512, QImage.Format.Format_ARGB32_Premultiplied)
                self._spray_pix.fill(0x00000000)
                self._spray_last_pos = QPointF(scene_pos)
    
    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """继续绘制路径"""
        if self._active and self._current_path and self._current_item:
            # 检查最小距离，避免过于密集的点
            if self._points and self._distance_to_last_point(scene_pos) < self._min_distance:
                return
            
            if self._brush_type == self.BrushType.SPRAY:
                self._spray_paint_along(scene_pos)
            else:
                self._points.append(scene_pos)
                if self._smoothing and len(self._points) >= 3:
                    smoothed_path = self._create_smooth_path()
                    try:
                        self._current_item.prepareGeometryChange()
                    except Exception:
                        pass
                    self._current_item.setPath(smoothed_path)
                else:
                    self._current_path.lineTo(scene_pos)
                    try:
                        self._current_item.prepareGeometryChange()
                    except Exception:
                        pass
                    self._current_item.setPath(self._current_path)
                # 动态风格：marker 轻微宽度抖动，calligraphy 方向相关宽度
                try:
                    pen = self._current_item.pen()
                    base_w = max(0.5, self._pen.widthF())
                    if self._brush_type == self.BrushType.MARKER:
                        jitter = 1.0 + (random.random() * 0.1 - 0.05)  # ±5%
                        pen.setWidthF(base_w * jitter)
                        self._current_item.setPen(pen)
                    elif self._brush_type == self.BrushType.CALLIGRAPHY and len(self._points) >= 2:
                        v = self._points[-1] - self._points[-2]
                        ang = math.atan2(v.y(), v.x())
                        phi = math.radians(45.0)
                        scale = 0.6 + 0.4 * abs(math.cos(ang - phi))
                        pen.setWidthF(base_w * scale)
                        self._current_item.setPen(pen)
                except Exception:
                    pass
            # 强制刷新，保证按下时可见
            # 强制刷新当前项与场景
            self._current_item.update()
            try:
                scene.invalidate(scene.sceneRect())
            except Exception:
                scene.update()
    
    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        """结束绘制路径"""
        if self._active and self._current_item:
            if self._brush_type == self.BrushType.SPRAY:
                # 将离屏图贴到路径（以填充方式表现）
                self._commit_spray_texture()
                self._finalize_path()
            else:
                if self._smoothing and len(self._points) >= 3:
                    self._optimize_timer.start(50)
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
            self._pen.setWidthF(8.0)
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
            self._pen.setWidthF(8.0)
            self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        elif self._brush_type == self.BrushType.ERASER:
            self._pen.setColor(QColor("#FFFFFF"))
            self._pen.setWidthF(8.0)
            self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    
    def _apply_brush_style(self) -> None:
        """应用画笔样式到当前图元"""
        if self._current_item:
            pen = QPen(self._pen)
            try:
                # cosmetic 笔触宽度稳定，不随变换缩放造成像素抖动
                pen.setCosmetic(True)
            except Exception:
                pass
            # 针对不同画笔调整风格
            if self._brush_type == self.BrushType.MARKER:
                # 颜色保持，宽度已在 _update_brush_properties 设置
                pass
            elif self._brush_type == self.BrushType.CALLIGRAPHY:
                # 起步稍细
                pen.setWidthF(max(1.0, pen.widthF()))
            elif self._brush_type == self.BrushType.SPRAY:
                # 喷枪使用点填充：描边设为透明、填充使用半透明前景
                pen.setColor(QColor(0, 0, 0, 0))
            self._current_item.setPen(pen)
            # 画笔路径应该只显示描边，不显示填充
            if self._brush_type == self.BrushType.SPRAY:
                self._current_item.setBrush(QBrush(QColor(self._pen.color().red(), self._pen.color().green(), self._pen.color().blue(), int(255*self._opacity*0.5))))
            else:
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

    # ---- 喷枪实现 ----
    def _spray_paint_along(self, curr: QPointF) -> None:
        """在上一次位置与当前位置之间做插值喷涂，形成连续雾带。"""
        if self._spray_last_pos is None:
            self._spray_last_pos = QPointF(curr)
        last = self._spray_last_pos
        # 分段数与移动距离/半径成比例
        radius = max(1.0, self._pen.widthF() / 2.0)
        dist = math.hypot(curr.x() - last.x(), curr.y() - last.y())
        # 限制最大步数，避免极快移动导致过多循环
        steps = max(1, min(64, int(dist / max(1.0, radius * 0.5))))
        for i in range(1, steps + 1):
            t = i / steps
            x = last.x() + (curr.x() - last.x()) * t
            y = last.y() + (curr.y() - last.y()) * t
            self._spray_paint(QPointF(x, y))
        self._spray_last_pos = QPointF(curr)

    def _spray_paint(self, pos: QPointF) -> None:
        if self._spray_pix is None or self._spray_origin is None or self._current_item is None:
            return
        try:
            radius = max(1.0, self._pen.widthF() / 2.0)
            # 在离屏图上绘制随机点
            p = QPainter(self._spray_pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            base = self._pen.color()
            # 样本数与半径线性相关
            # 限制样本数，避免卡顿
            samples = min(300, int(60 + radius * 8))
            for _ in range(samples):
                ang = random.random() * 2.0 * 3.1415926
                # 采用 sqrt 分布，让中心更浓
                r = radius * (random.random() ** 0.5)
                dx, dy = math.cos(ang) * r, math.sin(ang) * r
                a = max(40, min(220, int(220 * (1.0 - r / radius))))
                color = QColor(base.red(), base.green(), base.blue(), a)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(color))
                cx = int(pos.x()-self._spray_origin.x()+dx+256)
                cy = int(pos.y()-self._spray_origin.y()+dy+256)
                p.drawEllipse(cx-1, cy-1, 2, 2)
            p.end()
            # 将离屏结果贴为纹理，直接给出紧致矩形（以喷点邻域为界，避免扫描整图）
            from PySide6.QtCore import QRectF, QRect
            rect_full = QRectF(self._spray_origin.x()-256, self._spray_origin.y()-256, 512, 512)
            # 计算当前步的局部包围（以 radius 为边界）
            local = QRectF(pos.x()-radius, pos.y()-radius, radius*2, radius*2)
            # 将局部映射到贴图坐标
            src = QRect(int(local.x()-rect_full.x()), int(local.y()-rect_full.y()), int(local.width()), int(local.height()))
            tight = QRectF(local)
            # 直接使用 fast 接口更新（避免 O(w*h) 扫描）
            if hasattr(self._current_item, 'set_spray_texture_fast'):
                self._current_item.set_spray_texture_fast(self._spray_pix, rect_full, tight, src)
            else:
                self._current_item.set_spray_texture(self._spray_pix, rect_full)
            self._current_item.update()
        except Exception:
            pass

    def _commit_spray_texture(self) -> None:
        # 已在 _spray_paint 中把贴图设为 Brush，无需更多处理
        return
    
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
