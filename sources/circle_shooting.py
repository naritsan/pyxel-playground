import pyxel
import math

class Circle:
    def __init__(self, x, y, r, col):
        self.x = x
        self.y = y
        self.r = r
        self.col = col

    def intersects(self, other):
        if isinstance(other, Circle):
            dx = self.x - other.x
            dy = self.y - other.y
            dist_square = dx * dx + dy * dy
            return dist_square <= (self.r + other.r) ** 2
        return False

    def draw(self):
        pyxel.circ(self.x, self.y, self.r, self.col)

class Player(Circle):
    def __init__(self, x, y, r, col,speed):
        super().__init__(x, y, r, col)
        self.speed = speed

class Enemy(Circle):
    def __init__(self, x, y, r, col,speed,score=10):
        super().__init__(x, y, r, col)
        self.speed = speed
        self.score = score
        self.initial_y = y

class Bullet(Circle):
    def __init__(self, x, y, r, col,speed):
        super().__init__(x, y, r, col)
        self.speed = speed

class App:
    def __init__(self):
        pyxel.init(120, 160)
        self.player = Player(x=10, y=pyxel.height - 10, r=5, col=2,speed=2)
        self.enemy_list = [
            Enemy(x=0, y=10, r=5, col=3,speed=1),
            Enemy(x=0, y=40, r=5, col=4,speed=1.5),
            Enemy(x=0, y=70, r=5, col=5,speed=2),
        ]
        self.bullet_list = [] 
        self.score = 0
        self.game_over = False
        # 画面外に出たときのループをなめらかにするためにカメラを少し移動
        pyxel.camera(5,0)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player_update()
        self.bullet_update()
        self.enemy_update()
    
    def player_update(self):
        if self.is_left_pressed() and self.player.x - self.player.speed - self.player.r >= self.player.r-1:
            self.player.x -= self.player.speed
        if self.is_right_pressed() and self.player.x + self.player.speed + self.player.r <= pyxel.width + self.player.r:
            self.player.x += self.player.speed
        if self.is_up_pressed() and self.player.y - self.player.speed - self.player.r >= 0:
            self.player.y -= self.player.speed
        if self.is_down_pressed() and self.player.y + self.player.speed + self.player.r <= pyxel.height:
            self.player.y += self.player.speed

        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)) and len(self.bullet_list) < 3:
            self.bullet_list.append(Bullet(self.player.x, self.player.y - self.player.r, 2, 9,3))
        
        for enemy in self.enemy_list:
            if self.player.intersects(enemy):
                self.game_over = True
                break
    
    def enemy_update(self):
        for enemy in self.enemy_list:
            enemy.x = (enemy.x + enemy.speed) % (pyxel.width + enemy.r * 2)
            enemy.y = ( (math.sin(pyxel.frame_count * 0.1))  * 20  ) + enemy.initial_y 

    def bullet_update(self):
        for bullet in self.bullet_list:
            bullet.y -= bullet.speed

            for enemy in self.enemy_list:
                if bullet.intersects(enemy):
                    self.enemy_list.remove(enemy)
                    self.score += enemy.score
                    self.enemy_list.append(Enemy(x=0, y=pyxel.rndi(30, pyxel.height - 50), r=5, col=pyxel.rndi(1,15) ,speed=pyxel.rndf(1,3)))
                    self.bullet_list.remove(bullet)
                    break

            if bullet in self.bullet_list and bullet.y + bullet.r < 0:
                self.bullet_list.remove(bullet)

    def is_left_pressed(self):
        return pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)  
    def is_right_pressed(self):
        return pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)  
    def is_up_pressed(self):
        return pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP)  
    def is_down_pressed(self):
        return pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)

    def draw(self):

        if self.game_over:
            pyxel.cls(0)
            pyxel.text(pyxel.width // 2 - 20, pyxel.height // 2 - 10, "GAME OVER", 8)
            pyxel.text(pyxel.width // 2 - 20, pyxel.height // 2 + 10, f"SCORE: {self.score}", 7)
        else:
            pyxel.cls(0)

            self.player.draw()

            for enemy in self.enemy_list:
                enemy.draw()
            for bullet in self.bullet_list:
                bullet.draw()
            
            pyxel.text(5, 5, f"SCORE: {self.score}", 7)

App()