from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPoint, QPointF, Qt, QRectF, Signal, QMimeData
from PySide6.QtGui import QImage, QPainter, QCursor
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu

from app.core.tools.base_tool import BaseTool
from app.core.tools.circle_tool import CircleTool
from app.core.tools.point_tool import PointTool
from app.core.tools.line_tool import LineTool
from app.core.tools.rect_tool import RectTool
from app.core.tools.polygon_tool import PolygonTool
from app.core.tools.brush_tool import BrushTool
from app.core.tools.eraser_tool import EraserTool
from app.ui.icon_provider import IconProvider


class CanvasView(QGraphicsView):
    selectionGeometryChanged = Signal()
    shapeCommitted = Signal(object)
    moveCommitted = Signal(object, object, object)
    deleteRequested = Signal(object)
    copyCompleted = Signal(bool)
    pasteCompleted = Signal(bool)
    def __init__(self, scene: QGraphicsScene, parent=None) -> None:
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._panning = False
        self._pan_start: Optional[QPoint] = None
        self._space_held: bool = False
        self._tool: BaseTool | None = None
        self._circle_tool = CircleTool()
        self._point_tool = PointTool()
        self._line_tool = LineTool()
        self._rect_tool = RectTool()
        self._polygon_tool = PolygonTool()
        self._brush_tool = BrushTool()
        self._eraser_tool = EraserTool()
        # 光标图标提供器
        self._cursor_icons = IconProvider("light")
        # 提交后自动选中新建的图元
        self._circle_tool.on_committed(self._auto_select_item)
        self._point_tool.on_committed(self._auto_select_item)
        self._line_tool.on_committed(self._auto_select_item)
        self._rect_tool.on_committed(self._auto_select_item)
        self._polygon_tool.on_committed(self._auto_select_item)
        self._brush_tool.on_committed(self._auto_select_item)
        self._eraser_tool.on_committed(self._on_eraser_completed)
        self._dragged_item = None
        self._drag_start_pos: QPointF | None = None
        # 记录一次拖动开始时所有选中项的初始位置，以支持多选移动撤销
        self._drag_start_positions: dict | None = None
        self._pending_paste_payload: dict | None = None
        self._last_context_item = None
        # 橡皮框选择状态标记，供主窗抑制属性面板在框选时的回写
        self._rubber_selecting: bool = False
        # 当前绘制样式
        from PySide6.QtGui import QColor, QPen
        self._current_pen_color = QColor("#0066cc")
        self._current_pen_width = 2.0
        self._current_pen_style = Qt.PenStyle.SolidLine
        self._current_pen_obj = QPen(self._current_pen_color, float(self._current_pen_width))
        self._current_pen_obj.setStyle(self._current_pen_style)

    def wheelEvent(self, event):  # type: ignore[override]
        delta = event.angleDelta().y()
        factor = 1.0015 ** delta
        self.scale(factor, factor)

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and self._space_held):
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        # 若处于“等待点击粘贴”模式，则在点击位置粘贴
        if event.button() == Qt.LeftButton and self._pending_paste_payload is not None:
            scene_pos = self.mapToScene(event.pos())
            self._create_item_from_payload(self._pending_paste_payload, scene_pos)
            self._pending_paste_payload = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        # 仅在左键点击且有绘制工具时，启动绘制
        if event.button() == Qt.LeftButton and self._tool is not None:
            top_item = self.itemAt(event.pos())
            # 多边形：激活期间允许在图元上继续点选；其他工具仍要求空白区域
            allow_press = (
                (self._tool is self._polygon_tool and getattr(self._tool, "is_active", lambda: False)())
                or top_item is None
            )
            if allow_press:
                # 开始绘制会话时，禁用橡皮框拖拽以避免抢占事件
                self.setDragMode(QGraphicsView.NoDrag)
                scene_pos = self.mapToScene(event.pos())
                # 若为画笔工具，按当前样式注入
                try:
                    from PySide6.QtGui import QPen
                    if self._tool is self._brush_tool:
                        self._refresh_current_pen_obj()
                        self._brush_tool.set_pen(self._current_pen_obj)
                except Exception:
                    pass
                self._tool.on_press(self.scene(), scene_pos, event)
                # 若工具有草稿图元，为其设置当前笔触
                try:
                    draft = getattr(self._tool, "_draft", None)
                    if draft is not None and hasattr(draft, "pen") and hasattr(draft, "setPen"):
                        p = draft.pen(); p.setColor(self._current_pen_color); p.setWidthF(float(self._current_pen_width)); p.setStyle(self._current_pen_style); draft.setPen(p)
                except Exception:
                    pass
                event.accept()
                return
        # 记录拖动起点（选择模式下拖动选中图元）或进入框选
        if event.button() == Qt.LeftButton and self._tool is None:
            top_item = self.itemAt(event.pos())
            if top_item is not None and top_item.isSelected():
                self._dragged_item = top_item
                self._drag_start_pos = top_item.pos()
                # 记录所有选中项的原始位置（支持成组移动）
                sel = list(self.scene().selectedItems())
                if sel:
                    self._drag_start_positions = {it: it.pos() for it in sel}
                # 为了确保拖动命中项而不是拉框，按住期间禁用 RubberBand
                self.setDragMode(QGraphicsView.NoDrag)
            else:
                # 命中空白或命中未选中项：进入橡皮框扩选
                self._rubber_selecting = True
                self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # type: ignore[override]
        if self._panning and self._pan_start is not None:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.translate(delta.x(), delta.y())
            event.accept()
            return
        # 仅当绘制会话处于激活状态时才将移动事件分发给工具
        if self._tool is not None and getattr(self._tool, "is_active", lambda: False)():
            scene_pos = self.mapToScene(event.pos())
            self._tool.on_move(self.scene(), scene_pos, event)
            event.accept()
            return
        super().mouseMoveEvent(event)
        # 若正在进行橡皮框，持续标记，防止中途被清除
        if (event.buttons() & Qt.LeftButton) and self.dragMode() == QGraphicsView.RubberBandDrag:
            self._rubber_selecting = True
        # 仅在“正在拖动选中图元”时才通知几何变化，避免矩形/圆在框选时被联动修改
        if (event.buttons() & Qt.LeftButton) and (self._dragged_item is not None):
            self.selectionGeometryChanged.emit()

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        if self._panning and (event.button() == Qt.MiddleButton or event.button() == Qt.LeftButton):
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        # 仅当绘制会话处于激活状态时才结束绘制
        if self._tool is not None and getattr(self._tool, "is_active", lambda: False)():
            scene_pos = self.mapToScene(event.pos())
            self._tool.on_release(self.scene(), scene_pos, event)
            # 结束绘制会话后，恢复橡皮框拖拽
            self.setDragMode(QGraphicsView.RubberBandDrag)
            event.accept()
            return
        # 提交拖动命令
        if event.button() == Qt.LeftButton and self._dragged_item is not None:
            new_pos = self._dragged_item.pos()
            # 若记录了多选的起始位置，则为每个发生变化的项发送一次移动提交
            if isinstance(self._drag_start_positions, dict) and self._drag_start_positions:
                # 将一次多选移动合并为一个撤销宏，确保一次撤销全部回位
                any_moved = False
                us = None
                try:
                    mw = self.window()
                    if hasattr(mw, 'undo_stack'):
                        us = mw.undo_stack  # type: ignore[attr-defined]
                        us.beginMacro("移动")
                except Exception:
                    us = None
                for it, oldp in list(self._drag_start_positions.items()):
                    try:
                        newp = it.pos()
                    except Exception:
                        continue
                    if newp != oldp:
                        any_moved = True
                        self.moveCommitted.emit(it, oldp, newp)
                try:
                    if us is not None:
                        us.endMacro()
                except Exception:
                    pass
            else:
                if self._drag_start_pos is not None and (new_pos != self._drag_start_pos):
                    self.moveCommitted.emit(self._dragged_item, self._drag_start_pos, new_pos)
            self._dragged_item = None
            self._drag_start_pos = None
            self._drag_start_positions = None
            # 释放后恢复拉框选择
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)
        # 框选结束
        if event.button() == Qt.LeftButton:
            self._rubber_selecting = False

    def set_tool(self, name: str) -> None:
        if name in ("circle", "ellipse"):
            self._tool = self._circle_tool
        elif name == "point":
            self._tool = self._point_tool
        elif name == "line":
            self._tool = self._line_tool
        elif name == "rect":
            self._tool = self._rect_tool
        elif name == "polygon":
            self._tool = self._polygon_tool
        elif name.startswith("brush_"):
            # 设置画笔类型
            brush_type = name.replace("brush_", "")
            self._brush_tool.set_brush_type(brush_type)
            try:
                self._refresh_current_pen_obj(); self._brush_tool.set_pen(self._current_pen_obj)
            except Exception:
                pass
            self._tool = self._brush_tool
            # 切换到画笔时，隐藏并清理橡皮擦预览
            try:
                self._eraser_tool.cancel(self.scene())
            except Exception:
                pass
        elif name == "eraser":
            self._tool = self._eraser_tool
        else:
            self._tool = None
        # 更新画布光标为对应工具图标
        try:
            key = name if name else "select"
            ic = self._cursor_icons.get(key, 28)
            pm = ic.pixmap(28, 28)
            self.setCursor(QCursor(pm, pm.width() // 2, pm.height() // 2))
        except Exception:
            self.setCursor(Qt.ArrowCursor)
        # 仅在“选择”工具下允许拖动；其他工具禁用图元移动，避免被视为“创建后的拖动”
        try:
            allow_move = (self._tool is None)
            for it in list(self.scene().items()):
                try:
                    it.setFlag(it.GraphicsItemFlag.ItemIsMovable, allow_move)
                except Exception:
                    continue
        except Exception:
            pass

    def _auto_select_item(self, item):
        # 清空当前选择并选中新建项
        self.scene().clearSelection()
        item.setSelected(True)
        # 刚创建完成的图元只有在“选择”模式才允许拖动
        try:
            movable = (self._tool is None)
            item.setFlag(item.GraphicsItemFlag.ItemIsMovable, movable)
        except Exception:
            pass
        self.shapeCommitted.emit(item)
    
    def _on_eraser_completed(self, payload):
        """橡皮擦完成回调：payload = {'deleted': [...], 'updates': [...]}"""
        try:
            deleted = list(payload.get('deleted', [])) if isinstance(payload, dict) else []
            updates = list(payload.get('updates', [])) if isinstance(payload, dict) else []
        except Exception:
            deleted, updates = [], []

        # 先处理几何更新：确保第一步撤销就是还原擦除
        try:
            from app.core.commands.update_geometry_cmd import UpdateGeometryCommand
            from app.core.commands.delete_shape_cmd import DeleteShapeCommand
            mw = self.window()  # MainWindow
            if hasattr(mw, 'undo_stack'):
                us = mw.undo_stack  # type: ignore
                # 将整个擦除会话打包为一个宏，用户一次撤销即可还原全部
                us.beginMacro("擦除")
                # 先推几何更新
                for u in updates:
                    us.push(UpdateGeometryCommand(
                        u['item'], u['old_path'], u['new_path'],
                        u['old_pen'], u['new_pen'], u['old_brush'], u['new_brush'],
                        u.get('text', '更新几何')
                    ))
                # 再推删除命令
                for item in deleted:
                    # 不直接移除，交由命令 redo 执行
                    us.push(DeleteShapeCommand(self.scene(), item))
                us.endMacro()
        except Exception:
            # 退化路径：若无法访问撤销栈，至少执行删除
            for item in deleted:
                if item.scene():
                    item.scene().removeItem(item)

    def _create_item_from_payload(self, data: dict, at_scene_pos: QPointF | None = None) -> None:
        from app.core.shapes.circle_item import CircleItem
        from app.core.shapes.line_item import LineItem
        from app.core.shapes.rect_item import RectItem
        from app.core.shapes.polygon_item import PolygonItem
        from app.core.shapes.brush_path_item import BrushPathItem
        from PySide6.QtGui import QColor, QPen, QBrush, QPainterPath
        t = data.get("type")
        if t == "circle":
            cx = float(data.get("cx", 0)); cy = float(data.get("cy", 0)); r = float(data.get("r", 10))
            if at_scene_pos is not None:
                cx, cy = at_scene_pos.x(), at_scene_pos.y()
            item = CircleItem(cx, cy, r)
            pen = QPen(QColor(data.get("stroke", "#0066cc")), float(data.get("width", data.get("strokeWidth", 2.0))))
            try:
                from PySide6.QtCore import Qt as _Qt
                pen.setStyle(_Qt.PenStyle(int(data.get("style", 1))))
            except Exception:
                pass
            item.setPen(pen)
            item.setBrush(QBrush(QColor(data.get("fill", "#00000000"))))
            item.setOpacity(float(data.get("opacity", 1.0)))
            self.scene().addItem(item)
        elif t == "line":
            x1 = float(data.get("x1", 0)); y1 = float(data.get("y1", 0)); x2 = float(data.get("x2", 0)); y2 = float(data.get("y2", 0))
            if at_scene_pos is not None:
                dx = at_scene_pos.x() - x1; dy = at_scene_pos.y() - y1
                x1 += dx; y1 += dy; x2 += dx; y2 += dy
            item = LineItem(x1, y1, x2, y2)
            pen = QPen(QColor(data.get("stroke", "#333333")), float(data.get("width", data.get("strokeWidth", 2.0))))
            try:
                from PySide6.QtCore import Qt as _Qt
                pen.setStyle(_Qt.PenStyle(int(data.get("style", 1))))
            except Exception:
                pass
            item.setPen(pen)
            self.scene().addItem(item)
        elif t == "rect":
            # 兼容不同键名：rect_w/rect_h 或 w/h 或 width/height（几何）
            gw = data.get("rect_w", data.get("w", data.get("width", 10)))
            gh = data.get("rect_h", data.get("h", data.get("height", 10)))
            x = float(data.get("x", 0)); y = float(data.get("y", 0)); w = float(gw); h = float(gh)
            if at_scene_pos is not None:
                x, y = at_scene_pos.x(), at_scene_pos.y()
            item = RectItem(x, y, w, h)
            penw = float(data.get("strokeWidth", data.get("penWidth", data.get("pw", data.get("width", 2.0)))))
            pen = QPen(QColor(data.get("stroke", "#333333")), penw)
            try:
                from PySide6.QtCore import Qt as _Qt
                pen.setStyle(_Qt.PenStyle(int(data.get("style", 1))))
            except Exception:
                pass
            item.setPen(pen)
            item.setBrush(QBrush(QColor(data.get("fill", "#00000000"))))
            item.setOpacity(float(data.get("opacity", 1.0)))
            self.scene().addItem(item)
        elif t == "polygon":
            pts = [(float(x), float(y)) for x, y in data.get("points", [])]
            if at_scene_pos is not None and pts:
                dx = at_scene_pos.x() - pts[0][0]; dy = at_scene_pos.y() - pts[0][1]
                pts = [(x + dx, y + dy) for x, y in pts]
            item = PolygonItem()
            from PySide6.QtCore import QPointF
            item.set_polygon([QPointF(x, y) for x, y in pts])
            pen = QPen(QColor(data.get("stroke", "#333333")), float(data.get("width", data.get("strokeWidth", 2.0))))
            try:
                from PySide6.QtCore import Qt as _Qt
                pen.setStyle(_Qt.PenStyle(int(data.get("style", 1))))
            except Exception:
                pass
            item.setPen(pen)
            item.setBrush(QBrush(QColor(data.get("fill", "#00000000"))))
            item.setOpacity(float(data.get("opacity", 1.0)))
            self.scene().addItem(item)
        elif t == "brush_path":
            path_data = data.get("path", [])
            path = QPainterPath()
            for seg in path_data:
                cmd = seg.get("cmd"); x = float(seg.get("x", 0)); y = float(seg.get("y", 0))
                if cmd == "M":
                    path.moveTo(x, y)
                elif cmd == "L":
                    path.lineTo(x, y)
            if at_scene_pos is not None and not path.isEmpty():
                dx = at_scene_pos.x() - path.elementAt(0).x; dy = at_scene_pos.y() - path.elementAt(0).y
                path.translate(dx, dy)
            item = BrushPathItem(path)
            from PySide6.QtCore import Qt as _Qt
            pen = QPen(QColor(data.get("stroke", "#000000")), float(data.get("width", data.get("strokeWidth", 3.0))))
            pen.setStyle(_Qt.PenStyle(int(data.get("style", 1))))
            item.setPen(pen)
            item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            item.setOpacity(float(data.get("opacity", 1.0)))
            self.scene().addItem(item)
        else:
            return
        # 选中新建项并发出提交信号
        self.scene().clearSelection()
        try:
            item.setSelected(True)
        except Exception:
            pass
        self.shapeCommitted.emit(item)

    def _build_payload_from_item(self, item) -> dict | None:
        try:
            from PySide6.QtGui import QColor, QPainterPath
            from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem
            from app.core.shapes.circle_item import CircleItem
            # 圆/椭圆
            if isinstance(item, CircleItem) or isinstance(item, QGraphicsEllipseItem):
                if isinstance(item, CircleItem):
                    cx, cy, r = item.center_radius()
                else:
                    rect = item.rect(); r = rect.width() / 2.0; pos = item.scenePos(); cx, cy = pos.x(), pos.y()
                pen = item.pen(); brush = item.brush()
                return {"type": "circle", "cx": cx, "cy": cy, "r": r,
                        "stroke": pen.color().name(QColor.HexArgb), "width": pen.widthF(), "style": int(pen.style()),
                        "fill": brush.color().name(QColor.HexArgb), "opacity": float(item.opacity())}
            # 直线
            if isinstance(item, QGraphicsLineItem):
                ln = item.line(); pen = item.pen()
                return {"type": "line", "x1": ln.x1(), "y1": ln.y1(), "x2": ln.x2(), "y2": ln.y2(),
                        "stroke": pen.color().name(QColor.HexArgb), "width": pen.widthF(), "style": int(pen.style()),
                        "opacity": float(item.opacity())}
            # 矩形
            if isinstance(item, QGraphicsRectItem):
                rect = item.rect(); pos = item.scenePos(); pen = item.pen(); brush = item.brush()
                return {"type": "rect", "x": pos.x(), "y": pos.y(), "rect_w": rect.width(), "rect_h": rect.height(),
                        "stroke": pen.color().name(QColor.HexArgb), "strokeWidth": pen.widthF(), "style": int(pen.style()),
                        "fill": brush.color().name(QColor.HexArgb), "opacity": float(item.opacity())}
            # 多边形
            if isinstance(item, QGraphicsPolygonItem):
                poly = item.polygon(); pen = item.pen(); brush = item.brush()
                points = [(pt.x(), pt.y()) for pt in poly]
                return {"type": "polygon", "points": points,
                        "stroke": pen.color().name(QColor.HexArgb), "width": pen.widthF(), "style": int(pen.style()),
                        "fill": brush.color().name(QColor.HexArgb), "opacity": float(item.opacity())}
            # 画笔路径
            if isinstance(item, QGraphicsPathItem):
                path: QPainterPath = item.path(); pen = item.pen()
                segs = []
                for i in range(path.elementCount()):
                    el = path.elementAt(i)
                    if el.isMoveTo():
                        segs.append({"cmd": "M", "x": el.x, "y": el.y})
                    else:
                        segs.append({"cmd": "L", "x": el.x, "y": el.y})
                return {"type": "brush_path", "path": segs,
                        "stroke": pen.color().name(QColor.HexArgb), "width": pen.widthF(), "style": int(pen.style()),
                        "opacity": float(item.opacity())}
        except Exception:
            return None
        return None

    def _is_supported_item(self, item) -> bool:
        try:
            from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem
            from app.core.shapes.circle_item import CircleItem
            if isinstance(item, (CircleItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsPathItem)):
                return True
        except Exception:
            pass
        # 宽松判断：具备常见图元属性也视为可复制
        return all(hasattr(item, name) for name in ("pen", "opacity"))

    def _find_supported_selected_item(self):
        selected = self.scene().selectedItems()
        for it in selected:
            if self._is_supported_item(it):
                return it
        return None

    def keyPressEvent(self, event):  # type: ignore[override]
        if event.key() == Qt.Key_Escape and self._tool is self._polygon_tool and getattr(self._tool, "is_active", lambda: False)():
            # 取消正在创建的多边形
            self._polygon_tool.cancel(self.scene())
            self.setDragMode(QGraphicsView.RubberBandDrag)
            event.accept()
            return
        if event.key() == Qt.Key_Space and not self._space_held:
            self._space_held = True
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):  # type: ignore[override]
        if event.key() == Qt.Key_Space and self._space_held:
            self._space_held = False
            if self._panning:
                # 若正在平移，释放空格后结束平移
                self._panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().keyReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):  # type: ignore[override]
        if self._tool is not None and isinstance(self._tool, PolygonTool):
            self._polygon_tool.double_click(self.scene())
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def export_png(self, path: str) -> bool:
        rect: QRectF = self.sceneRect()
        width = max(1, int(rect.width()))
        height = max(1, int(rect.height()))
        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(0x00000000)
        painter = QPainter(image)
        self.render(painter)
        painter.end()
        return image.save(path)

    # 删除选中（由视图捕获按键是可选；这里放在 MainWindow 里做也行）
    def delete_selected(self) -> None:
        for item in list(self.scene().selectedItems()):
            self.deleteRequested.emit(item)

    def copy_selected(self) -> None:
        item = self._find_supported_selected_item()
        if item is None:
            # 尝试使用鼠标当前位置命中一个可复制图元
            try:
                from PySide6.QtGui import QCursor
                pos_view = self.mapFromGlobal(QCursor.pos())
                hit = self.itemAt(pos_view)
                if hit is not None and self._is_supported_item(hit):
                    item = hit
                else:
                    # 最后兜底：若命中失败但有任何选中项，取第一个进行通用复制
                    sel = list(self.scene().selectedItems())
                    if sel:
                        item = sel[0]
                    else:
                        self.copyCompleted.emit(False)
                        return
            except Exception:
                self.copyCompleted.emit(False)
                return
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QColor
            import json
            # 优先特定类型的 payload
            payload = self._build_payload_from_item(item)
            # 通用兜底：用包围盒创建矩形
            if payload is None:
                payload = self._fallback_payload_any(item)
            if payload is not None:
                text = json.dumps(payload)
                mime = QMimeData()
                # 同一个 QMimeData 同时设置文本与自定义 MIME，避免平台覆盖
                mime.setText(text)
                mime.setData("application/x-graphics-shape", text.encode("utf-8"))
                cb = QApplication.clipboard()
                cb.setMimeData(mime)
                self._last_copied_payload = payload
                self.copyCompleted.emit(True)
                return
        except Exception:
            self.copyCompleted.emit(False)

    def _fallback_payload_any(self, item) -> dict | None:
        try:
            from PySide6.QtGui import QColor
            rect = item.sceneBoundingRect()
            pen = getattr(item, 'pen', lambda: None)()
            stroke = pen.color().name(QColor.HexArgb) if pen is not None else "#333333"
            width = float(getattr(pen, 'widthF', lambda: 2.0)()) if pen is not None else 2.0
            return {
                "type": "rect",
                "x": rect.x(), "y": rect.y(),
                "rect_w": rect.width(), "rect_h": rect.height(),
                "stroke": stroke,
                "strokeWidth": width,
                "style": int(getattr(pen, 'style', lambda: 1)()),
                "fill": "#00000000",
                "opacity": float(getattr(item, 'opacity', lambda: 1.0)()),
            }
        except Exception:
            return None

    def paste_from_clipboard(self, at_scene_pos: QPointF | None = None) -> None:
        try:
            from PySide6.QtWidgets import QApplication
            import json

            cb = QApplication.clipboard()
            md = cb.mimeData()
            text = None
            if md and md.hasFormat("application/x-graphics-shape"):
                try:
                    ba = md.data("application/x-graphics-shape")
                    text = bytes(ba).decode("utf-8")
                except Exception:
                    text = None
            if not text:
                text = cb.text()
            data = None
            try:
                data = json.loads(text) if text else None
            except Exception:
                data = None
            # 读取失败时使用内存兜底
            if not isinstance(data, dict) and isinstance(self._last_copied_payload, dict):
                data = dict(self._last_copied_payload)
            if not isinstance(data, dict):
                self.pasteCompleted.emit(False)
                return
            self._create_item_from_payload(data, at_scene_pos)
            self.pasteCompleted.emit(True)
        except Exception:
            self.pasteCompleted.emit(False)

    def begin_paste_from_clipboard(self) -> None:
        """进入‘点击画布以粘贴’模式，从剪贴板解析 payload，等待用户点击场景位置。"""
        try:
            from PySide6.QtWidgets import QApplication
            import json
            cb = QApplication.clipboard()
            md = cb.mimeData()
            text = None
            if md and md.hasFormat("application/x-graphics-shape"):
                try:
                    ba = md.data("application/x-graphics-shape")
                    text = bytes(ba).decode("utf-8")
                except Exception:
                    text = None
            if not text:
                text = cb.text()
            data = None
            try:
                data = json.loads(text) if text else None
            except Exception:
                data = None
            if not isinstance(data, dict) and isinstance(self._last_copied_payload, dict):
                data = dict(self._last_copied_payload)
            if not isinstance(data, dict):
                return
            self._pending_paste_payload = data
            self.setCursor(Qt.CrossCursor)
        except Exception:
            self._pending_paste_payload = None

    def contextMenuEvent(self, event):  # type: ignore[override]
        # 若当前无选择，则尝试选中右键位置下的图元，方便复制
        hit = self.itemAt(event.pos())
        if not self.scene().selectedItems():
            if hit is not None:
                self.scene().clearSelection()
                hit.setSelected(True)
                self._last_context_item = hit
            else:
                self._last_context_item = None
        menu = QMenu(self)
        act_del = menu.addAction("删除")
        act_copy = menu.addAction("复制")
        act_paste = menu.addAction("粘贴")
        # 根据状态启用/禁用（放宽：有命中或有选择即可复制/删除）
        sel_items = self.scene().selectedItems()
        has_any_target = bool(sel_items) or (hit is not None)
        act_del.setEnabled(has_any_target)
        act_copy.setEnabled(has_any_target)
        # 粘贴有效性检查（放宽）：剪贴板有自定义 MIME 或者文本非空即可尝试
        try:
            from PySide6.QtWidgets import QApplication
            cb = QApplication.clipboard()
            md = cb.mimeData()
            enabled = False
            if md and (md.hasFormat("application/x-graphics-shape") or (cb.text() or "").strip()):
                enabled = True
            act_paste.setEnabled(enabled)
        except Exception:
            act_paste.setEnabled(False)
        action = menu.exec(event.globalPos())
        if action == act_del:
            self.delete_selected()
        elif action == act_copy:
            # 若此前命中到了图元（哪怕没选中），直接基于命中项复制
            if self._last_context_item is not None:
                try:
                    from PySide6.QtWidgets import QApplication
                    import json
                    payload = self._build_payload_from_item(self._last_context_item)
                    if payload is None:
                        payload = self._fallback_payload_any(self._last_context_item)
                    if payload:
                        text = json.dumps(payload)
                        mime = QMimeData(); mime.setText(text); mime.setData("application/x-graphics-shape", text.encode("utf-8"))
                        cb = QApplication.clipboard(); cb.setMimeData(mime)
                        self.copyCompleted.emit(True)
                    else:
                        self.copyCompleted.emit(False)
                except Exception:
                    self.copyCompleted.emit(False)
            else:
                self.copy_selected()
        elif action == act_paste:
            self.paste_from_clipboard(self.mapToScene(event.pos()))
        event.accept()

    def _refresh_current_pen_obj(self) -> None:
        from PySide6.QtGui import QPen
        self._current_pen_obj = QPen(self._current_pen_color, float(self._current_pen_width))
        try:
            self._current_pen_obj.setCosmetic(True)
        except Exception:
            pass
        self._current_pen_obj.setStyle(self._current_pen_style)


