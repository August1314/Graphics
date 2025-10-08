from __future__ import annotations

import logging
from typing import Any, Dict, List

from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsItem,
    QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsPathItem,
)

logger = logging.getLogger('drawing_app.serializer')


def encode_color(c: QColor) -> str:
    return c.name(QColor.HexArgb)


def decode_color(s: str) -> QColor:
    try:
        return QColor(s)
    except Exception:
        return QColor("#FF000000")


def encode_pen(p: QPen) -> Dict[str, Any]:
    return {
        "color": encode_color(p.color()),
        "width": float(p.widthF()),
        "style": int(p.style().value),
    }


def apply_pen(item, data: Dict[str, Any]) -> None:
    p = item.pen()
    if "color" in data:
        p.setColor(decode_color(str(data["color"])) )
    if "width" in data:
        try:
            p.setWidthF(float(data["width"]))
        except Exception:
            pass
    if "style" in data:
        from PySide6.QtCore import Qt
        try:
            p.setStyle(Qt.PenStyle(int(data["style"])) )
        except Exception:
            pass
    item.setPen(p)


def dump(scene: QGraphicsScene) -> Dict[str, Any]:
    shapes: List[Dict[str, Any]] = []
    items = list(scene.items())
    
    # 保存前先取消所有选中状态，避免高亮效果被保存
    selected_items = scene.selectedItems()
    for item in selected_items:
        item.setSelected(False)
    
    # Qt 返回的是从上到下，这里按自然顺序导出（保持视觉层级即可）
    for it in items:
        try:
            tname = it.__class__.__name__
            # 先用类名快速匹配，避免 import/多实例环境造成 isinstance 失配
            if tname == "BrushPathItem":
                logger.debug("找到 BrushPathItem，调用 to_dict()")
                try:
                    data = it.to_dict()  # type: ignore[attr-defined]
                    logger.debug(f"to_dict() 返回: {data}")
                except Exception as e:
                    logger.warning(f"to_dict() 异常: {e}")
                    # 基础导出：采样路径
                    path = it.path(); pts = []
                    for i in range(path.elementCount()):
                        e = path.elementAt(i)
                        pts.append([float(e.x), float(e.y)])
                    data = {"points": pts, "brush_type": "pen", "smoothing": True}
                    logger.debug(f"使用基础导出: {data}")
                if data:
                    data["pen"] = encode_pen(it.pen())
                    data["type"] = "brush_path"
                    shapes.append(data)
                    logger.debug(f"成功添加 BrushPathItem 到 shapes，当前 shapes 长度: {len(shapes)}")
                else:
                    logger.warning("data 为空，跳过")
                continue
            if tname == "CircleItem":
                cx = getattr(it, "center_radius")()[0]
                cy = getattr(it, "center_radius")()[1]
                r = getattr(it, "center_radius")()[2]
                shapes.append({"type": "circle", "cx": cx, "cy": cy, "r": r, "pen": encode_pen(it.pen())})
                continue
            if tname == "LineItem":
                ln = it.line(); shapes.append({"type": "line", "x1": ln.x1(), "y1": ln.y1(), "x2": ln.x2(), "y2": ln.y2(), "pen": encode_pen(it.pen())})
                continue
            if tname == "RectItem":
                r = it.rect(); shapes.append({"type": "rect", "x": r.x(), "y": r.y(), "width": r.width(), "height": r.height(), "pen": encode_pen(it.pen())})
                continue
            if tname == "PolygonItem":
                poly = it.polygon(); pts = [[p.x(), p.y()] for p in poly]
                shapes.append({"type": "polygon", "points": pts, "pen": encode_pen(it.pen())})
                continue
            if tname == "PointItem":
                rect = it.rect(); pos = it.pos(); r = rect.width() / 2.0
                shapes.append({"type": "point", "x": pos.x(), "y": pos.y(), "r": r, "pen": encode_pen(it.pen())})
                continue

            # 优先识别自定义类型
            try:
                from app.core.shapes.brush_path_item import BrushPathItem  # type: ignore
                if isinstance(it, BrushPathItem):
                    logger.debug("找到 BrushPathItem，调用 to_dict()")
                    data = it.to_dict()  # type: ignore[attr-defined]
                    logger.debug(f"to_dict() 返回: {data}")
                    if data:
                        data["pen"] = encode_pen(it.pen())
                        data["type"] = "brush_path"
                        shapes.append(data)
                        logger.debug("成功添加 BrushPathItem 到 shapes")
                    else:
                        logger.warning("to_dict() 返回 None 或空数据")
                    continue
            except Exception as e:
                logger.warning(f"BrushPathItem isinstance 检查失败: {e}")
                # 尝试通过类名匹配
                if tname == "BrushPathItem":
                    logger.debug("通过类名匹配找到 BrushPathItem")
                    try:
                        data = it.to_dict()  # type: ignore[attr-defined]
                        logger.debug(f"to_dict() 返回: {data}")
                        if data:
                            data["pen"] = encode_pen(it.pen())
                            data["type"] = "brush_path"
                            shapes.append(data)
                            logger.debug("成功添加 BrushPathItem 到 shapes")
                        else:
                            logger.warning("to_dict() 返回 None 或空数据")
                        continue
                    except Exception as e2:
                        logger.error(f"BrushPathItem to_dict() 失败: {e2}")
                pass
            try:
                from app.core.shapes.circle_item import CircleItem
                if isinstance(it, CircleItem):
                    cx, cy, r = it.center_radius()
                    shapes.append({
                        "type": "circle", "cx": cx, "cy": cy, "r": r,
                        "pen": encode_pen(it.pen())
                    })
                    continue
            except Exception:
                pass
            try:
                from app.core.shapes.line_item import LineItem
                if isinstance(it, LineItem):
                    ln = it.line()
                    shapes.append({
                        "type": "line", "x1": ln.x1(), "y1": ln.y1(), "x2": ln.x2(), "y2": ln.y2(),
                        "pen": encode_pen(it.pen())
                    })
                    continue
            except Exception:
                pass
            try:
                from app.core.shapes.rect_item import RectItem
                if isinstance(it, RectItem):
                    r = it.rect()
                    shapes.append({
                        "type": "rect", "x": r.x(), "y": r.y(), "width": r.width(), "height": r.height(),
                        "pen": encode_pen(it.pen())
                    })
                    continue
            except Exception:
                pass
            try:
                from app.core.shapes.polygon_item import PolygonItem
                if isinstance(it, PolygonItem):
                    poly = it.polygon()
                    pts = [[p.x(), p.y()] for p in poly]
                    shapes.append({"type": "polygon", "points": pts, "pen": encode_pen(it.pen())})
                    continue
            except Exception:
                pass
            try:
                from app.core.shapes.point_item import PointItem
                if isinstance(it, PointItem):
                    rect = it.rect(); pos = it.pos(); r = rect.width() / 2.0
                    shapes.append({"type": "point", "x": pos.x(), "y": pos.y(), "r": r, "pen": encode_pen(it.pen())})
                    continue
            except Exception:
                pass

            # 兜底：识别 Qt 内建类型，尽量导出
            if isinstance(it, QGraphicsEllipseItem) and it.rect().width() == it.rect().height():
                # 近似当作 circle
                rct = it.rect(); pos = it.pos(); r = rct.width() / 2.0
                shapes.append({"type": "circle", "cx": pos.x(), "cy": pos.y(), "r": r, "pen": encode_pen(it.pen())})
            elif isinstance(it, QGraphicsRectItem):
                r = it.rect(); shapes.append({"type": "rect", "x": r.x(), "y": r.y(), "width": r.width(), "height": r.height(), "pen": encode_pen(it.pen())})
            elif isinstance(it, QGraphicsLineItem):
                ln = it.line(); shapes.append({"type": "line", "x1": ln.x1(), "y1": ln.y1(), "x2": ln.x2(), "y2": ln.y2(), "pen": encode_pen(it.pen())})
            elif isinstance(it, QGraphicsPolygonItem):
                poly = it.polygon(); pts = [[p.x(), p.y()] for p in poly]
                shapes.append({"type": "polygon", "points": pts, "pen": encode_pen(it.pen())})
            elif isinstance(it, QGraphicsPathItem):
                # 导出为 brush_path 的普通路径
                try:
                    from app.core.shapes.brush_path_item import BrushPathItem  # type: ignore
                    if isinstance(it, BrushPathItem):
                        data = it.to_dict()
                    else:
                        # 基础导出：采样路径点
                        path = it.path(); pts = []
                        for i in range(path.elementCount()):
                            e = path.elementAt(i)
                            pts.append([float(e.x), float(e.y)])
                        data = {"type": "brush_path", "points": pts, "brush_type": "pen", "smoothing": True}
                    data["pen"] = encode_pen(it.pen());
                    shapes.append(data)
                except Exception:
                    pass
            else:
                # 最后兜底：导出为 unknown，带 boundingRect
                try:
                    br = it.boundingRect(); pos = it.pos()
                    shapes.append({
                        "type": "unknown",
                        "pos": {"x": pos.x(), "y": pos.y()},
                        "bounds": {"x": br.x(), "y": br.y(), "w": br.width(), "h": br.height()},
                        "pen": encode_pen(it.pen()) if hasattr(it, 'pen') else {"color": "#FF000000", "width": 1, "style": 1}
                    })
                except Exception:
                    pass
        except Exception:
            continue

    # 调试信息：如果 shapes 为空，记录场景中的对象信息
    if not shapes:
        logger.warning(f"场景中有 {len(items)} 个对象，但没有可序列化的图形")
        for i, it in enumerate(items):
            try:
                logger.debug(f"  [{i}] {type(it).__name__} - {it.__class__.__module__}")
            except Exception as e:
                logger.debug(f"  [{i}] 无法获取类型信息: {e}")
    return {
        "version": "1.0",
        "canvas": {"width": 0, "height": 0},
        "shapes": shapes,
    }


