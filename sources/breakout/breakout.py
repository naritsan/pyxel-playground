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
        
        # パドル（カプセル形状）
        paddle_center_x = SCREEN_WIDTH / 2
        paddle_y = SCREEN_HEIGHT - 10
        self.paddle_width = 24
        self.paddle_radius = 3
        # カプセルの線分の始点と終点
        self.paddle = geo.Capsule(
            Vector2(paddle_center_x - self.paddle_width/2, paddle_y),
            Vector2(paddle_center_x + self.paddle_width/2, paddle_y),
            self.paddle_radius
        )
        self.paddle_speed = 3.0

        # ボール（円形状）
        self.ball = geo.Circle(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20, 2.5)
        self.ball_vel = Vector2(1.5, -2.0)
        
        # 壁（Lineで定義）
        self.wall_left = geo.Line(Vector2(0, 0), Vector2(0, SCREEN_HEIGHT))
        self.wall_right = geo.Line(Vector2(SCREEN_WIDTH, 0), Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.wall_top = geo.Line(Vector2(0, 0), Vector2(SCREEN_WIDTH, 0))
        # 下はゲームオーバー用（判定のみ）
        self.wall_bottom = geo.Line(Vector2(0, SCREEN_HEIGHT), Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # ブロック（ポリゴンのリスト）
        self.blocks: list[Polygon] = []
        self.setup_blocks()
        
        pyxel.run(self.update, self.draw)

    def setup_blocks(self):
        self.blocks.clear()
        cols = 8
        rows = 5
        block_w = 16
        block_h = 8
        start_x = 16
        start_y = 16
        
        colors = [8, 9, 10, 11, 12]  # 赤, オレンジ, 黄, 緑, 青系
        
        for r in range(rows):
            for c in range(cols):
                bx = start_x + c * (block_w + 2)
                by = start_y + r * (block_h + 2)
                # 矩形ブロックを作成（中心座標で指定するので調整）
                block = Polygon.create_rect(block_w, block_h, bx + block_w/2, by + block_h/2)
                # 色を動的に付与（Pythonでは許容される）
                block.color = colors[r % len(colors)]  # type: ignore
                self.blocks.append(block)

    def update(self):
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            self.reset_game()
            
        if self.is_game_over or self.is_cleared:
            return

        # 1. パドルの移動
        dx = 0
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): dx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): dx += 1
        
        # アナログスティック対応
        pad_x = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)
        if abs(pad_x) > 0.2:
            dx = pad_x
            
        if dx != 0:
            # パドルの移動を画面内に制限
            # 全体の幅 = 線分の長さ(24) + 両端の半径(3×2)
            half_width = self.paddle_width / 2 + self.paddle_radius
            
            min_x = half_width + 2
            max_x = SCREEN_WIDTH - (half_width + 2)
            
            # 新しい中心座標を計算
            current_center_x = (self.paddle.start.x + self.paddle.end.x) / 2
            new_center_x = current_center_x + (dx * self.paddle_speed)
            
            # クランプ処理（範囲内に収める）
            new_center_x = max(min_x, min(new_center_x, max_x))
            
            # パドルの座標を更新
            self.paddle.start.x = new_center_x - self.paddle_width / 2
            self.paddle.end.x = new_center_x + self.paddle_width / 2
            
        # 2. ボールの移動
        self.ball.translate(self.ball_vel.x, self.ball_vel.y)
        
        # 3. 壁との衝突判定（Lineを使用）
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
        
        # 4. パドルとの衝突判定（Y速度を反転）
        if self.ball.intersects(self.paddle):
            # 再衝突を防ぐためボールをパドルの上に押し出す
            self.ball.center.y = self.paddle.start.y - self.paddle_radius - self.ball.radius - 1
            self.ball_vel.y *= -1
            
            # パドルの移動方向をボールに反映
            self.ball_vel.x += dx * 0.3
            
            # 速度を正規化（最小/最大制限）
            speed = self.ball_vel.magnitude()
            speed = min(max(speed, 1.5), 3.5)
            self.ball_vel = self.ball_vel.normalized() * speed
            
        # 5. ブロックとの衝突判定（Y速度を反転）
        for i in range(len(self.blocks) - 1, -1, -1):
            block = self.blocks[i]
            if self.ball.intersects(block):
                # シンプルな跳ね返り: Y速度を反転
                self.ball_vel.y *= -1
                
                # ブロックを破壊
                self.blocks.pop(i)
                self.score += 10
                break  # 1フレームに1ブロックのみ

        if not self.blocks:
            self.is_cleared = True

    def reset_game(self):
        self.is_game_over = False
        self.is_cleared = False
        self.score = 0
        self.ball.center = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20)
        self.ball_vel = Vector2(random.uniform(-1.5, 1.5), -2.0).normalized() * 2.5
        
        # パドルをリセット
        paddle_center_x = SCREEN_WIDTH / 2
        paddle_y = SCREEN_HEIGHT - 10
        self.paddle.start = Vector2(paddle_center_x - self.paddle_width/2, paddle_y)
        self.paddle.end = Vector2(paddle_center_x + self.paddle_width/2, paddle_y)
        
        self.setup_blocks()

    def draw(self):
        pyxel.cls(0)
        
        # ブロックを描画
        for block in self.blocks:
            c = getattr(block, 'color', 13)
            block.draw(c, fill=True)
            
        # パドルを描画（ピンク）
        self.paddle.draw(14, fill=True)
        
        # ボールを描画（白）
        self.ball.draw(7, fill=True)
        
        # HUD（スコア表示）
        pyxel.text(5, 5, f"Score: {self.score}", 7)
        if self.is_game_over:
            pyxel.text(60, 60, "GAME OVER", 8)
            pyxel.text(50, 70, "Press R or Y to Reset", 7)
        elif self.is_cleared:
             pyxel.text(60, 60, "CLEARED!", 10)
             pyxel.text(50, 70, "Press R or Y to Reset", 7)

if __name__ == "__main__":
    App()
