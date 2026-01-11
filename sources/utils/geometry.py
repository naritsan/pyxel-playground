from __future__ import annotations
import pyxel
import math
from .vector2 import Vector2
from .shape import Shape
from . import polygon  # Local module import to handle circular dependency safely

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .polygon import Polygon


class Circle(Shape):
    """円を表すクラス。中心座標と半径で定義される。"""
    
    def __init__(self, x: float, y: float, radius: float):
        self.center = Vector2(x, y)
        self.radius = radius
        self._base_radius = radius

    def intersects(self, other: Shape) -> bool:
        if isinstance(other, Circle):
            return self._intersects_circle(other)
        elif isinstance(other, Capsule):
            return self._intersects_capsule(other)
        elif isinstance(other, Line):
            return other.intersects(self)  # Delegate to Line
        elif isinstance(other, polygon.Polygon):
            return other.intersects(self)
        return False

    def _intersects_circle(self, other: Circle) -> bool:
        """円同士の交差判定。"""
        dist_sq = (self.center.x - other.center.x)**2 + (self.center.y - other.center.y)**2
        radius_sum = self.radius + other.radius
        return dist_sq <= radius_sum**2

    def _intersects_capsule(self, other: Capsule) -> bool:
        """円とカプセルの交差判定。"""
        return other.contains_point(self.center, self.radius)

    def contains_point(self, point: Vector2) -> bool:
        """点が円の内部にあるか判定。"""
        dist_sq = (self.center.x - point.x)**2 + (self.center.y - point.y)**2
        return dist_sq <= self.radius**2

    def set_scale(self, sx: float, sy: float):
        """スケールを設定（半径に影響）。"""
        self.radius = self._base_radius * ((abs(sx) + abs(sy)) / 2)

    def rotate(self, angle: float):
        """回転（円には視覚的効果なし）。"""
        pass

    def translate(self, dx: float, dy: float):
        """円を移動。"""
        self.center.x += dx
        self.center.y += dy

    def draw(self, col: int, fill: bool = False):
        """円を描画。"""
        if fill:
            pyxel.circ(self.center.x, self.center.y, self.radius, col)
        else:
            pyxel.circb(self.center.x, self.center.y, self.radius, col)


class Line(Shape):
    """線分を表すクラス。始点と終点で定義される（半径なし）。"""

    def __init__(self, start: Vector2, end: Vector2):
        self.start = start
        self.end = end

    def intersects(self, other: Shape) -> bool:
        if isinstance(other, Circle):
            return self._intersects_circle(other)
        elif isinstance(other, Line):
            return self._intersects_line(other)
        elif isinstance(other, Capsule):
            # Capsule は Line を継承しているので、Capsule 側に委譲
            return other.intersects(self)
        return False

    def _intersects_circle(self, circle: Circle) -> bool:
        """円と線分の交差判定。"""
        closest = self.closest_point(circle.center)
        dist_sq = (circle.center.x - closest.x)**2 + (circle.center.y - closest.y)**2
        return dist_sq <= circle.radius**2

    def _intersects_line(self, other: Line) -> bool:
        """線分同士の交差判定。"""
        def ccw(a: Vector2, b: Vector2, c: Vector2) -> float:
            return (c.y - a.y) * (b.x - a.x) - (b.y - a.y) * (c.x - a.x)
        
        d1 = ccw(self.start, self.end, other.start)
        d2 = ccw(self.start, self.end, other.end)
        d3 = ccw(other.start, other.end, self.start)
        d4 = ccw(other.start, other.end, self.end)
        
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        return False

    def get_direction(self) -> Vector2:
        """線分の方向ベクトルを返す。"""
        return self.end - self.start

    def get_normal(self) -> Vector2:
        """線分の法線ベクトル（左側）を返す。"""
        d = self.get_direction().normalized()
        return Vector2(-d.y, d.x)

    def length(self) -> float:
        """線分の長さを返す。"""
        return self.get_direction().magnitude()

    def closest_point(self, point: Vector2) -> Vector2:
        """点から線分への最近点を返す。"""
        ab = self.end - self.start
        if ab.x == 0 and ab.y == 0:
            return self.start
        ap = point - self.start
        t = ap.dot(ab) / ab.dot(ab)
        t = max(0.0, min(1.0, float(t)))
        return self.start + ab * t

    def rotate(self, angle: float):
        """線分を中心周りに回転。"""
        center = (self.start + self.end) * 0.5
        self.start = (self.start - center).rotate(angle) + center
        self.end = (self.end - center).rotate(angle) + center

    def set_scale(self, sx: float, sy: float):
        """スケール（線分には効果なし）。"""
        pass

    def translate(self, dx: float, dy: float):
        """線分を移動。"""
        self.start.x += dx
        self.start.y += dy
        self.end.x += dx
        self.end.y += dy

    def draw(self, col: int, fill: bool = False):
        """線分を描画。"""
        pyxel.line(self.start.x, self.start.y, self.end.x, self.end.y, col)


