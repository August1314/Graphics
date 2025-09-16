from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPoint, QPointF, Qt, QRectF, Signal, QMimeData
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu

from app.core.tools.base_tool import BaseTool
from app.core.tools.circle_tool import CircleTool
from app.core.tools.point_tool import PointTool
from app.core.tools.line_tool import LineTool
from app.core.tools.rect_tool import RectTool
from app.core.tools.polygon_tool import PolygonTool


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
        # 提交后自动选中新建的图元
        self._circle_tool.on_committed(self._auto_select_item)
        self._point_tool.on_committed(self._auto_select_item)
        self._line_tool.on_committed(self._auto_select_item)
        self._rect_tool.on_committed(self._auto_select_item)
        self._polygon_tool.on_committed(self._auto_select_item)
        self._dragged_item = None
        self._drag_start_pos: QPointF | None = None
        self._pending_paste_payload: dict | None = None
        self._last_context_item = None

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
                self._tool.on_press(self.scene(), scene_pos, event)
                event.accept()
                return
        # 记录拖动起点（选择模式下拖动选中图元）
        if event.button() == Qt.LeftButton and self._tool is None:
            top_item = self.itemAt(event.pos())
            if top_item is not None and top_item.isSelected():
                self._dragged_item = top_item
                self._drag_start_pos = top_item.pos()
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
        # 非绘制状态下，移动可能拖动已选中的图元，通知属性面板刷新
        if event.buttons() & Qt.LeftButton and self.scene().selectedItems():
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
            if self._drag_start_pos is not None and (new_pos != self._drag_start_pos):
                self.moveCommitted.emit(self._dragged_item, self._drag_start_pos, new_pos)
            self._dragged_item = None
            self._drag_start_pos = None
        super().mouseReleaseEvent(event)

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
        else:
            self._tool = None

    def _auto_select_item(self, item):
        # 清空当前选择并选中新建项
        self.scene().clearSelection()
        item.setSelected(True)
        self.shapeCommitted.emit(item)

    def _create_item_from_payload(self, data: dict, at_scene_pos: QPointF | None = None) -> None:
        from app.core.shapes.circle_item import CircleItem
        from PySide6.QtGui import QColor, QPen, QBrush
        if data.get("type") == "circle":
            cx = float(data.get("cx", 0))
            cy = float(data.get("cy", 0))
            r = float(data.get("r", 10))
            if at_scene_pos is not None:
                cx, cy = at_scene_pos.x(), at_scene_pos.y()
            item = CircleItem(cx, cy, r)
            pen = QPen(QColor(data.get("stroke", "#0066cc")), float(data.get("width", 2.0)))
            try:
                from PySide6.QtCore import Qt as _Qt
                pen.setStyle(_Qt.PenStyle(int(data.get("style", 1))))
            except Exception:
                pass
            item.setPen(pen)
            item.setBrush(QBrush(QColor(data.get("fill", "#00000000"))))
            item.setOpacity(float(data.get("opacity", 1.0)))
            self.scene().addItem(item)
            self.scene().clearSelection()
            item.setSelected(True)
            self.shapeCommitted.emit(item)

    def _build_payload_from_item(self, item) -> dict | None:
        try:
            from PySide6.QtGui import QColor
            from app.core.shapes.circle_item import CircleItem
            from PySide6.QtWidgets import QGraphicsEllipseItem
            if isinstance(item, CircleItem):
                cx, cy, r = item.center_radius()
                pen = item.pen(); brush = item.brush()
                return {
                    "type": "circle",
                    "cx": cx, "cy": cy, "r": r,
                    "stroke": pen.color().name(QColor.HexArgb),
                    "width": pen.widthF(),
                    "style": int(pen.style()),
                    "fill": brush.color().name(QColor.HexArgb),
                    "opacity": float(item.opacity()),
                }
            if isinstance(item, QGraphicsEllipseItem):
                rect = item.rect(); r = rect.width() / 2.0
                pos = item.scenePos(); pen = item.pen(); brush = item.brush()
                return {
                    "type": "circle",
                    "cx": pos.x(), "cy": pos.y(), "r": r,
                    "stroke": pen.color().name(QColor.HexArgb),
                    "width": pen.widthF(),
                    "style": int(pen.style()),
                    "fill": brush.color().name(QColor.HexArgb),
                    "opacity": float(item.opacity()),
                }
        except Exception:
            return None
        return None

    def _is_supported_item(self, item) -> bool:
        try:
            from app.core.shapes.circle_item import CircleItem
            from PySide6.QtWidgets import QGraphicsEllipseItem
            if isinstance(item, (CircleItem, QGraphicsEllipseItem)):
                return True
        except Exception:
            pass
        # 宽松判断：具备椭圆关键属性也视为可复制
        return all(hasattr(item, name) for name in ("rect", "pen", "brush", "scenePos", "opacity"))

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
                    self.copyCompleted.emit(False)
                    return
            except Exception:
                self.copyCompleted.emit(False)
                return
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QColor
            import json
            # 宽松检查：尽可能从任意“椭圆样式”的图元构建 payload
            payload = self._build_payload_from_item(item)
            if payload is None and hasattr(item, 'rect') and hasattr(item, 'pen') and hasattr(item, 'brush') and hasattr(item, 'scenePos') and hasattr(item, 'opacity'):
                rect = item.rect()
                r = rect.width() / 2.0
                pos = item.scenePos()
                pen = item.pen()
                brush = item.brush()
                payload = {
                    "type": "circle",
                    "cx": pos.x(),
                    "cy": pos.y(),
                    "r": r,
                    "stroke": pen.color().name(QColor.HexArgb),
                    "width": pen.widthF(),
                    "style": int(pen.style()),
                    "fill": brush.color().name(QColor.HexArgb),
                    "opacity": float(item.opacity()),
                }
            if payload is None and hasattr(item, 'sceneBoundingRect') and hasattr(item, 'pen') and hasattr(item, 'brush') and hasattr(item, 'opacity'):
                # 最后兜底：使用包围盒作为圆，中心取 sceneBoundingRect 中心，半径取较大边/2
                rect = item.sceneBoundingRect()
                r = max(rect.width(), rect.height()) / 2.0
                center = rect.center()
                pen = item.pen(); brush = item.brush()
                payload = {
                    "type": "circle",
                    "cx": center.x(),
                    "cy": center.y(),
                    "r": r,
                    "stroke": pen.color().name(QColor.HexArgb),
                    "width": pen.widthF(),
                    "style": int(pen.style()),
                    "fill": brush.color().name(QColor.HexArgb),
                    "opacity": float(item.opacity()),
                }

            if payload is not None:
                text = json.dumps(payload)
                mime = QMimeData()
                mime.setText(text)
                mime.setData("application/x-graphics-shape", text.encode("utf-8"))
                cb = QApplication.clipboard()
                # 先写入纯文本，再写入自定义 MIME（某些平台需要此顺序）
                cb.setText(text)
                cb.setMimeData(mime)
                self.copyCompleted.emit(True)
                return
        except Exception:
            self.copyCompleted.emit(False)

    def paste_from_clipboard(self, at_scene_pos: QPointF | None = None) -> None:
        try:
            from PySide6.QtWidgets import QApplication
            import json

            cb = QApplication.clipboard()
            md = cb.mimeData()
            text = md.data("application/x-graphics-shape").data().decode("utf-8") if md.hasFormat("application/x-graphics-shape") else cb.text()
            data = json.loads(text)
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
            text = md.data("application/x-graphics-shape").data().decode("utf-8") if md and md.hasFormat("application/x-graphics-shape") else cb.text()
            data = json.loads(text)
            if not isinstance(data, dict):
                return
            self._pending_paste_payload = data
            self.setCursor(Qt.CrossCursor)
        except Exception:
            self._pending_paste_payload = None

    def contextMenuEvent(self, event):  # type: ignore[override]
        # 若当前无选择，则尝试选中右键位置下的图元，方便复制
        if not self.scene().selectedItems():
            hit = self.itemAt(event.pos())
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
        # 根据状态启用/禁用（仅当选中的是圆时开放复制）
        sel_items = self.scene().selectedItems()
        has_supported = any(self._is_supported_item(it) for it in sel_items)
        act_del.setEnabled(bool(sel_items))
        act_copy.setEnabled(has_supported)
        # 粘贴有效性检查（优先自定义 MIME，其次纯文本 JSON）
        try:
            from PySide6.QtWidgets import QApplication
            import json
            cb = QApplication.clipboard()
            md = cb.mimeData()
            enabled = False
            if md and md.hasFormat("application/x-graphics-shape"):
                enabled = True
            else:
                txt = cb.text()
                data = json.loads(txt)
                enabled = isinstance(data, dict) and data.get("type") == "circle"
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
                    if payload:
                        text = json.dumps(payload)
                        mime = QMimeData(); mime.setText(text); mime.setData("application/x-graphics-shape", text.encode("utf-8"))
                        cb = QApplication.clipboard(); cb.setText(text); cb.setMimeData(mime)
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


