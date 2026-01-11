from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from .vector2 import Vector2

class Shape(ABC):
    """
    すべての幾何図形の抽象基底クラス。
    衝突判定の実装を強制する。
    """

    @abstractmethod
    def intersects(self, other: "Shape") -> bool:
        """
        この図形が他の図形と交差しているか判定。
        すべてのサブクラスで実装必須。
        """
        pass

    @abstractmethod
    def draw(self, col: int, fill: bool = False):
        """
        図形を描画。
        すべてのサブクラスで実装必須。
        """
        pass

    @abstractmethod
    def rotate(self, angle: float):
        """
        図形を指定した角度（度単位）で回転。
        すべてのサブクラスで実装必須。
        """
        pass

    @abstractmethod
    def set_scale(self, sx: float, sy: float):
        """
        図形のスケールを設定。
        すべてのサブクラスで実装必須。
        """
        pass

    @abstractmethod
    def translate(self, dx: float, dy: float):
        """
        図形を移動。
        すべてのサブクラスで実装必須。
        """
        pass
