"""
pyxresファイルからスプライトを読み込んで表示するシンプルなデモ。
pyxel.load() と pyxel.blt() の基本的な使い方を示す。
"""
import pyxel
from ..utils import geometry as geo
from ..utils.vector2 import Vector2

# 画面サイズ
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128

# スプライトサイズ
SPRITE_SIZE = 8

# タイルサイズ
TILE_SIZE = 8

# 床タイルのID（pyxresのタイル番号に合わせて調整）
# pget()は(u, v)タプルを返す
FLOOR_TILES = [(1, 13), (6, 13), (3, 0),(6,11),(12,13)]  # 床とみなすタイルIDのリスト

# はしごタイルのID
# (88,112) → (11,14), (96,112) → (12,14)
LADDER_TILES = [(11, 14), (12, 14)]  # はしごとみなすタイルIDのリスト


class Player:
    """プレイヤーキャラクター。"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 1.5
        
        # アニメーション用
        self.is_moving = False
        self.anim_counter = 0
        
        # スプライト設定
        self.sprite_u = 40  # イメージバンク内のX座標
        self.sprite_v = 0   # イメージバンク内のY座標
        self.size = SPRITE_SIZE
        self.facing_right = True  # 右向きかどうか
        
        # 重力・速度
        self.vy = 0.0  # Y方向の速度
        self.gravity = 0.2  # 通常の重力
        self.fall_gravity = 0.6  # 落下時の重力（速い）
        self.jump_power = -3.5  # ジャンプ力（負の値）
        self.on_ground = False
        self.on_ladder = False  # はしごにいるか
        self.climb_speed = 1.0  # はしごを登る速度
        
        # 当たり判定用の円（中心座標をスプライトの中心に）
        self.hitbox = geo.Circle(x + self.size / 2, y + self.size / 2, self.size / 2 - 1)
        
        # 攻撃アニメーション
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_frames = [(56, 0), (64, 0), (72, 0)]  # 攻撃タイルの座標
        self.attack_speed = 2  # フレームごとのアニメ速度
        self.attack_counter = 0
        
        # はしごアニメーション（タイル座標を設定）
        self.climb_frames = [(24, 0), (32, 0)]  # はしご登りタイル（要調整）
        self.is_climbing = False  # 実際に登っているか
        self.ladder_released = False  # はしごを離したか（再キャッチ防止用）

    def update(self):
        """入力処理と移動。"""
        dx = 0.0
        # はしご上では左右移動不可
        if not self.on_ladder:
            if pyxel.btn(pyxel.KEY_LEFT):
                dx -= self.speed
            if pyxel.btn(pyxel.KEY_RIGHT):
                dx += self.speed
        
        # 動いているか判定
        self.is_moving = (dx != 0)
        
        # 向きを記録
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
        
        # 動いているときだけアニメーションカウンターを進める
        if self.is_moving:
            self.anim_counter += 1
        
        # ジャンプ（地面にいるときのみ）
        if self.on_ground:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.vy = self.jump_power
                self.on_ground = False
        else:
            # ジャンプボタンを離したら上昇を早めにカット（可変ジャンプ高さ）
            if self.vy < 0:  # 上昇中
                if not (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)):
                    self.vy *= 0.5  # 上昇速度を半減
        
        # 攻撃入力（ZキーまたはゲームパッドX）
        if not self.is_attacking:
            if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.is_attacking = True
                self.attack_frame = 0
                self.attack_counter = 0
                # self.anim_counter += 5  # 歩行アニメーションを進める
        else:
            # 攻撃アニメーション進行
            self.attack_counter += 1
            # self.anim_counter += 1  # 攻撃中も歩行アニメを進める
            if self.attack_counter >= self.attack_speed:
                self.attack_counter = 0
                self.attack_frame += 1
                if self.attack_frame >= len(self.attack_frames):
                    # アニメーション終了
                    self.is_attacking = False
        # はしご判定
        center_x = int((self.x + self.size / 2) // TILE_SIZE)
        center_y = int((self.y + self.size / 2) // TILE_SIZE)
        is_on_ladder_tile = self._is_ladder(center_x, center_y)
        
        # はしごタイルから離れたらクールダウン解除
        if not is_on_ladder_tile:
            self.ladder_released = False
        
        # はしごをつかむ条件：タイル上 + クールダウン中でない + 上下キーを新規押し
        if is_on_ladder_tile and not self.ladder_released:
            if not self.on_ladder:
                # 上下キーを押したらつかむ
                if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_DOWN):
                    self.on_ladder = True
            # 既につかんでいる場合は継続
        else:
            self.on_ladder = False
        
        # はしごにいる場合の上下移動
        if self.on_ladder:
            # ジャンプボタンではしごを離す
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.on_ladder = False
                self.is_climbing = False
                self.ladder_released = True  # クールダウン開始
            else:
                dy = 0.0
                if pyxel.btn(pyxel.KEY_UP):
                    dy -= self.climb_speed
                if pyxel.btn(pyxel.KEY_DOWN):
                    dy += self.climb_speed
                
                # 登っているか判定
                if dy != 0:
                    self.is_climbing = True
                    # はしごの中心にX座標をスナップ
                    ladder_center_x = center_x * TILE_SIZE + TILE_SIZE / 2 - self.size / 2
                    self.x = ladder_center_x
                    self.anim_counter += 1  # はしごアニメを進める
                else:
                    self.is_climbing = False
                
                self.y += dy
                self.vy = 0  # はしご中は重力無効
        else:
            self.is_climbing = False
            # 重力を適用（落下中は速い重力）
            if self.vy > 0:
                self.vy += self.fall_gravity
            else:
                self.vy += self.gravity
        
        # X方向の移動と衝突判定
        self.x += dx
        self._check_horizontal_collision(dx)
        
        # Y方向の移動と衝突判定
        self.y += self.vy
        self._check_vertical_collision()
        
        # 画面外に落ちたらリセット
        if self.y > SCREEN_HEIGHT:
            self.y = 0.0
            self.vy = 0.0
        
        # 画面内に制限（X方向）
        self.x = max(0.0, min(float(SCREEN_WIDTH - self.size), self.x))
        
        # ヒットボックスの位置を同期
        self.hitbox.center.x = self.x + self.size / 2
        self.hitbox.center.y = self.y + self.size / 2

    def _is_solid(self, tx: int, ty: int) -> bool:
        """タイルが固体（床・壁）かどうか。"""
        if 0 <= tx < SCREEN_WIDTH // TILE_SIZE and 0 <= ty < SCREEN_HEIGHT // TILE_SIZE:
            tile_id = pyxel.tilemaps[2].pget(tx, ty)  # (u, v)タプル
            return tile_id in FLOOR_TILES
        return False

    def _is_ladder(self, tx: int, ty: int) -> bool:
        """タイルがはしごかどうか。"""
        if 0 <= tx < SCREEN_WIDTH // TILE_SIZE and 0 <= ty < SCREEN_HEIGHT // TILE_SIZE:
            tile_id = pyxel.tilemaps[2].pget(tx, ty)  # (u, v)タプル
            return tile_id in LADDER_TILES
        return False

    def _check_horizontal_collision(self, dx: float):
        """左右の壁との衝突判定。"""
        # プレイヤーの左右端のタイル座標
        top = int(self.y // TILE_SIZE)
        bottom = int((self.y + self.size - 1) // TILE_SIZE)
        
        if dx > 0:  # 右に移動
            right = int((self.x + self.size) // TILE_SIZE)
            for ty in range(top, bottom + 1):
                if self._is_solid(right, ty):
                    # 右壁に押し戻す
                    self.x = right * TILE_SIZE - self.size
                    break
        elif dx < 0:  # 左に移動
            left = int(self.x // TILE_SIZE)
            for ty in range(top, bottom + 1):
                if self._is_solid(left, ty):
                    # 左壁に押し戻す
                    self.x = (left + 1) * TILE_SIZE
                    break

    def _check_vertical_collision(self):
        """上下の床・天井との衝突判定。"""
        left = int(self.x // TILE_SIZE)
        right = int((self.x + self.size - 1) // TILE_SIZE)
        
        self.on_ground = False
        
        if self.vy > 0:  # 下に落下中
            bottom = int((self.y + self.size) // TILE_SIZE)
            for tx in range(left, right + 1):
                if self._is_solid(tx, bottom):
                    # 床に乗る
                    self.y = bottom * TILE_SIZE - self.size
                    self.vy = 0
                    self.on_ground = True
                    break
        elif self.vy < 0:  # 上に移動中（ジャンプ）
            top = int(self.y // TILE_SIZE)
            for tx in range(left, right + 1):
                if self._is_solid(tx, top):
                    # 天井にぶつかる
                    self.y = (top + 1) * TILE_SIZE
                    self.vy = 0
                    break


    def draw(self):
        """プレイヤーを描画。"""
        # はしごにいる場合は専用スプライト
        if self.on_ladder:
            if self.is_climbing:
                # 登り中はアニメーション
                climb_frame = (self.anim_counter // 5) % len(self.climb_frames)
            else:
                # 停止中は最初のフレームで固定
                climb_frame = 0
            sprite_u, sprite_v = self.climb_frames[climb_frame]
            pyxel.blt(self.x, self.y, 0, sprite_u, sprite_v, self.size, self.size, 0)
            return  # はしご中は他の描画をスキップ
        
        # 歩行アニメーション（動いているとき、攻撃中は固定）
        if self.is_attacking:
            anim_frame = 1  # 攻撃中は2番目のフレームで固定
        elif self.is_moving:
            anim_frame = (self.anim_counter // 5) % 2
        else:
            anim_frame = 0  # 止まっているときは最初のフレーム
        
        sprite_u = self.sprite_u + anim_frame * self.size
        
        # スプライト描画（左向きなら反転）
        # wをマイナスにすると水平反転
        if self.facing_right:
            pyxel.blt(self.x, self.y, 0, sprite_u, self.sprite_v, self.size, self.size, 0)
        else:
            # 左向き: uは右端から指定し、wをマイナスに
            pyxel.blt(self.x, self.y, 0, sprite_u , self.sprite_v, -self.size, self.size, 0)
        
        # 攻撃アニメーション描画
        if self.is_attacking:
            attack_u, attack_v = self.attack_frames[self.attack_frame]
            # プレイヤーの前面に描画
            if self.facing_right:
                attack_x = self.x + self.size
                pyxel.blt(attack_x, self.y, 0, attack_u, attack_v, self.size, self.size, 0)
            else:
                attack_x = self.x - self.size
                pyxel.blt(attack_x, self.y, 0, attack_u, attack_v, -self.size, self.size, 0)
    
    @property
    def anim_frame(self) -> int:
        """現在のアニメーションフレーム（デバッグ用）。"""
        if self.is_moving:
            return (self.anim_counter // 5) % 2
        return 0


class Enemy:
    """敵キャラクター。"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 0.5
        
        # アニメーション用
        self.anim_counter = 0
        
        # スプライト設定
        self.sprite_u = 0  # 敵スプライトの位置（要調整）
        self.sprite_v = 8
        self.size = SPRITE_SIZE
        self.facing_right = False  # 左向き
        
        # 当たり判定用の円
        self.hitbox = geo.Circle(x + self.size / 2, y + self.size / 2, self.size / 2 - 1)
        
        # 移動設定
        self.move_dir = -1  # -1: 左, 1: 右
        self.move_range = (x - 30, x + 30)  # 左右に30ピクセル移動

    def update(self):
        """自動移動。"""
        # 左右に往復移動
        self.x += self.speed * self.move_dir
        
        # 端に到達したら方向転換
        if self.x <= self.move_range[0]:
            self.move_dir = 1
            self.facing_right = True
        elif self.x >= self.move_range[1]:
            self.move_dir = -1
            self.facing_right = False
        
        # アニメーションカウンター
        self.anim_counter += 1
        
        # ヒットボックスの位置を同期
        self.hitbox.center.x = self.x + self.size / 2
        self.hitbox.center.y = self.y + self.size / 2

    def draw(self):
        """敵を描画。"""
        anim_frame = (self.anim_counter // 8) % 2
        sprite_u = self.sprite_u + anim_frame * self.size
        
        if self.facing_right:
            pyxel.blt(self.x, self.y, 0, sprite_u, self.sprite_v, self.size, self.size, 0)
        else:
            pyxel.blt(self.x, self.y, 0, sprite_u, self.sprite_v, -self.size, self.size, 0)


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxres Sprite Demo")
        
        # pyxresファイルからスプライトを読み込む
        pyxel.load("assets/sample.pyxres")
        
        # プレイヤー
        self.player = Player(0.0, 112.0)
        
        # 敵
        self.enemy = Enemy(100.0, 112.0)
        
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()
        self.enemy.update()
        
        # プレイヤーと敵の当たり判定
        self.is_colliding = self.player.hitbox.intersects(self.enemy.hitbox)

    def draw(self):
        pyxel.cls(0)
        
        # タイルマップ描画
        pyxel.bltm(0, 0, 2, 0, 0, 128, 128)

        # プレイヤー描画
        self.player.draw()
        
        # 敵描画
        self.enemy.draw()
        
        # 当たり判定の円を描画（デバッグ用）
        self.player.hitbox.draw(11, fill=False)  # 緑
        self.enemy.hitbox.draw(8, fill=False)    # 赤
        
        # HUD
        pyxel.text(5, 5, "Arrows: Move", 7)
        pyxel.text(5, 15, f"frame_count: {pyxel.frame_count}", 7)
        pyxel.text(5, 25, f"anim_frame: {self.player.anim_frame}", 10)
        
        # 足元のタイルID表示
        foot_x = int((self.player.x + SPRITE_SIZE / 2) // TILE_SIZE)
        foot_y = int((self.player.y + SPRITE_SIZE) // TILE_SIZE)
        if 0 <= foot_x < SCREEN_WIDTH // TILE_SIZE and 0 <= foot_y < SCREEN_HEIGHT // TILE_SIZE:
            tile_id = pyxel.tilemaps[2].pget(foot_x, foot_y)
            pyxel.text(5, 35, f"tile: {tile_id}", 9)
        
        pyxel.text(5, SCREEN_HEIGHT - 10, f"Pos: ({int(self.player.x)}, {int(self.player.y)})", 5)
        
        # 当たり判定結果
        if self.is_colliding:
            pyxel.text(50, 60, "HIT!", 8)


if __name__ == "__main__":
    App()
