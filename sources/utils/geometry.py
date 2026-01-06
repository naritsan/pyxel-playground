from __future__ import annotations
import pyxel
import math
from .vector2 import Vector2

class Circle:
    """Represents a circle defined by a center position and a radius."""
    
    def __init__(self, x: float, y: float, radius: float):
        self.center = Vector2(x, y)
        self.radius = radius

    def intersects_circle(self, other: Circle) -> bool:
        """Checks if this circle intersects with another circle."""
        dist_sq = (self.center.x - other.center.x)**2 + (self.center.y - other.center.y)**2
        radius_sum = self.radius + other.radius
        return dist_sq <= radius_sum**2

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


class Capsule:
    """Represents a capsule shape defined by a line segment (start to end) and a radius."""

    def __init__(self, start: Vector2, end: Vector2, radius: float):
        self.start = start
        self.end = end
        self.radius = radius

    def get_direction(self) -> Vector2:
        """Returns the vector from start to end."""
        return self.end - self.start

    def length(self) -> float:
        """Returns the length of the central line segment."""
        return self.get_direction().magnitude()
    
    def contains_point(self, point: Vector2) -> bool:
        """Checks if a point is inside the capsule."""
        # Find the closest point on the line segment
        ab = self.end - self.start
        ap = point - self.start
        
        t = ap.dot(ab) / ab.dot(ab)
        # Clamp t to the segment [0, 1]
        t = max(0.0, min(1.0, float(t)))
        
        closest_point = self.start + ab * t
        
        # Check distance from the closest point
        dist_sq = (point.x - closest_point.x)**2 + (point.y - closest_point.y)**2
        return dist_sq <= self.radius**2

    def draw(self, col: int, fill: bool = True):
        """Draws the capsule.
        
        Args:
            col: Color index.
            fill: If True, draws a filled capsule. If False, draws a wireframe (internal lines may be visible).
        """
        if fill:
            # Draw circles at both ends
            pyxel.circ(self.start.x, self.start.y, self.radius, col)
            pyxel.circ(self.end.x, self.end.y, self.radius, col)
            
            # Draw the rectangle connecting them
            perp = (self.end - self.start).normalized().rotate(90) * self.radius
            
            p1 = self.start + perp
            p2 = self.end + perp
            p3 = self.end - perp
            p4 = self.start - perp
            
            # Draw the body using triangles
            pyxel.tri(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, col)
            pyxel.tri(p1.x, p1.y, p3.x, p3.y, p4.x, p4.y, col)
        else:
            # Draw outline (wireframe style)
            # Ends
            pyxel.circb(self.start.x, self.start.y, self.radius, col)
            pyxel.circb(self.end.x, self.end.y, self.radius, col)
            
            # Sides
            perp = (self.end - self.start).normalized().rotate(90) * self.radius
            p1 = self.start + perp
            p2 = self.end + perp
            p3 = self.end - perp
            p4 = self.start - perp
            
            pyxel.line(p1.x, p1.y, p2.x, p2.y, col)
            pyxel.line(p3.x, p3.y, p4.x, p4.y, col)
