from __future__ import annotations

from typing import List


class PropertyRegistry:
    """简单注册表：按图形类型返回属性键集合。
    后续可扩展为返回真正的组件实例列表。
    """

    @staticmethod
    def keys_for_shape(shape: str) -> List[str]:
        if shape in ("circle", "point"):
            return [
                "center", "radius", "strokeColor", "strokeWidth", "dash", "fillColor", "opacity",
            ]
        if shape == "line":
            return [
                "lineP1", "lineP2", "strokeColor", "strokeWidth", "dash", "opacity",
            ]
        if shape == "rect":
            return [
                "rectGeom", "strokeColor", "strokeWidth", "dash", "fillColor", "opacity",
            ]
        if shape == "polygon":
            return [
                "strokeColor", "strokeWidth", "dash", "fillColor", "opacity",
            ]
        if shape == "brush_path":
            return [
                "brushType", "strokeColor", "strokeWidth", "dash", "opacity"
            ]
        if shape == "eraser":
            return [
                "eraserMode", "eraserSize", "previewColor", "previewOpacity", 
                "smoothing", "minDistance"
            ]
        return []


