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
        
        # Capsule animation state
        self.capsule_center = Vector2(130, 30)
        self.capsule_vector = Vector2(0, 5) # Dist from center to end
        self.capsule_angle = 0
        self.capsule_base_radius = 6
        
        # Circle base state
        self.circle_base_radius = 8
        
        pyxel.run(self.update, self.draw)

    def update(self):
        # Calculate scale factor for pulsing
        # Cycle speed: 0.1, Amplitude: 0.3 (0.7 to 1.3)
        import math
        s = 1.0 + math.sin(pyxel.frame_count * 0.1) * 0.3
        
        # Rotate and Scale all polygons
        for poly in self.polygons:
            poly.rotate(2) # 2 degrees per frame (Cumulative)
            poly.set_scale(s, s) # Absolute scale

        # Circle scaling
        self.circle.radius = self.circle_base_radius * s

        # Capsule rotation and scaling
        self.capsule_angle += 2
        
        # Calculate new capsule vector with rotation and scale
        # Start/End are offset from center
        vec = self.capsule_vector.rotate(self.capsule_angle) * s
        
        self.capsule.start = self.capsule_center - vec
        self.capsule.end = self.capsule_center + vec
        self.capsule.radius = self.capsule_base_radius * s

    def draw(self):
        pyxel.cls(0)
        
        # Labels
        pyxel.text(5, 5, "Shape Demo", 7)
        
        # Draw Shapes
        # Outline only (fill=False)
        self.rect.draw(8, fill=False)      # Red
        self.triangle.draw(9, fill=False)  # Orange
        self.circle.draw(10, fill=False)   # Yellow
        self.capsule.draw(11, fill=False)  # Green
        
        self.star.draw(12, fill=False)     # Blue
        self.heart.draw(8, fill=False)     # Red
        self.arrow.draw(14, fill=False)    # Pink

if __name__ == "__main__":
    App()
