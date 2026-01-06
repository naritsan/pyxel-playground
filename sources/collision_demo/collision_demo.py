import pyxel
from sources.utils.vector2 import Vector2
from sources.utils.polygon import Polygon
import sources.utils.geometry as geo

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Collision Demo")
        
        # Player Polygon (Triangle)
        self.player = Polygon.create_regular_polygon(3, 8, x=80, y=60)
        self.player_color = 10 # Yellow
        
        # Static Obstacles
        self.obstacles = []
        self.obstacles.append(Polygon.create_rect(30, 20, x=40, y=40))
        self.obstacles.append(Polygon.create_regular_polygon(5, 12, x=120, y=30))
        self.obstacles.append(Polygon.create_star(5, 10, 5, x=100, y=90))
        self.obstacles.append(Polygon.create_rect(10, 60, x=20, y=80)) # Long wall
        
        # New Shapes (Circle, Capsule)
        self.obstacles.append(geo.Circle(140, 80, 10))
        self.obstacles.append(geo.Capsule(Vector2(50, 90), Vector2(70, 110), 5))

        # Rotation for fun
        self.obstacles[1].rotate(15)
        self.obstacles[3].rotate(45)

        pyxel.run(self.update, self.draw)

    def update(self):
        # Player Movement
        speed = 2.0
        dx, dy = 0, 0
        if pyxel.btn(pyxel.KEY_UP): dy -= 1
        if pyxel.btn(pyxel.KEY_DOWN): dy += 1
        if pyxel.btn(pyxel.KEY_LEFT): dx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT): dx += 1
        
        # Normalize vector to ensure consistent speed
        if dx != 0 or dy != 0:
            input_vec = Vector2(dx, dy).normalized()
            self.player.translate(input_vec.x * speed, input_vec.y * speed)
        
        # Player Rotation
        if pyxel.btn(pyxel.KEY_Z): self.player.rotate(-3)
        if pyxel.btn(pyxel.KEY_X): self.player.rotate(3)

        # Collision Check
        self.is_colliding = False
        self.hit_indices = []
        
        for i, obs in enumerate(self.obstacles):
            # Using unified intersects method
            if self.player.intersects(obs):
                self.is_colliding = True
                self.hit_indices.append(i)

    def draw(self):
        pyxel.cls(0)
        
        # Draw Obstacles
        for i, obs in enumerate(self.obstacles):
            # Change color if hit
            col = 8 if i in self.hit_indices else 12 # Red if hit, Blue otherwise
            # Draw call is polymorphic; all Shapes have draw(col, fill)
            obs.draw(col, fill=True)
            
        # Draw Player
        p_col = 8 if self.is_colliding else 10 # Red if hit, Yellow otherwise
        self.player.draw(p_col, fill=True) 

        # Instructions
        pyxel.text(5, 5, "Arrows: Move", 7)
        pyxel.text(5, 12, "Z/X: Rotate", 7)
        
        if self.is_colliding:
            pyxel.text(60, 100, "HIT!", 8)

if __name__ == "__main__":
    App()
