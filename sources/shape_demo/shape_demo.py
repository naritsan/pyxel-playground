import pyxel

# Removed manual path manipulation in favor of running from root script

from sources.utils.vector2 import Vector2
from sources.utils.polygon import Polygon
from sources.utils.geometry import Circle, Capsule

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Shape Demo")

        # Grid Layout Settings
        # Cols: 4, Rows: 2
        # Cell size: 40x60
        
        # Row 1 (Y=30)
        self.rect = Polygon.create_rect(20, 15, x=20, y=30)
        self.triangle = Polygon.create_regular_polygon(3, 10, x=60, y=30)
        self.circle = Circle(100, 30, 8)
        self.capsule = Capsule(Vector2(130, 30-5), Vector2(130, 30+5), 6) # Vertical capsule
        
        # Row 2 (Y=90)
        self.star = Polygon.create_star(5, 12, 5, x=20, y=90)
        self.heart = Polygon.create_heart(1.0, x=60, y=90)
        self.arrow = Polygon.create_arrow(20, 10, 4, x=100, y=90)
        # Placeholder for one more or just empty
        
        self.polygons = [self.rect, self.triangle, self.star, self.heart, self.arrow]
        
        pyxel.run(self.update, self.draw)

    def update(self):
        # Rotate all polygons
        for poly in self.polygons:
            poly.rotate(2) # 2 degrees per frame

        # Capsule rotation (manual update of start/end)
        # Rotate capsule around its center (130, 30)
        cx, cy = 130, 30
        self.capsule.start = (self.capsule.start - Vector2(cx, cy)).rotate(2) + Vector2(cx, cy)
        self.capsule.end = (self.capsule.end - Vector2(cx, cy)).rotate(2) + Vector2(cx, cy)

    def draw(self):
        pyxel.cls(0)
        
        # Labels
        pyxel.text(5, 5, "Shape Demo", 7)
        
        # Draw Shapes
        self.rect.draw(8)      # Red
        self.triangle.draw(9)  # Orange
        self.circle.draw(10, fill=False)   # Yellow (Outline)
        self.capsule.draw(11)  # Green
        
        self.star.draw(12)     # Blue
        self.heart.draw(8)     # Red
        self.arrow.draw(14)    # Pink

if __name__ == "__main__":
    App()
