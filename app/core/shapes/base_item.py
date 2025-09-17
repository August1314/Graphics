from __future__ import annotations

from abc import ABC, abstractmethod
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem


class BaseShapeItem(ABC):
    """图形图元基类接口"""
    
    @abstractmethod
    def get_center(self) -> QPointF:
        """获取图元中心点"""
        pass
    
    @abstractmethod
    def set_center(self, center: QPointF) -> None:
        """设置图元中心点"""
        pass
    
    @abstractmethod
    def get_bounds(self) -> tuple[float, float, float, float]:
        """获取边界 (x, y, width, height)"""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """序列化为字典"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'BaseShapeItem':
        """从字典反序列化"""
        pass
