import pyxel
import math
from sources.utils.vector2 import Vector2
from sources.utils.polygon import Polygon
import sources.utils.geometry as geo

from sources.utils.shape import Shape

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Collision Demo")
        
        # Game State
        self.is_animating = True
        self.shape_index = 0
        self.shapes_list = [
            "Triangle", "Rect", "Pentagon", "Star", "Heart", "Arrow", "Circle", "Capsule"
        ]
        
        # Player Init
        self.player_x = 80
        self.player_y = 60
        self.player: Shape # Explicit type annotation to support polymorphism
        self.create_player_shape()
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

        # Initial rotations for setup
        self.obstacles[1].rotate(15)
        self.obstacles[3].rotate(45)
        
        # Animation frame counter
        self.frame_count = 0

        pyxel.run(self.update, self.draw)

    def create_player_shape(self):
        shape_name = self.shapes_list[self.shape_index]
        x, y = self.player_x, self.player_y
        
        if shape_name == "Triangle":
            self.player = Polygon.create_regular_polygon(3, 8, x=x, y=y)
        elif shape_name == "Rect":
            self.player = Polygon.create_rect(14, 14, x=x, y=y)
        elif shape_name == "Pentagon":
            self.player = Polygon.create_regular_polygon(5, 10, x=x, y=y)
        elif shape_name == "Star":
            self.player = Polygon.create_star(5, 10, 5, x=x, y=y)
        elif shape_name == "Heart":
            self.player = Polygon.create_heart(1.0, x=x, y=y)
        elif shape_name == "Arrow":
            self.player = Polygon.create_arrow(16, 8, 4, x=x, y=y)
        elif shape_name == "Circle":
            self.player = geo.Circle(x, y, 8)
        elif shape_name == "Capsule":
            # Vertical capsule centered at x,y
            self.player = geo.Capsule(Vector2(x, y-5), Vector2(x, y+5), 4)

    def update_player_position(self, dx, dy):
        # Update logical position vars
        self.player_x += dx
        self.player_y += dy
        
        # Update Shape object position
        if isinstance(self.player, Polygon):
            self.player.translate(dx, dy)
        elif isinstance(self.player, geo.Circle):
            self.player.translate(dx, dy)
        elif isinstance(self.player, geo.Capsule):
            self.player.translate(dx, dy)

    def update(self):
        # Toggle Animation (Space or Gamepad A)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.is_animating = not self.is_animating
            
        # Change Shape (S or Gamepad Y)
        if pyxel.btnp(pyxel.KEY_S) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            self.shape_index = (self.shape_index + 1) % len(self.shapes_list)
            # Re-create player at current position
            # Note: For Polygon rotate/scale state is lost, but that avoids complex state transfer
            current_rot = 0
            if isinstance(self.player, Polygon):
                current_rot = self.player.rotation
                
            self.create_player_shape()
            
            # Simple attempt to restore rotation for polygon to feel continuous
            if isinstance(self.player, Polygon):
                self.player.rotation = current_rot

        # Player Movement
        speed = 2.0
        dx, dy = 0, 0
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP): dy -= 1
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): dy += 1
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): dx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): dx += 1
        
        # Normalize vector
        if dx != 0 or dy != 0:
            input_vec = Vector2(dx, dy).normalized()
            self.update_player_position(input_vec.x * speed, input_vec.y * speed)
        
        # Player Rotation (Polygon and Capsule)
        if isinstance(self.player, (Polygon, geo.Capsule)):
            if pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER): self.player.rotate(-3)
            if pyxel.btn(pyxel.KEY_X) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER): self.player.rotate(3)

        # Obstacle Animation
        if self.is_animating:
            self.frame_count += 1
            
            # --- Rotation ---
            # Rect(0), Pentagon(1), Star(2), Rect(3), Capsule(5)
            self.obstacles[0].rotate(2)
            self.obstacles[1].rotate(1) 
            self.obstacles[2].rotate(1.5)
            self.obstacles[3].rotate(-0.5) 
            if len(self.obstacles) > 5:
                # Capsule
                self.obstacles[5].rotate(1.0)

            # --- Pulse (Scale) ---
            # Apply pulsing to ALL obstacles
            # Base amplitude 0.5 for everyone
            
            # Rect(0): Phase 0
            scale0 = 1.0 + 0.5 * math.sin(self.frame_count * 0.1)
            self.obstacles[0].set_scale(scale0, scale0)
            
            # Pentagon(1): Phase 0.5
            scale1 = 1.0 + 0.5 * math.sin(self.frame_count * 0.1 + 0.5)
            self.obstacles[1].set_scale(scale1, scale1)
            
            # Star(2): Phase 1.0
            scale2 = 1.0 + 0.5 * math.sin(self.frame_count * 0.1 + 1.0)
            if isinstance(self.obstacles[2], Polygon): # Check mainly for safety
                self.obstacles[2].set_scale(scale2, scale2)

            # Rect(3): Phase 1.5
            scale3 = 1.0 + 0.5 * math.sin(self.frame_count * 0.1 + 1.5)
            self.obstacles[3].set_scale(scale3, scale3)
            
            # Circle(4): Phase 2.0 (Only scale now, or both?)
            scale4 = 1.0 + 0.5 * math.sin(self.frame_count * 0.1 + 2.0)
            if len(self.obstacles) > 4:
                # Assuming I added set_scale to Circle now
                self.obstacles[4].set_scale(scale4, scale4)
                # Still moving? Let's keep moving too for fun
                move_x = math.sin(self.frame_count * 0.05) * 1.0
                self.obstacles[4].translate(move_x, 0)

            # Capsule(5): Phase 2.5
            if len(self.obstacles) > 5:
                scale5 = 1.0 + 0.5 * math.sin(self.frame_count * 0.1 + 2.5)
                self.obstacles[5].set_scale(scale5, scale5)


        # Collision Check
        self.is_colliding = False
        self.hit_indices = []
        
        for i, obs in enumerate(self.obstacles):
            if self.player.intersects(obs):
                self.is_colliding = True
                self.hit_indices.append(i)

    def draw(self):
        pyxel.cls(0)
        
        # Draw Obstacles
        for i, obs in enumerate(self.obstacles):
            col = 8 if i in self.hit_indices else 12 
            obs.draw(col, fill=True)
            
        # Draw Player
        p_col = 8 if self.is_colliding else 10 
        self.player.draw(p_col, fill=True) 

        # HUD
        c = 7
        pyxel.text(5, 5, f"Shape: {self.shapes_list[self.shape_index]} (S/Y)", c)
        pyxel.text(5, 12, "Anim: " + ("ON" if self.is_animating else "OFF") + " (Space/A)", c)
        pyxel.text(5, 19, "Z/X or LB/RB: Rotate", c)
        pyxel.text(5, 26, "Arrows/D-Pad: Move", c)
        
        if self.is_colliding:
            pyxel.text(135, 5, "HIT!", 8)

if __name__ == "__main__":
    App()
