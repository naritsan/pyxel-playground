import pyxel
import random
import math
from ..utils import geometry as geo
from ..utils.polygon import Polygon
from ..utils.vector2 import Vector2
from ..utils.shape import Shape

# 画面サイズ定数
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Breakout Demo")
        
        # ゲーム状態
        self.is_game_over = False
        self.is_cleared = False
        self.score = 0
        
        # オブジェクト初期化
        self._init_paddle()
        self._init_ball()
        self._init_walls()
        
        # ブロック（ポリゴンのリスト）
        self.blocks: list[Polygon] = []
        self.setup_blocks()
        
        pyxel.run(self.update, self.draw)

    def _init_paddle(self):
        """パドルを初期化。"""
        paddle_center_x = SCREEN_WIDTH / 2
        paddle_y = SCREEN_HEIGHT - 10
        self.paddle_width = 24
        self.paddle_radius = 3
        self.paddle_speed = 3.0
        self.paddle = geo.Capsule(
            Vector2(paddle_center_x - self.paddle_width/2, paddle_y),
            Vector2(paddle_center_x + self.paddle_width/2, paddle_y),
            self.paddle_radius
        )

    def _init_ball(self):
        """ボールを初期化。"""
        self.ball = geo.Circle(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20, 2.5)
        self.ball_vel = Vector2(1.5, -2.0)

    def _init_walls(self):
        """壁（Line）を初期化。"""
        self.wall_left = geo.Line(Vector2(0, 0), Vector2(0, SCREEN_HEIGHT))
        self.wall_right = geo.Line(Vector2(SCREEN_WIDTH, 0), Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.wall_top = geo.Line(Vector2(0, 0), Vector2(SCREEN_WIDTH, 0))
        self.wall_bottom = geo.Line(Vector2(0, SCREEN_HEIGHT), Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))

    def setup_blocks(self):
        """ブロックを配置。"""
        self.blocks.clear()
        cols, rows = 8, 5
        block_w, block_h = 16, 8
        start_x, start_y = 16, 16
        colors = [8, 9, 10, 11, 12]  # 赤, オレンジ, 黄, 緑, 青系
        
        for r in range(rows):
            for c in range(cols):
                bx = start_x + c * (block_w + 2)
                by = start_y + r * (block_h + 2)
                block = Polygon.create_rect(block_w, block_h, bx + block_w/2, by + block_h/2)
                block.color = colors[r % len(colors)]  # type: ignore
                self.blocks.append(block)

    # --- Update ---

    def update(self):
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            self.reset_game()
            
        if self.is_game_over or self.is_cleared:
            return

        dx = self._get_input()
        self._update_paddle(dx)
        self._update_ball()
        self._check_wall_collision()
        self._check_paddle_collision(dx)
        self._check_block_collision()
        self._check_clear_condition()

    def _get_input(self) -> float:
        """入力を取得。"""
        dx = 0.0
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            dx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            dx += 1
        
        # アナログスティック対応
        pad_x = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)
        if abs(pad_x) > 0.2:
            dx = pad_x
        return dx

    def _update_paddle(self, dx: float):
        """パドルを移動。"""
        if dx == 0:
            return
            
        half_width = self.paddle_width / 2 + self.paddle_radius
        min_x = half_width + 2
        max_x = SCREEN_WIDTH - (half_width + 2)
        
        current_center_x = (self.paddle.start.x + self.paddle.end.x) / 2
        new_center_x = current_center_x + (dx * self.paddle_speed)
        new_center_x = max(min_x, min(new_center_x, max_x))
        
        self.paddle.start.x = new_center_x - self.paddle_width / 2
        self.paddle.end.x = new_center_x + self.paddle_width / 2

    def _update_ball(self):
        """ボールを移動。"""
        self.ball.translate(self.ball_vel.x, self.ball_vel.y)

    def _check_wall_collision(self):
        """壁との衝突を判定。"""
        if self.ball.intersects(self.wall_left):
            self.ball.center.x = self.ball.radius
            self.ball_vel.x *= -1
        elif self.ball.intersects(self.wall_right):
            self.ball.center.x = SCREEN_WIDTH - self.ball.radius
            self.ball_vel.x *= -1
            
        if self.ball.intersects(self.wall_top):
            self.ball.center.y = self.ball.radius
            self.ball_vel.y *= -1
        elif self.ball.intersects(self.wall_bottom):
            self.is_game_over = True

    def _check_paddle_collision(self, dx: float):
        """パドルとの衝突を判定（当たった位置で角度が変わる）。"""
        if not self.ball.intersects(self.paddle):
            return
            
        # ボールをパドルの上に押し出す
        self.ball.center.y = self.paddle.start.y - self.paddle_radius - self.ball.radius - 1
        
        # パドルの中心からボールまでの相対位置を計算 (-1.0 ~ 1.0)
        paddle_center_x = (self.paddle.start.x + self.paddle.end.x) / 2
        paddle_half_width = self.paddle_width / 2 + self.paddle_radius
        hit_position = (self.ball.center.x - paddle_center_x) / paddle_half_width
        hit_position = max(-1.0, min(1.0, hit_position))  # クランプ
        
        # 跳ね返り角度を計算（端ほど急角度）
        # hit_position: -1.0(左端) → 0.0(中央) → 1.0(右端)
        # 角度: 150度(左端) → 90度(中央) → 30度(右端)
        # ※角度は上方向を0度として時計回り
        max_angle = 60  # 中央からの最大偏角（度）
        bounce_angle = 90 - hit_position * max_angle
        
        # 角度をラジアンに変換してベクトル計算
        rad = math.radians(bounce_angle)
        speed = self.ball_vel.magnitude()
        speed = min(max(speed, 2.0), 3.5)
        
        # 新しい速度ベクトル（常に上方向に跳ね返る）
        self.ball_vel = Vector2(math.cos(rad), -math.sin(rad)) * speed

    def _check_block_collision(self):
        """ブロックとの衝突を判定。"""
        for i in range(len(self.blocks) - 1, -1, -1):
            block = self.blocks[i]
            if self.ball.intersects(block):
                self.ball_vel.y *= -1
                self.blocks.pop(i)
                self.score += 10
                break  # 1フレームに1ブロックのみ

    def _check_clear_condition(self):
        """クリア条件を判定。"""
        if not self.blocks:
            self.is_cleared = True

    def reset_game(self):
        """ゲームをリセット。"""
        self.is_game_over = False
        self.is_cleared = False
        self.score = 0
        
        # ボールリセット
        self.ball.center = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20)
        self.ball_vel = Vector2(random.uniform(-1.5, 1.5), -2.0).normalized() * 2.5
        
        # パドルリセット
        paddle_center_x = SCREEN_WIDTH / 2
        paddle_y = SCREEN_HEIGHT - 10
        self.paddle.start = Vector2(paddle_center_x - self.paddle_width/2, paddle_y)
        self.paddle.end = Vector2(paddle_center_x + self.paddle_width/2, paddle_y)
        
        self.setup_blocks()

    # --- Draw ---

    def draw(self):
        pyxel.cls(0)
        self._draw_blocks()
        self._draw_paddle()
        self._draw_ball()
        self._draw_hud()

    def _draw_blocks(self):
        """ブロックを描画。"""
        for block in self.blocks:
            c = getattr(block, 'color', 13)
            block.draw(c, fill=True)

    def _draw_paddle(self):
        """パドルを描画。"""
        self.paddle.draw(14, fill=True)

    def _draw_ball(self):
        """ボールを描画。"""
        self.ball.draw(7, fill=True)

    def _draw_hud(self):
        """HUDを描画。"""
        pyxel.text(5, 5, f"Score: {self.score}", 7)
        if self.is_game_over:
            pyxel.text(60, 60, "GAME OVER", 8)
            pyxel.text(50, 70, "Press R or Y to Reset", 7)
        elif self.is_cleared:
            pyxel.text(60, 60, "CLEARED!", 10)
            pyxel.text(50, 70, "Press R or Y to Reset", 7)


if __name__ == "__main__":
    App()
