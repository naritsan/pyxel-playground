import pyxel
import random

class App:
    def __init__(self):
        pyxel.init(160, 120)
        self.x = 55.0
        self.y = 41.0
        self.dx = 2.0
        self.dy = 2.0
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        self.x += self.dx
        self.y += self.dy

        if self.x <= 0 or self.x >= pyxel.width - 50: # approx text width
            self.dx *= -1
            self.dy += random.uniform(-0.5, 0.5) # perturb angle
        
        if self.y <= 0 or self.y >= pyxel.height - 6: # text height
            self.dy *= -1
            self.dx += random.uniform(-0.5, 0.5) # perturb angle
        
        # Keep speed reasonable
        self.dx = max(min(self.dx, 4), -4)
        if abs(self.dx) < 1: self.dx = 1 if self.dx > 0 else -1
        
        self.dy = max(min(self.dy, 4), -4)
        if abs(self.dy) < 1: self.dy = 1 if self.dy > 0 else -1

    def draw(self):
        pyxel.cls(0)
        pyxel.text(self.x, self.y, "Hello, Pyxel!", pyxel.frame_count % 16)

if __name__ == "__main__":
    App()
