from __future__ import annotations
from abc import ABC, abstractmethod

class Shape(ABC):
    """
    Abstract base class for all geometric shapes.
    Enforces the implementation of collision detection.
    """

    @abstractmethod
    def intersects(self, other: "Shape") -> bool:
        """
        Checks if this shape intersects with another shape.
        This method must be implemented by all subclasses.
        """
        pass
