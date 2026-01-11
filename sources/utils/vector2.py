from __future__ import annotations
import math

class Vector2:
    """ゲーム開発用の2Dベクトルクラス。"""

    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    # --- 算術演算 ---

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        """スカラー倍。"""
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2:
        """逆方向のスカラー倍（scalar * vector）。"""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vector2:
        """スカラー除算。"""
        if scalar == 0:
             raise ZeroDivisionError("Vector2をゼロで割ることはできません。")
        return Vector2(self.x / scalar, self.y / scalar)

    # --- 比較と表現 ---

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return NotImplemented
        return math.isclose(self.x, other.x, rel_tol=1e-9) and math.isclose(self.y, other.y, rel_tol=1e-9)

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    # --- ベクトル演算 ---

    def magnitude(self) -> float:
        """ベクトルの長さ（大きさ）を返す。"""
        return math.hypot(self.x, self.y)

    def dot(self, other: Vector2) -> float:
        """内積を返す。"""
        return (self.x * other.x) + (self.y * other.y)

    def cross(self, other: Vector2) -> float:
        """外積（2Dでは行列式の値）を返す。"""
        return (self.x * other.y) - (self.y * other.x)

    def normalized(self) -> Vector2:
        """同じ方向の単位ベクトルを返す。"""
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def proj(self, other: Vector2) -> Vector2:
        """このベクトルを別のベクトルに射影した結果を返す。"""
        n = other.normalized()
        length = self.dot(n)
        return n * length

    def perp(self, other: Vector2) -> Vector2:
        """このベクトルの、別のベクトルに垂直な成分を返す。"""
        return self - self.proj(other)

    def rotate(self, degrees: float) -> Vector2:
        """ベクトルを度単位で回転させ、新しいVector2を返す。"""
        rad = math.radians(degrees)
        cos = math.cos(rad)
        sin = math.sin(rad)
        new_x = self.x * cos - self.y * sin
        new_y = self.x * sin + self.y * cos
        return Vector2(new_x, new_y)

    def scale(self, sx: float, sy: float) -> Vector2:
        """ベクトルをsx, syで非一様にスケールし、新しいVector2を返す。"""
        return Vector2(self.x * sx, self.y * sy)