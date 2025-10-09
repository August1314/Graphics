from __future__ import annotations

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush
import os
from pathlib import Path
try:
    from PySide6.QtSvg import QSvgRenderer  # type: ignore
except Exception:
    QSvgRenderer = None  # type: ignore


class IconProvider:
    def __init__(self, theme: str = "light") -> None:
        self._theme = theme
        self._default_size = 20  # 统一图标尺寸
        # 浅色主题：深色图标；深色主题：浅色图标
        if theme == "dark":
            self._fg = QColor(240, 240, 240)
        else:
            self._fg = QColor("#0f172a")  # 使用设计系统的TEXT_PRIMARY颜色
        self._bg = Qt.GlobalColor.transparent
        self._icon_cache = {}  # 图标缓存
        self._base_dir = Path(__file__).resolve().parent.parent / "resources" / "icons"
        self._name_map = {
            "select": "select.svg",
            "point": "point.svg",
            "line": "line.svg",
            "rect": "rect.svg",
            "circle": "circle.svg",
            "polygon": "polygon.svg",
            # 画笔系列
            "brush": "brush.svg",
            "brush_pen": "brush_pen.svg",
            "brush_marker": "brush_marker.svg",
            "brush_calligraphy": "brush_calligraphy.svg",
            "brush_spray": "brush_spray.svg",
            # 其他
            "eraser": "eraser.svg",
        }

    def set_theme(self, theme: str) -> None:
        self.__init__(theme)

    def get(self, name: str, size: int = 0) -> QIcon:
        # 使用默认尺寸（20px）如果未指定
        if size == 0:
            size = self._default_size
        
        # 检查缓存
        cache_key = f"{name}_{size}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # 1) 尝试本地 SVG 资源
        # 允许为不同 brush 变体提供独立图标，不再强制折叠为 brush
        fname = self._name_map.get(name)
        if fname:
            theme_dir = self._base_dir / ("dark" if self._theme == "dark" else "light")
            svg_path = theme_dir / fname
            if svg_path.exists():
                ic = self._load_svg_icon(svg_path, size)
                if not ic.isNull():
                    self._icon_cache[cache_key] = ic
                    return ic
        # 2) 兜底：绘制型图标
        icon = self._draw_fallback(name, size)
        self._icon_cache[cache_key] = icon
        return icon

    # ---- helpers ----
    def _load_svg_icon(self, svg_path: Path, size: int) -> QIcon:
        try:
            if QSvgRenderer is None:
                return QIcon(str(svg_path))
            pm = QPixmap(size, size)
            pm.fill(Qt.GlobalColor.transparent)
            renderer = QSvgRenderer(str(svg_path))
            p = QPainter(pm)
            p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
            renderer.render(p)
            p.end()
            # 着色为主题前景色
            tinted = QPixmap(size, size)
            tinted.fill(Qt.GlobalColor.transparent)
            p2 = QPainter(tinted)
            p2.setCompositionMode(QPainter.CompositionMode_Source)
            p2.drawPixmap(0, 0, pm)
            p2.setCompositionMode(QPainter.CompositionMode_SourceIn)
            p2.fillRect(0, 0, size, size, self._fg)
            p2.end()
            return QIcon(tinted)
        except Exception:
            return QIcon()

    def _draw_fallback(self, name: str, size: int) -> QIcon:
        pm = QPixmap(size, size)
        pm.fill(self._bg)
        p = QPainter(pm)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        pen = QPen(self._fg)
        pen.setWidthF(2.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        r = QRectF(3, 3, size - 6, size - 6)
        try:
            if name == "select":
                p.drawLine(QPointF(r.left(), r.top()), QPointF(r.center().x() - 1, r.center().y()))
                p.drawLine(QPointF(r.left() + 2, r.top()), QPointF(r.left() + 2, r.bottom() - 2))
                p.drawLine(QPointF(r.left() + 2, r.bottom() - 2), QPointF(r.center().x() + 2, r.center().y()))
            elif name == "point":
                p.setBrush(QBrush(self._fg))
                p.drawEllipse(r.center(), 2.8, 2.8)
            elif name == "line":
                p.drawLine(r.topLeft(), r.bottomRight())
            elif name == "rect":
                p.drawRoundedRect(r, 3, 3)
            elif name == "circle":
                p.drawEllipse(r)
            elif name == "polygon":
                pts = []
                import math
                for i in range(6):
                    angle = (60 * i - 30) * math.pi / 180.0
                    cx, cy = r.center().x(), r.center().y()
                    rx, ry = r.width() / 2.2, r.height() / 2.2
                    pts.append(QPointF(cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
                for i in range(6):
                    p.drawLine(pts[i], pts[(i + 1) % 6])
            elif name.startswith("brush"):
                p.drawLine(QPointF(r.left(), r.bottom()-2), QPointF(r.right(), r.top()+2))
                head = QRectF(r.right()-8, r.top()+2, 6, 6)
                p.setBrush(QBrush(self._fg))
                p.drawEllipse(head)
            elif name == "eraser":
                p.save()
                p.translate(r.center())
                p.rotate(-25)
                rr = QRectF(-6, -4, 12, 8)
                p.drawRoundedRect(rr, 2, 2)
                p.restore()
                p.drawLine(QPointF(r.left()+2, r.bottom()-2), QPointF(r.right()-2, r.bottom()-2))
            else:
                p.drawEllipse(r)
        finally:
            p.end()
        return QIcon(pm)


