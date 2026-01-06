from __future__ import annotations
import pyxel
import math
from .vector2 import Vector2

class Polygon:
    """
    A class to represent a 2D polygon with multiple vertices.
    Manages local vertices and applies transformations (scale, rotation, translation)
    to calculate world coordinates.
    """

    def __init__(self, vertices: list[Vector2], x: float = 0, y: float = 0):
        # Local coordinates (relative to the center/origin of the shape)
        self.local_vertices: list[Vector2] = vertices
        
        # World state
        self.position: Vector2 = Vector2(x, y)
        self.rotation: float = 0.0  # Degrees
        self.scale: Vector2 = Vector2(1.0, 1.0)
        
        # Cache for transformed vertices (optimization, optional but good practice)
        # self._cache_valid = False
        # self._transformed_vertices = []

    def get_transformed_vertices(self) -> list[Vector2]:
        """
        Returns a list of vertices transformed by the current scale, rotation, and position.
        Order of operations: Scale -> Rotate -> Translate
        """
        # Pre-calculate rotation trigonometry
        rad = math.radians(self.rotation)
        cos_theta = math.cos(rad)
        sin_theta = math.sin(rad)

        world_vertices = []

        for v in self.local_vertices:
            # 1. Scale
            sx = v.x * self.scale.x
            sy = v.y * self.scale.y

            # 2. Rotate
            # x' = x*cos - y*sin
            # y' = x*sin + y*cos
            rx = sx * cos_theta - sy * sin_theta
            ry = sx * sin_theta + sy * cos_theta

            # 3. Translate (Add position)
            wx = rx + self.position.x
            wy = ry + self.position.y

            world_vertices.append(Vector2(wx, wy))

        return world_vertices

    def translate(self, dx: float, dy: float):
        """Moves the polygon properly."""
        self.position += Vector2(dx, dy)

    def rotate(self, angle: float):
        """Rotates the polygon by the specified angle (in degrees)."""
        self.rotation += angle

    def set_scale(self, sx: float, sy: float):
        """Sets the scale of the polygon."""
        self.scale = Vector2(sx, sy)

    @classmethod
    def create_rect(cls, width: float, height: float, x: float = 0, y: float = 0) -> Polygon:
        """
        Creates a rectangle centered at (x, y).
        """
        hw = width / 2
        hh = height / 2
        # Define vertices relative to center (0,0)
        vertices = [
            Vector2(-hw, -hh),  # Top-Left
            Vector2(hw, -hh),   # Top-Right
            Vector2(hw, hh),    # Bottom-Right
            Vector2(-hw, hh)    # Bottom-Left
        ]
        return cls(vertices, x, y)

    @classmethod
    def create_regular_polygon(cls, sides: int, radius: float, x: float = 0, y: float = 0, angle_offset: float = -90) -> Polygon:
        """
        Creates a regular polygon (triangle, pentagon, hexagon, etc.).
        sides: Number of vertices (e.g., 3 for triangle).
        radius: Distance from center to each vertex.
        angle_offset: Rotation offset in degrees (default -90 puts the first vertex at the top).
        """
        if sides < 3:
            raise ValueError("Polygon must have at least 3 sides.")

        vertices = []
        angle_step = 360 / sides

        for i in range(sides):
            deg = angle_offset + i * angle_step
            rad = math.radians(deg)
            vx = radius * math.cos(rad)
            vy = radius * math.sin(rad)
            vertices.append(Vector2(vx, vy))

        return cls(vertices, x, y)

    @classmethod
    def create_star(cls, points: int, outer_radius: float, inner_radius: float, x: float = 0, y: float = 0) -> Polygon:
        """
        Creates a star shape.
        points: Number of points on the star.
        outer_radius: Radius of the outer points.
        inner_radius: Radius of the inner indentations.
        """
        vertices = []
        angle_step = 180 / points
        angle_offset = -90

        for i in range(points * 2):
            deg = angle_offset + i * angle_step
            rad = math.radians(deg)
            # Alternate between outer and inner radius
            radius = outer_radius if i % 2 == 0 else inner_radius
            vx = radius * math.cos(rad)
            vy = radius * math.sin(rad)
            vertices.append(Vector2(vx, vy))

        return cls(vertices, x, y)

    @classmethod
    def create_heart(cls, scale: float = 1.0, x: float = 0, y: float = 0) -> Polygon:
        """
        Creates a heart shape using an approximate polygon.
        scale: Size multiplier.
        """
        # Data points for a heart shape
        raw_points = [
            (0, -0.5), (0.2, -0.7), (0.5, -0.8), (0.8, -0.6),
            (0.9, -0.3), (0.8, 0.1), (0.5, 0.5), (0, 0.9),
            (-0.5, 0.5), (-0.8, 0.1), (-0.9, -0.3), (-0.8, -0.6),
            (-0.5, -0.8), (-0.2, -0.7)
        ]
        # Invert Y because game coordinates usually have Y down, but let's keep it standard math for now
        # Actually in Pyxel Y is down.
        # Let's adjust to make sure it looks upright.
        # Standard heart param eq or manual points. Manual is safer for low poly.
        
        # Optimized low-poly heart
        vertices = [
            Vector2(0, -0.25), Vector2(0.3, -0.6), Vector2(0.7, -0.6),
            Vector2(0.9, -0.3), Vector2(0.9, 0.1), Vector2(0, 0.8),
            Vector2(-0.9, 0.1), Vector2(-0.9, -0.3), Vector2(-0.7, -0.6),
           Vector2(-0.3, -0.6)
        ]
        
        # Apply scale
        vertices = [v * scale * 10 for v in vertices] # Base size approx 10
        return cls(vertices, x, y)

    @classmethod
    def create_arrow(cls, length: float, head_size: float, shaft_width: float, x: float = 0, y: float = 0) -> Polygon:
        """
        Creates an arrow pointing up.
        length: Total length of the arrow.
        head_size: Width/Height of the arrow head.
        shaft_width: Width of the arrow shaft.
        """
        hw = head_size / 2
        sw = shaft_width / 2
        l = length / 2 # Half length for centering
        
        # Defined pointing UP (negative Y)
        vertices = [
            Vector2(0, -l - hw),       # Tip
            Vector2(hw, -l + hw),      # Head Right
            Vector2(sw, -l + hw),      # Shaft Right Top
            Vector2(sw, l),            # Shaft Right Bottom
            Vector2(-sw, l),           # Shaft Left Bottom
            Vector2(-sw, -l + hw),     # Shaft Left Top
            Vector2(-hw, -l + hw)      # Head Left
        ]
        return cls(vertices, x, y)

    def draw(self, col: int, fill: bool = False):
        """Draws the polygon.
        
        Args:
            col: Color index.
            fill: If True, draws a filled polygon (using triangle fan from center).
                  Note: Simple fan works for convex and star-shaped polygons. Complex concave ones may have artifacts.
        """
        verts = self.get_transformed_vertices()
        center = self.position # Approximate center for fan

        if fill:
            # Triangle fan from center (self.position)
            # This works well for the predefined shapes (Rect, Regular, Star, Heart, Arrow-ish)
            # providing the center is inside the kernel of the shape.
            for i in range(len(verts)):
                p1 = verts[i]
                p2 = verts[(i + 1) % len(verts)]
                pyxel.tri(center.x, center.y, p1.x, p1.y, p2.x, p2.y, col)
        else:
            for i in range(len(verts)):
                p1 = verts[i]
                p2 = verts[(i + 1) % len(verts)]
                pyxel.line(p1.x, p1.y, p2.x, p2.y, col)