def load(data: Dict[str, Any], scene: QGraphicsScene) -> List[QGraphicsItem]:
    created: List[QGraphicsItem] = []
    items = data.get("shapes", []) or []
    
    # 临时阻止场景发出信号，避免加载过程中触发属性面板刷新
    logger.debug("阻止场景信号")
    scene.blockSignals(True)
    
    for obj in items:
        try:
            tp = str(obj.get("type"))
            if tp == "brush_path":
                from app.core.shapes.brush_path_item import BrushPathItem
                item = BrushPathItem.from_dict(obj)
                scene.addItem(item)
                # brush_path 的 from_dict 已经处理了 pen，不需要再次调用 apply_pen
                # if "pen" in obj:
                #     apply_pen(item, obj["pen"])  # type: ignore[arg-type]
                created.append(item)
            elif tp == "circle":
                from app.core.shapes.circle_item import CircleItem
                item = CircleItem.from_dict(obj)
                scene.addItem(item)
                if "pen" in obj:
                    apply_pen(item, obj["pen"])  # type: ignore[arg-type]
                created.append(item)
            elif tp == "line":
                from app.core.shapes.line_item import LineItem
                item = LineItem.from_dict(obj)
                scene.addItem(item)
                if "pen" in obj:
                    apply_pen(item, obj["pen"])  # type: ignore[arg-type]
                created.append(item)
            elif tp == "rect":
                from app.core.shapes.rect_item import RectItem
                item = RectItem.from_dict(obj)
                scene.addItem(item)
                if "pen" in obj:
                    apply_pen(item, obj["pen"])  # type: ignore[arg-type]
                created.append(item)
            elif tp == "polygon":
                from app.core.shapes.polygon_item import PolygonItem
                item = PolygonItem.from_dict(obj)
                scene.addItem(item)
                if "pen" in obj:
                    apply_pen(item, obj["pen"])  # type: ignore[arg-type]
                created.append(item)
            elif tp == "point":
                from app.core.shapes.point_item import PointItem
                item = PointItem.from_dict(obj)
                scene.addItem(item)
                if "pen" in obj:
                    apply_pen(item, obj["pen"])  # type: ignore[arg-type]
                created.append(item)
        except Exception:
            continue
    
    # 为所有加载的项目设置基础样式
    for item in created:
        if hasattr(scene, 'update_base_style'):
            scene.update_base_style(item)
    
    # 恢复场景信号
    logger.debug("恢复场景信号")
    scene.blockSignals(False)
    
    # 加载后立即取消所有选中状态，避免高亮效果
    for item in created:
        item.setSelected(False)
    
    return created


