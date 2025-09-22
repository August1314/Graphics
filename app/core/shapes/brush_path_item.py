from __future__ import annotations

from typing import List
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath
from PySide6.QtWidgets import QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget

from app.core.shapes.base_item import BaseShapeItem


class BrushPathItem(QGraphicsPathItem):
    """画笔路径图元 - 支持路径编辑和样式修改"""
    
    def __init__(self, path: QPainterPath = None, parent=None) -> None:
        super().__init__(path or QPainterPath(), parent)
        self.setFlags(
            self.GraphicsItemFlag.ItemIsMovable | 
            self.GraphicsItemFlag.ItemIsSelectable |
            self.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        
        # 默认样式 - 画笔路径只显示描边，不显示填充
        self.setPen(QPen(QColor("#000000"), 3.0))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setOpacity(1.0)
        
        # 路径数据
        self._original_path = QPainterPath(path) if path else QPainterPath()
        self._brush_type = "pen"
        self._smoothing_enabled = True
        
        # 编辑状态
        self._editing = False
        
        # 性能优化：启用渲染缓存
        self.setCacheMode(self.CacheMode.ItemCoordinateCache)
        self._cached_mode = self.cacheMode()
        self._control_points: List[QPointF] = []
        self._selected_control_point = -1
    
    def setPen(self, pen: QPen) -> None:
        """重写 setPen 方法以便调试宽度变化"""
        import traceback
        super().setPen(pen)
        print(f"DEBUG: setPen 被调用，新宽度: {pen.widthF()}")
        print(f"DEBUG: setPen 调用栈:")
        for line in traceback.format_stack()[-3:-1]:
            print(f"  {line.strip()}")
        
    def brush_type(self) -> str:
        """获取画笔类型"""
        return self._brush_type
    
    def set_brush_type(self, brush_type: str) -> None:
        """设置画笔类型"""
        self._brush_type = brush_type
        # 如果是从加载来的对象，不要调用 _update_brush_style
        if hasattr(self, '_loaded_from_dict') and self._loaded_from_dict:
            print(f"DEBUG: set_brush_type 跳过 _update_brush_style，因为是从加载来的对象")
            return
        print(f"DEBUG: set_brush_type 调用 _update_brush_style，_loaded_from_dict: {getattr(self, '_loaded_from_dict', False)}")
        self._update_brush_style()
    
    def smoothing_enabled(self) -> bool:
        """是否启用平滑"""
        return self._smoothing_enabled
    
    def set_smoothing_enabled(self, enabled: bool) -> None:
        """设置平滑"""
        self._smoothing_enabled = enabled
    
    def path_points(self) -> List[QPointF]:
        """获取路径关键点"""
        points = []
        path = self.path()
        
        # 提取路径中的关键点
        for i in range(path.elementCount()):
            element = path.elementAt(i)
            if element.type == QPainterPath.ElementType.MoveToElement:
                points.append(QPointF(element.x, element.y))
            elif element.type == QPainterPath.ElementType.LineToElement:
                points.append(QPointF(element.x, element.y))
            elif element.type == QPainterPath.ElementType.CurveToElement:
                # 对于曲线，添加控制点
                points.append(QPointF(element.x, element.y))
        
        return points
    
    def set_path_points(self, points: List[QPointF]) -> None:
        """设置路径关键点"""
        if not points:
            return
        # 路径与包围盒将改变
        self.prepareGeometryChange()
        new_path = QPainterPath()
        new_path.moveTo(points[0])
        
        if self._smoothing_enabled and len(points) >= 3:
            # 使用平滑算法重建路径
            for i in range(1, len(points) - 1):
                current = points[i]
                next_point = points[i + 1]
                control_x = (current.x() + next_point.x()) / 2
                control_y = (current.y() + next_point.y()) / 2
                new_path.quadTo(current, QPointF(control_x, control_y))
            
            if len(points) > 1:
                new_path.lineTo(points[-1])
        else:
            # 直接连线
            for point in points[1:]:
                new_path.lineTo(point)
        
        self.setPath(new_path)
        self._original_path = QPainterPath(new_path)
    
    def simplify_path(self, tolerance: float = 1.0) -> None:
        """简化路径（减少点数）"""
        points = self.path_points()
        if len(points) <= 2:
            return
        
        simplified = self._douglas_peucker(points, tolerance)
        if len(simplified) < len(points):
            self.set_path_points(simplified)
    
    def smooth_path(self) -> None:
        """平滑路径"""
        points = self.path_points()
        if len(points) < 3:
            return
        
        # 使用移动平均平滑
        smoothed = []
        window_size = 3
        
        for i in range(len(points)):
            start = max(0, i - window_size // 2)
            end = min(len(points), i + window_size // 2 + 1)
            
            avg_x = sum(p.x() for p in points[start:end]) / (end - start)
            avg_y = sum(p.y() for p in points[start:end]) / (end - start)
            smoothed.append(QPointF(avg_x, avg_y))
        
        self.set_path_points(smoothed)
    
    def start_editing(self) -> None:
        """开始编辑模式"""
        self.prepareGeometryChange()
        self._editing = True
        self._control_points = self.path_points()
        # 编辑过程中禁用坐标缓存，避免缓存残留导致虚线框不消失
        self._cached_mode = self.cacheMode()
        self.setCacheMode(self.CacheMode.NoCache)
        self.update()
    
    def stop_editing(self) -> None:
        """结束编辑模式"""
        self.prepareGeometryChange()
        self._editing = False
        self._control_points = []
        self._selected_control_point = -1
        # 恢复缓存
        try:
            self.setCacheMode(self._cached_mode)
        except Exception:
            self.setCacheMode(self.CacheMode.ItemCoordinateCache)
        self.update()
    
    def is_editing(self) -> bool:
        """是否在编辑模式"""
        return self._editing
    
    def boundingRect(self) -> QRectF:
        """重写边界矩形，为控制点留出空间"""
        rect = super().boundingRect()
        if self._editing:
            # 为控制点留出额外空间
            margin = 10.0
            rect.adjust(-margin, -margin, margin, margin)
        return rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None) -> None:
        # 保存当前 pen
        original_pen = self.pen()
        
        if self.isSelected():
            print(f"DEBUG: paint 方法中对象被选中，当前宽度: {original_pen.widthF()}")
            # 动态应用高亮效果
            highlight_pen = QPen(original_pen)
            color = highlight_pen.color().darker(125)
            highlight_pen.setColor(color)
            # 不修改宽度，只改变颜色
            # 如果需要加粗，可以在这里绘制额外边框，但不修改 original_pen
            painter.setPen(highlight_pen)
        else:
            painter.setPen(original_pen)
        
        painter.setBrush(self.brush())
        painter.drawPath(self.path())
        
        # 如果需要绘制选中边框
        if self.isSelected():
            # 绘制虚线选中框
            sel_pen = QPen(QColor("#CCCCCC"), 1, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())

        
        # 在编辑模式下绘制控制点
        if self._editing and self._control_points:
            painter.save()
            painter.setRenderHint(painter.RenderHint.Antialiasing)
            
            # 绘制控制点
            for i, point in enumerate(self._control_points):
                if i == self._selected_control_point:
                    # 选中的控制点
                    painter.setPen(QPen(QColor("#FF0000"), 2))
                    painter.setBrush(QBrush(QColor("#FF0000")))
                else:
                    # 普通控制点
                    painter.setPen(QPen(QColor("#0066CC"), 1))
                    painter.setBrush(QBrush(QColor("#FFFFFF")))
                
                painter.drawEllipse(point, 4, 4)
            
            # 绘制连接线
            if len(self._control_points) > 1:
                painter.setPen(QPen(QColor("#CCCCCC"), 1, Qt.PenStyle.DashLine))
                for i in range(len(self._control_points) - 1):
                    painter.drawLine(self._control_points[i], self._control_points[i + 1])
            
            painter.restore()
    
    def mousePressEvent(self, event) -> None:
        """处理鼠标按下事件"""
        if self._editing:
            # 检查是否点击了控制点
            click_pos = event.pos()
            for i, point in enumerate(self._control_points):
                if (click_pos - point).manhattanLength() < 10:
                    self._selected_control_point = i
                    self.update()
                    event.accept()
                    return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        """处理鼠标移动事件"""
        if self._editing and self._selected_control_point >= 0:
            # 移动选中的控制点
            new_pos = event.pos()
            self._control_points[self._selected_control_point] = new_pos
            self.set_path_points(self._control_points)
            self.update()
            event.accept()
            return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """处理鼠标释放事件"""
        if self._editing:
            self._selected_control_point = -1
            self.update()
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def _update_brush_style(self) -> None:
        """根据画笔类型更新样式"""
        pen = self.pen()
        print(f"DEBUG: _update_brush_style 被调用，当前宽度: {pen.widthF()}, 画笔类型: {self._brush_type}")
        print(f"DEBUG: _loaded_from_dict 标志: {getattr(self, '_loaded_from_dict', False)}")
        
        # 如果是从加载来的对象，不要覆盖宽度
        if hasattr(self, '_loaded_from_dict') and self._loaded_from_dict:
            print(f"DEBUG: 跳过宽度设置，因为是从加载来的对象")
            # 只设置样式，不设置宽度
            if self._brush_type == "pen":
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            elif self._brush_type == "marker":
                pen.setCapStyle(Qt.PenCapStyle.SquareCap)
                pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            elif self._brush_type == "calligraphy":
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            elif self._brush_type == "spray":
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            elif self._brush_type == "eraser":
                pen.setColor(QColor("#FFFFFF"))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            self.setPen(pen)
            return
        
        if self._brush_type == "pen":
            pen.setWidthF(8.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        elif self._brush_type == "marker":
            pen.setWidthF(8.0)
            pen.setCapStyle(Qt.PenCapStyle.SquareCap)
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        elif self._brush_type == "calligraphy":
            pen.setWidthF(8.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        elif self._brush_type == "spray":
            pen.setWidthF(8.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        elif self._brush_type == "eraser":
            pen.setColor(QColor("#FFFFFF"))
            pen.setWidthF(8.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        
        self.setPen(pen)
        # 确保画笔路径始终不显示填充
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
    
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
    
    # 实现 BaseShapeItem 接口
    def get_center(self) -> QPointF:
        """获取图元中心点"""
        rect = self.boundingRect()
        return rect.center()
    
    def set_center(self, center: QPointF) -> None:
        """设置图元中心点"""
        rect = self.boundingRect()
        current_center = rect.center()
        offset = center - current_center
        self.moveBy(offset.x(), offset.y())
    
    def get_bounds(self) -> tuple[float, float, float, float]:
        """获取边界 (x, y, width, height)"""
        rect = self.boundingRect()
        return rect.x(), rect.y(), rect.width(), rect.height()
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        points = self.path_points()
        return {
            "type": "brush_path",
            "points": [[p.x(), p.y()] for p in points],
            "brush_type": self._brush_type,
            "smoothing": self._smoothing_enabled,
            "stroke": self.pen().color().name(),
            "width": self.pen().widthF(),
            "style": int(self.pen().style().value),
            "fill": self.brush().color().name(),
            "opacity": self.opacity()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BrushPathItem':
        """从字典反序列化"""
        points_data = data.get("points", [])
        if points_data:
            points = [QPointF(p[0], p[1]) for p in points_data]
            path = QPainterPath()
            if points:
                path.moveTo(points[0])
                # 使用与正常绘制相同的平滑逻辑
                if len(points) > 1:
                    # 使用二次贝塞尔曲线平滑
                    for i in range(1, len(points) - 1):
                        current = points[i]
                        next_point = points[i + 1]
                        
                        # 控制点
                        control_x = (current.x() + next_point.x()) / 2
                        control_y = (current.y() + next_point.y()) / 2
                        
                        path.quadTo(current, QPointF(control_x, control_y))
                    
                    # 最后一点
                    path.lineTo(points[-1])
                else:
                    # 只有一个点，直接使用
                    path.lineTo(points[0])
            item = cls(path)
            
            # 立即标记这是从加载来的对象，避免构造函数或其他方法调用 _update_brush_style
            item._loaded_from_dict = True
            print(f"DEBUG: 设置 _loaded_from_dict = True")
            
            # 先设置基本属性，但不调用 _update_brush_style
            item._brush_type = data.get("brush_type", "pen")
            # 直接设置属性，避免调用 set_smoothing_enabled 可能触发的方法
            item._smoothing_enabled = data.get("smoothing", True)
            
            # 应用保存的样式信息
            pen = item.pen()
            if "width" in data:
                print(f"DEBUG: 设置宽度为 {data['width']}")
                pen.setWidthF(float(data["width"]))
                print(f"DEBUG: 设置后宽度为 {pen.widthF()}")
            
            if "stroke" in data:
                pen.setColor(QColor(data["stroke"]))
            
            # 设置笔触样式
            if item._brush_type == "pen":
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            elif item._brush_type == "marker":
                pen.setCapStyle(Qt.PenCapStyle.SquareCap)
                pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            elif item._brush_type == "calligraphy":
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            
            item.setPen(pen)
            
            if "fill" in data:
                brush = item.brush()
                brush.setColor(QColor(data["fill"]))
                item.setBrush(brush)
            
            if "opacity" in data:
                item.setOpacity(float(data["opacity"]))
            
            return item
        return cls()
