from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPoint, QPointF, Qt, QRectF, Signal
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu

from app.core.tools.base_tool import BaseTool
from app.core.tools.circle_tool import CircleTool


class CanvasView(QGraphicsView):
    selectionGeometryChanged = Signal()
    shapeCommitted = Signal(object)
    moveCommitted = Signal(object, object, object)
    deleteRequested = Signal(object)
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
        # 提交后自动选中新建的图元
        self._circle_tool.on_committed(self._auto_select_item)
        self._dragged_item = None
        self._drag_start_pos: QPointF | None = None

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
        # 仅在左键点击空白区域且有绘制工具时，启动绘制
        if event.button() == Qt.LeftButton and self._tool is not None:
            top_item = self.itemAt(event.pos())
            if top_item is None:  # 空白区域
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
        if name == "circle" or name == "ellipse":
            self._tool = self._circle_tool
        else:
            self._tool = None

    def _auto_select_item(self, item):
        # 清空当前选择并选中新建项
        self.scene().clearSelection()
        item.setSelected(True)
        self.shapeCommitted.emit(item)

    def keyPressEvent(self, event):  # type: ignore[override]
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
        items = self.scene().selectedItems()
        if not items:
            return
        item = items[0]
        try:
            from PySide6.QtGui import QGuiApplication, QColor
            import json
            from app.core.shapes.circle_item import CircleItem

            payload = None
            if isinstance(item, CircleItem):
                cx, cy, r = item.center_radius()
                pen = item.pen()
                brush = item.brush()
                payload = {
                    "type": "circle",
                    "cx": cx,
                    "cy": cy,
                    "r": r,
                    "stroke": pen.color().name(QColor.HexArgb),
                    "width": pen.widthF(),
                    "style": int(pen.style()),
                    "fill": brush.color().name(QColor.HexArgb),
                    "opacity": float(item.opacity()),
                }
            if payload is not None:
                QGuiApplication.clipboard().setText(json.dumps(payload))
        except Exception:
            pass

    def paste_from_clipboard(self, at_scene_pos: QPointF | None = None) -> None:
        try:
            from PySide6.QtGui import QGuiApplication
            import json
            from app.core.shapes.circle_item import CircleItem
            from PySide6.QtGui import QColor, QPen, QBrush

            text = QGuiApplication.clipboard().text()
            data = json.loads(text)
            if not isinstance(data, dict):
                return
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
        except Exception:
            pass

    def contextMenuEvent(self, event):  # type: ignore[override]
        menu = QMenu(self)
        act_del = menu.addAction("删除")
        act_copy = menu.addAction("复制")
        act_paste = menu.addAction("粘贴")
        # 根据状态启用/禁用（仅当选中的是圆时开放复制）
        sel_items = self.scene().selectedItems()
        has_circle = False
        if sel_items:
            try:
                from app.core.shapes.circle_item import CircleItem
                has_circle = isinstance(sel_items[0], CircleItem)
            except Exception:
                has_circle = False
        act_del.setEnabled(bool(sel_items))
        act_copy.setEnabled(has_circle)
        # 粘贴有效性检查
        try:
            from PySide6.QtGui import QGuiApplication
            import json
            txt = QGuiApplication.clipboard().text()
            data = json.loads(txt)
            act_paste.setEnabled(isinstance(data, dict) and data.get("type") == "circle")
        except Exception:
            act_paste.setEnabled(False)
        action = menu.exec(event.globalPos())
        if action == act_del:
            self.delete_selected()
        elif action == act_copy:
            self.copy_selected()
        elif action == act_paste:
            self.paste_from_clipboard(self.mapToScene(event.pos()))
        event.accept()