class Capsule(Line):
    """カプセルを表すクラス。線分（Line）+ 半径で定義される。"""

    def __init__(self, start: Vector2, end: Vector2, radius: float):
        super().__init__(start, end)
        self.radius = radius
        self._base_radius = radius

    def intersects(self, other: Shape) -> bool:
        if isinstance(other, Circle):
            return self._intersects_circle(other)
        elif isinstance(other, Capsule):
            return self._intersects_capsule(other)
        elif isinstance(other, Line):
            return self._intersects_line_with_radius(other)
        elif isinstance(other, polygon.Polygon):
            return other.intersects(self)
        return False

    def _intersects_circle(self, circle: Circle) -> bool:
        """円とカプセルの交差判定。"""
        return self.contains_point(circle.center, circle.radius)

    def _intersects_capsule(self, other: Capsule) -> bool:
        """カプセル同士の交差判定（簡易版）。"""
        if self.contains_point(other.start, other.radius) or self.contains_point(other.end, other.radius):
            return True
        if other.contains_point(self.start, self.radius) or other.contains_point(self.end, self.radius):
            return True
        return False

    def _intersects_line_with_radius(self, line: Line) -> bool:
        """線分とカプセルの交差判定。"""
        # 線分の両端点がカプセル内にあるかチェック
        if self.contains_point(line.start, 0) or self.contains_point(line.end, 0):
            return True
        # 線分同士の交差もチェック
        return super()._intersects_line(line)

    def contains_point(self, point: Vector2, expansion: float = 0.0) -> bool:
        """点がカプセル内（+拡張半径）にあるか判定。"""
        closest = self.closest_point(point)
        dist_sq = (point.x - closest.x)**2 + (point.y - closest.y)**2
        return dist_sq <= (self.radius + expansion)**2

    def set_scale(self, sx: float, sy: float):
        """スケールを設定（半径に影響）。"""
        self.radius = self._base_radius * ((abs(sx) + abs(sy)) / 2)

    def draw(self, col: int, fill: bool = True):
        """カプセルを描画。"""
        if fill:
            pyxel.circ(self.start.x, self.start.y, self.radius, col)
            pyxel.circ(self.end.x, self.end.y, self.radius, col)
            
            direction = self.get_direction()
            if direction.x != 0 or direction.y != 0:
                perp = direction.normalized().rotate(90) * self.radius
                p1 = self.start + perp
                p2 = self.end + perp
                p3 = self.end - perp
                p4 = self.start - perp
                
                pyxel.tri(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, col)
                pyxel.tri(p1.x, p1.y, p3.x, p3.y, p4.x, p4.y, col)
        else:
            pyxel.circb(self.start.x, self.start.y, self.radius, col)
            pyxel.circb(self.end.x, self.end.y, self.radius, col)
            
            direction = self.get_direction()
            if direction.x != 0 or direction.y != 0:
                perp = direction.normalized().rotate(90) * self.radius
                p1 = self.start + perp
                p2 = self.end + perp
                p3 = self.end - perp
                p4 = self.start - perp
                
                pyxel.line(p1.x, p1.y, p2.x, p2.y, col)
                pyxel.line(p3.x, p3.y, p4.x, p4.y, col)
