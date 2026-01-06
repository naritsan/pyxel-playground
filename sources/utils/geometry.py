from __future__ import annotations
import pyxel
import math
from .vector2 import Vector2
from .shape import Shape
from . import polygon # Local module import to handle circular dependency safely

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .polygon import Polygon

class Circle(Shape):
    """Represents a circle defined by a center position and a radius."""
    
    def __init__(self, x: float, y: float, radius: float):
        self.center = Vector2(x, y)
        self.radius = radius

    def intersects(self, other: Shape) -> bool:
        if isinstance(other, Circle):
            return self._intersects_circle(other)
        elif isinstance(other, Capsule):
            return self._intersects_capsule(other)
        elif isinstance(other, polygon.Polygon):
            # Delegate to Polygon's logic (inverted)
            return other.intersects(self)
        return False

    def _intersects_circle(self, other: Circle) -> bool:
        """Checks if this circle intersects with another circle."""
        dist_sq = (self.center.x - other.center.x)**2 + (self.center.y - other.center.y)**2
        radius_sum = self.radius + other.radius
        return dist_sq <= radius_sum**2

    def _intersects_capsule(self, other: Capsule) -> bool:
        """Checks if this circle intersects with a capsule."""
        # Check distance from circle center to capsule line segment
        return other.contains_point(self.center, self.radius)

    def contains_point(self, point: Vector2) -> bool:
        """Checks if a point is inside the circle."""
        dist_sq = (self.center.x - point.x)**2 + (self.center.y - point.y)**2
        return dist_sq <= self.radius**2

    def draw(self, col: int, fill: bool = False):
        """Draws the circle."""
        if fill:
            pyxel.circ(self.center.x, self.center.y, self.radius, col)
        else:
            pyxel.circb(self.center.x, self.center.y, self.radius, col)


class Capsule(Shape):
    """Represents a capsule shape defined by a line segment (start to end) and a radius."""

    def __init__(self, start: Vector2, end: Vector2, radius: float):
        self.start = start
        self.end = end
        self.radius = radius

    def intersects(self, other: Shape) -> bool:
        if isinstance(other, Circle):
            return self._intersects_circle(other)
        elif isinstance(other, Capsule):
            return self._intersects_capsule(other)
        elif isinstance(other, polygon.Polygon):
            return other.intersects(self)
        return False

    def _intersects_circle(self, other: Circle) -> bool:
        return self.contains_point(other.center, other.radius)

    def _intersects_capsule(self, other: Capsule) -> bool:
        # Simplified approximate intersection
        if self.contains_point(other.start, other.radius) or self.contains_point(other.end, other.radius):
            return True
        if other.contains_point(self.start, self.radius) or other.contains_point(self.end, self.radius):
            return True
        return False

    def get_direction(self) -> Vector2:
        """Returns the vector from start to end."""
        return self.end - self.start

    def length(self) -> float:
        """Returns the length of the central line segment."""
        return self.get_direction().magnitude()
    
    def contains_point(self, point: Vector2, expansion: float = 0.0) -> bool:
        """Checks if a point is inside the capsule (or expanded area)."""
        ab = self.end - self.start
        if ab.x == 0 and ab.y == 0:
            closest_point = self.start
        else:
            ap = point - self.start
            t = ap.dot(ab) / ab.dot(ab)
            t = max(0.0, min(1.0, float(t)))
            closest_point = self.start + ab * t
        
        dist_sq = (point.x - closest_point.x)**2 + (point.y - closest_point.y)**2
        return dist_sq <= (self.radius + expansion)**2

    def draw(self, col: int, fill: bool = True):
        """Draws the capsule."""
        if fill:
            pyxel.circ(self.start.x, self.start.y, self.radius, col)
            pyxel.circ(self.end.x, self.end.y, self.radius, col)
            
            perp = (self.end - self.start).normalized().rotate(90) * self.radius
            p1, p2 = self.start + perp, self.end + perp
            p3, p4 = self.end - perp, self.start - perp
            
            pyxel.tri(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, col)
            pyxel.tri(p1.x, p1.y, p3.x, p3.y, p4.x, p4.y, col)
        else:
            pyxel.circb(self.start.x, self.start.y, self.radius, col)
            pyxel.circb(self.end.x, self.end.y, self.radius, col)
            
            perp = (self.end - self.start).normalized().rotate(90) * self.radius
            p1, p2 = self.start + perp, self.end + perp
            p3, p4 = self.end - perp, self.start - perp
            
            pyxel.line(p1.x, p1.y, p2.x, p2.y, col)
            pyxel.line(p3.x, p3.y, p4.x, p4.y, col)
