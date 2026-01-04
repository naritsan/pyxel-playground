from __future__ import annotations
import math

class Vector2:
    """A 2D vector class for game development."""

    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    # --- Arithmetic Operations ---

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        """Scalar multiplication."""
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2:
        """Reverse scalar multiplication (scalar * vector)."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vector2:
        """Scalar division."""
        if scalar == 0:
             raise ZeroDivisionError("Cannot divide Vector2 by zero.")
        return Vector2(self.x / scalar, self.y / scalar)

    # --- Comparison and Representation ---

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return NotImplemented
        return math.isclose(self.x, other.x, rel_tol=1e-9) and math.isclose(self.y, other.y, rel_tol=1e-9)

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    # --- Vector Operations ---

    def magnitude(self) -> float:
        """Returns the length (magnitude) of the vector."""
        return math.hypot(self.x, self.y)

    def dot(self, other: Vector2) -> float:
        """Returns the dot product."""
        return (self.x * other.x) + (self.y * other.y)

    def cross(self, other: Vector2) -> float:
        """Returns the cross product (determinant/wedge product value)."""
        return (self.x * other.y) - (self.y * other.x)

    def normalized(self) -> Vector2:
        """Returns a unit vector with the same direction."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def proj(self, other: Vector2) -> Vector2:
        """Projects this vector onto another vector."""
        n = other.normalized()
        length = self.dot(n)
        return n * length

    def perp(self, other: Vector2) -> Vector2:
        """Returns the component of this vector perpendicular to the other vector."""
        return self - self.proj(other)

    def rotate(self, degrees: float) -> Vector2:
        """Rotates the vector by a given angle in degrees. Returns a new Vector2."""
        rad = math.radians(degrees)
        cos = math.cos(rad)
        sin = math.sin(rad)
        new_x = self.x * cos - self.y * sin
        new_y = self.x * sin + self.y * cos
        return Vector2(new_x, new_y)

    def scale(self, sx: float, sy: float) -> Vector2:
        """Scales the vector non-uniformly by sx and sy. Returns a new Vector2."""
        return Vector2(self.x * sx, self.y * sy)