from __future__ import annotations

from typing import Optional, List, Callable, Set

try:
    import pyclipper  # type: ignore
    _HAS_PYCLIPPER = True
except Exception:
    _HAS_PYCLIPPER = False

from PySide6.QtCore import QPointF, QTimer, Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QMouseEvent, QPainterPathStroker
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPathItem, QGraphicsItem, QGraphicsEllipseItem

from app.core.tools.base_tool import BaseTool
from app.core.commands.update_geometry_cmd import UpdateGeometryCommand


class EraserTool(BaseTool):
    """商业级橡皮擦工具

    - 普通橡皮擦: 将笔画几何与橡皮擦几何做差集 (object - eraser)
    - 对象橡皮擦: 直接删除命中的对象

    优先使用 pyclipper 做鲁棒布尔运算；不可用时退回 Qt 的 QPainterPath.subtracted。
    为避免复杂度爆炸，首次将中心线转换为几何，之后一直在几何上做差集。
    """

    class EraserMode:
        PATH_ERASER = "path_eraser"
        OBJECT_ERASER = "object_eraser"

    def __init__(self, mode: str = EraserMode.OBJECT_ERASER) -> None:
        super().__init__()
        self._mode = mode
        self._active = False
        self._on_committed: Optional[Callable[[List[QGraphicsItem]], None]] = None

        # eraser state
        self._size: float = 15.0
        self._color: QColor = QColor("#FF0000")
        self._opacity: float = 0.3

        self._points: List[QPointF] = []
        self._current_path: Optional[QPainterPath] = None
        self._eraser_preview: Optional[QGraphicsEllipseItem] = None
        self._eraser_path: Optional[QPainterPath] = None  # scene-space union of eraser dabs

        self._min_distance: float = 3.0
        self._smoothing: bool = True
        self._opt_timer = QTimer()
        self._opt_timer.setSingleShot(True)
        self._opt_timer.timeout.connect(self._finalize_erasing)

        # affected items: item -> { 'path': QPainterPath, 'mode': 'center'|'geometry', 'pen': QPen }
        self._affected: dict[QGraphicsPathItem, dict] = {}
        self._erased_items: Set[QGraphicsItem] = set()

    # ---------- public API ----------
    def set_mode(self, mode: str) -> None:
        self._mode = mode

    def set_size(self, size: float) -> None:
        self._size = max(1.0, min(200.0, size))
        if self._eraser_preview:
            self._eraser_preview.setRect(0, 0, self._size, self._size)

    def get_size(self) -> float:
        return self._size

    def on_committed(self, cb: Callable[[List[QGraphicsItem]], None]) -> None:
        self._on_committed = cb

    def is_active(self) -> bool:
        return self._active

    def cancel(self, scene: QGraphicsScene) -> None:
        self._cleanup_preview(scene)
        self._reset_state()

    # ---------- interaction ----------
    def on_press(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if event.button() != event.button().LeftButton:
            return
        self._active = True
        self._points = [scene_pos]
        self._erased_items.clear()

        if self._mode == self.EraserMode.PATH_ERASER:
            self._begin_path_erase(scene, scene_pos)
        else:
            self._begin_object_erase(scene, scene_pos)

    def on_move(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if not self._active:
            return
        if self._points and self._distance(scene_pos, self._points[-1]) < self._min_distance:
            return
        self._points.append(scene_pos)

        if self._mode == self.EraserMode.PATH_ERASER:
            self._continue_path_erase(scene, scene_pos)
        else:
            self._continue_object_erase(scene, scene_pos)

    def on_release(self, scene: QGraphicsScene, scene_pos: QPointF, event: QMouseEvent) -> None:
        if not self._active:
            return
        if self._mode == self.EraserMode.PATH_ERASER and self._smoothing and len(self._points) >= 3:
            self._opt_timer.start(30)
        else:
            self._finalize_erasing()

    # ---------- path eraser ----------
    def _begin_path_erase(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        self._create_preview(scene, scene_pos)
        self._eraser_path = QPainterPath()
        self._add_eraser_dab(scene_pos)
        self._affected.clear()
        self._collect_affected_items(scene, scene_pos)
        self._apply_realtime()

    def _continue_path_erase(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        if self._eraser_preview:
            self._eraser_preview.setPos(scene_pos.x() - self._size / 2.0, scene_pos.y() - self._size / 2.0)
        self._add_eraser_dab(scene_pos)
        self._collect_affected_items(scene, scene_pos)
        self._apply_realtime()

    def _add_eraser_dab(self, scene_pos: QPointF) -> None:
        if self._eraser_path is None:
            self._eraser_path = QPainterPath()
        self._eraser_path.addEllipse(scene_pos.x() - self._size / 2.0,
                                     scene_pos.y() - self._size / 2.0,
                                     self._size, self._size)

    # ---------- object eraser ----------
    def _begin_object_erase(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        self._create_preview(scene, scene_pos)
        self._delete_objects_at(scene, scene_pos)

    def _continue_object_erase(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        if self._eraser_preview:
            self._eraser_preview.setPos(scene_pos.x() - self._size / 2.0, scene_pos.y() - self._size / 2.0)
        self._delete_objects_at(scene, scene_pos)

    # ---------- realtime preview ----------
    def _apply_realtime(self) -> None:
        if not self._eraser_path:
            return
        for item, st in self._affected.items():
            self._preview_boolean(item, st)

    def _preview_boolean(self, item: QGraphicsPathItem, st: dict) -> None:
        try:
            base = st.get('path')
            inv, ok = item.sceneTransform().inverted()
            if not ok:
                return
            local_eraser = inv.map(self._eraser_path)
            pen: QPen = st.get('pen') or item.pen()

            # base geometry
            if base is None or st.get('mode', 'center') == 'center':
                center_path = st.get('orig_path') or item.path()
                base = self._stroke_to_geometry(center_path, pen)

            result = self._difference(base, local_eraser)

            item.setPath(result)
            # filled rendering for geometry
            item.setPen(Qt.PenStyle.NoPen)
            item.setBrush(QBrush(pen.color()))

            # store geometry for subsequent operations
            st['path'] = result
            st['mode'] = 'geometry'
            st['pen'] = pen
        except Exception:
            return

    # ---------- finalize ----------
    def _finalize_erasing(self) -> None:
        items_to_remove: List[QGraphicsItem] = []
        geometry_updates_payload: List[dict] = []
        if self._mode == self.EraserMode.PATH_ERASER:
            for item, st in list(self._affected.items()):
                try:
                    base = st.get('path')
                    inv, ok = item.sceneTransform().inverted()
                    if not ok or self._eraser_path is None:
                        continue
                    local_eraser = inv.map(self._eraser_path)
                    pen: QPen = st.get('pen') or item.pen()
                    if base is None or st.get('mode', 'center') == 'center':
                        center_path = st.get('orig_path') or item.path()
                        base = self._stroke_to_geometry(center_path, pen)
                    result = self._difference(base, local_eraser)
                    if result.isEmpty():
                        items_to_remove.append(item)
                    else:
                        # 记录可撤销更新载荷（由上层推入 undo 栈）
                        geometry_updates_payload.append({
                            'item': item,
                            'old_path': st.get('orig_path') or item.path(),
                            'new_path': result,
                            'old_pen': st.get('orig_pen') or item.pen(),
                            'new_pen': QPen(Qt.PenStyle.NoPen),
                            'old_brush': st.get('orig_brush') or item.brush(),
                            'new_brush': QBrush(pen.color()),
                            'text': '擦除'
                        })
                        # 直接应用新几何以呈现最终效果
                        item.setPath(result)
                        item.setPen(Qt.PenStyle.NoPen)
                        item.setBrush(QBrush(pen.color()))
                        st['path'] = result
                        st['mode'] = 'geometry'
                        st['pen'] = pen
                except Exception:
                    continue
        else:
            items_to_remove.extend(list(self._erased_items))

        # 将结果交给上层（CanvasView/MainWindow）统一处理与推入撤销栈
        if self._on_committed:
            self._on_committed({'deleted': items_to_remove, 'updates': geometry_updates_payload})

        # reset
        self._reset_state()

    # ---------- helpers ----------
    def _create_preview(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        if self._eraser_preview and self._eraser_preview.scene():
            scene.removeItem(self._eraser_preview)
        self._eraser_preview = QGraphicsEllipseItem(0, 0, self._size, self._size)
        self._eraser_preview.setPos(scene_pos.x() - self._size / 2.0, scene_pos.y() - self._size / 2.0)
        self._eraser_preview.setPen(QPen(self._color, 2))
        self._eraser_preview.setBrush(QBrush(self._color, Qt.BrushStyle.NoBrush))
        self._eraser_preview.setOpacity(self._opacity)
        self._eraser_preview.setZValue(1000)
        scene.addItem(self._eraser_preview)

    def _collect_affected_items(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        rect = QRectF(scene_pos.x() - self._size / 2.0, scene_pos.y() - self._size / 2.0, self._size, self._size)
        for it in scene.items(rect):
            if not isinstance(it, QGraphicsPathItem) or it is self._eraser_preview:
                continue
            if it not in self._affected:
                self._affected[it] = {
                    # 原始状态（用于撤销）
                    'orig_path': it.path(),
                    'orig_pen': it.pen(),
                    'orig_brush': it.brush(),
                    # 运行态（用于布尔运算与预览）
                    'path': None,
                    'mode': 'center',
                    'pen': it.pen()
                }

    def _delete_objects_at(self, scene: QGraphicsScene, scene_pos: QPointF) -> None:
        rect = QRectF(scene_pos.x() - self._size / 2.0, scene_pos.y() - self._size / 2.0, self._size, self._size)
        for it in scene.items(rect):
            if it is self._eraser_preview:
                continue
            self._erased_items.add(it)

    def _cleanup_preview(self, scene: QGraphicsScene) -> None:
        if self._eraser_preview and self._eraser_preview.scene():
            scene.removeItem(self._eraser_preview)
        self._eraser_preview = None

    def _reset_state(self) -> None:
        self._active = False
        self._points.clear()
        self._current_path = None
        self._eraser_path = None
        self._affected.clear()
        self._erased_items.clear()
        self._opt_timer.stop()

    # ---- geometry/boolean helpers ----
    def _stroke_to_geometry(self, path: QPainterPath, pen: QPen) -> QPainterPath:
        stroker = QPainterPathStroker()
        stroker.setWidth(max(0.1, pen.widthF()))
        stroker.setCapStyle(pen.capStyle())
        stroker.setJoinStyle(pen.joinStyle())
        return stroker.createStroke(path)

    def _difference(self, subject: QPainterPath, clip: QPainterPath) -> QPainterPath:
        if subject.isEmpty():
            return QPainterPath()
        if clip.isEmpty():
            return subject
        if _HAS_PYCLIPPER:
            try:
                scale = 100.0  # enough precision
                subj_polys = self._to_polygons(subject, scale)
                clip_polys = self._to_polygons(clip, scale)
                pc = pyclipper.Pyclipper()
                pc.AddPaths(subj_polys, pyclipper.PT_SUBJECT, True)
                pc.AddPaths(clip_polys, pyclipper.PT_CLIP, True)
                solution = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
                return self._from_polygons(solution, scale)
            except Exception:
                pass
        # fallback
        return subject.subtracted(clip)

    def _to_polygons(self, path: QPainterPath, scale: float) -> List[List[tuple[int, int]]]:
        polys = path.toFillPolygons()
        out: List[List[tuple[int, int]]] = []
        for poly in polys:
            pts: List[tuple[int, int]] = []
            for p in poly:
                pts.append((int(round(p.x() * scale)), int(round(p.y() * scale))))
            if len(pts) >= 3:
                out.append(pts)
        return out

    def _from_polygons(self, paths: List[List[tuple[int, int]]], scale: float) -> QPainterPath:
        res = QPainterPath()
        for poly in paths:
            if not poly:
                continue
            first = True
            for x, y in poly:
                px = x / scale
                py = y / scale
                if first:
                    res.moveTo(px, py)
                    first = False
                else:
                    res.lineTo(px, py)
            res.closeSubpath()
        return res

    @staticmethod
    def _distance(a: QPointF, b: QPointF) -> float:
        dx = a.x() - b.x()
        dy = a.y() - b.y()
        return (dx * dx + dy * dy) ** 0.5


