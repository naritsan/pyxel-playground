from __future__ import annotations
import pyxel
import math
from .vector2 import Vector2
from .shape import Shape
from . import geometry  # 循環参照を安全に処理するためのローカルインポート

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .geometry import Circle, Capsule

class Polygon(Shape):
    """
    複数の頂点を持つ2Dポリゴンを表すクラス。
    ローカル頂点を管理し、トランスフォーム（スケール、回転、移動）を適用して
    ワールド座標を計算する。
    """

    def __init__(self, vertices: list[Vector2], x: float = 0, y: float = 0):
        # ローカル座標（図形の中心/原点からの相対座標）
        self.local_vertices: list[Vector2] = vertices
        
        # ワールド状態
        self.position: Vector2 = Vector2(x, y)
        self.rotation: float = 0.0  # 度単位
        self.scale: Vector2 = Vector2(1.0, 1.0)

    def get_transformed_vertices(self) -> list[Vector2]:
        """
        現在のスケール、回転、位置でトランスフォームされた頂点リストを返す。
        適用順序: スケール → 回転 → 移動
        """
        # 回転の三角関数を事前計算
        rad = math.radians(self.rotation)
        cos_theta = math.cos(rad)
        sin_theta = math.sin(rad)

        world_vertices = []

        for v in self.local_vertices:
            # 1. スケール
            sx = v.x * self.scale.x
            sy = v.y * self.scale.y

            # 2. 回転
            # x' = x*cos - y*sin
            # y' = x*sin + y*cos
            rx = sx * cos_theta - sy * sin_theta
            ry = sx * sin_theta + sy * cos_theta

            # 3. 移動（位置を加算）
            wx = rx + self.position.x
            wy = ry + self.position.y

            world_vertices.append(Vector2(wx, wy))

        return world_vertices

    def translate(self, dx: float, dy: float):
        """ポリゴンを移動する。"""
        self.position += Vector2(dx, dy)

    def rotate(self, angle: float):
        """ポリゴンを指定した角度（度単位）で回転する。"""
        self.rotation += angle

    def set_scale(self, sx: float, sy: float):
        """ポリゴンのスケールを設定する。"""
        self.scale = Vector2(sx, sy)

    @classmethod
    def create_rect(cls, width: float, height: float, x: float = 0, y: float = 0) -> Polygon:
        """(x, y)を中心とした矩形を作成する。"""
        hw = width / 2
        hh = height / 2
        vertices = [
            Vector2(-hw, -hh), Vector2(hw, -hh),
            Vector2(hw, hh), Vector2(-hw, hh)
        ]
        return cls(vertices, x, y)

    @classmethod
    def create_regular_polygon(cls, sides: int, radius: float, x: float = 0, y: float = 0, angle_offset: float = -90) -> Polygon:
        """正多角形を作成する。"""
        if sides < 3:
            raise ValueError("ポリゴンは少なくとも3辺必要です。")
        vertices = []
        angle_step = 360 / sides
        for i in range(sides):
            deg = angle_offset + i * angle_step
            rad = math.radians(deg)
            vx = radius * math.cos(rad)
            vy = radius * math.sin(rad)
            vertices.append(Vector2(vx, vy))
        return cls(vertices, x, y)

    @classmethod
    def create_star(cls, points: int, outer_radius: float, inner_radius: float, x: float = 0, y: float = 0) -> Polygon:
        """星形を作成する。"""
        vertices = []
        angle_step = 180 / points
        angle_offset = -90
        for i in range(points * 2):
            deg = angle_offset + i * angle_step
            rad = math.radians(deg)
            radius = outer_radius if i % 2 == 0 else inner_radius
            vx = radius * math.cos(rad)
            vy = radius * math.sin(rad)
            vertices.append(Vector2(vx, vy))
        return cls(vertices, x, y)

    @classmethod
    def create_heart(cls, scale: float = 1.0, x: float = 0, y: float = 0) -> Polygon:
        """ハート形を作成する。"""
        vertices = [
            Vector2(0, -0.25), Vector2(0.3, -0.6), Vector2(0.7, -0.6),
            Vector2(0.9, -0.3), Vector2(0.9, 0.1), Vector2(0, 0.8),
            Vector2(-0.9, 0.1), Vector2(-0.9, -0.3), Vector2(-0.7, -0.6),
           Vector2(-0.3, -0.6)
        ]
        vertices = [v * scale * 10 for v in vertices]
        return cls(vertices, x, y)

    @classmethod
    def create_arrow(cls, length: float, head_size: float, shaft_width: float, x: float = 0, y: float = 0) -> Polygon:
        """上向きの矢印を作成する。"""
        hw, sw, l = head_size / 2, shaft_width / 2, length / 2
        vertices = [
            Vector2(0, -l - hw), Vector2(hw, -l + hw), Vector2(sw, -l + hw),
            Vector2(sw, l), Vector2(-sw, l), Vector2(-sw, -l + hw), Vector2(-hw, -l + hw)
        ]
        return cls(vertices, x, y)

    def draw(self, col: int, fill: bool = False):
        """ポリゴンを描画する。"""
        verts = self.get_transformed_vertices()
        center = self.position
        if fill:
            for i in range(len(verts)):
                p1 = verts[i]
                p2 = verts[(i + 1) % len(verts)]
                pyxel.tri(center.x, center.y, p1.x, p1.y, p2.x, p2.y, col)
        else:
            for i in range(len(verts)):
                p1 = verts[i]
                p2 = verts[(i + 1) % len(verts)]
                pyxel.line(p1.x, p1.y, p2.x, p2.y, col)

    def intersects(self, other: Shape) -> bool:
        if isinstance(other, Polygon):
            return self._intersects_polygon(other)
        elif isinstance(other, geometry.Circle):
            return self._intersects_circle(other)
        elif isinstance(other, geometry.Capsule):
            return self._intersects_capsule(other)
        return False

    def _intersects_polygon(self, other: Polygon) -> bool:
        """SATを使用してポリゴン同士の交差を判定する。"""
        axes = self.get_axes() + other.get_axes()
        for axis in axes:
            min1, max1 = self.project(axis)
            min2, max2 = other.project(axis)
            if max1 < min2 or max2 < min1:
                return False
        return True

    def _intersects_circle(self, other: geometry.Circle) -> bool:
        """SATを使用して円との交差を判定する。"""
        verts = self.get_transformed_vertices()
        center = other.center
        
        closest_vertex = verts[0]
        min_dist = (center - verts[0]).magnitude()
        for v in verts:
            dist = (center - v).magnitude()
            if dist < min_dist:
                min_dist = dist
                closest_vertex = v
        
        axes = self.get_axes()
        if min_dist > 0:
             axes.append((center - closest_vertex).normalized())

        for axis in axes:
            min1, max1 = self.project(axis)
            center_proj = center.dot(axis)
            min2, max2 = center_proj - other.radius, center_proj + other.radius
            if max1 < min2 or max2 < min1:
                return False
        return True

    def _intersects_capsule(self, other: geometry.Capsule) -> bool:
        """カプセルとの交差を判定する。"""
        # 端点をチェック
        if self._intersects_circle(geometry.Circle(other.start.x, other.start.y, other.radius)): return True
        if self._intersects_circle(geometry.Circle(other.end.x, other.end.y, other.radius)): return True
            
        # ボディ部分の近似判定（簡略化したSAT）
        axes = self.get_axes()
        cap_dir = other.get_direction()
        if cap_dir.x != 0 or cap_dir.y != 0:
            axes.append(Vector2(-cap_dir.y, cap_dir.x).normalized())
            
        for axis in axes:
            min_p, max_p = self.project(axis)
            p_start, p_end = other.start.dot(axis), other.end.dot(axis)
            min_c, max_c = min(p_start, p_end) - other.radius, max(p_start, p_end) + other.radius
            if max_p < min_c or max_c < min_p:
                return False
        return True

    def get_axes(self) -> list[Vector2]:
        """ポリゴンの全辺に対する法線ベクトルのリストを返す。"""
        axes = []
        verts = self.get_transformed_vertices()
        for i in range(len(verts)):
            p1 = verts[i]
            p2 = verts[(i + 1) % len(verts)]
            edge = p2 - p1
            axes.append(Vector2(-edge.y, edge.x).normalized())
        return axes

    def project(self, axis: Vector2) -> tuple[float, float]:
        """ポリゴンを指定した軸に射影する。"""
        verts = self.get_transformed_vertices()
        if not verts: return 0.0, 0.0
        min_proj = max_proj = verts[0].dot(axis)
        for i in range(1, len(verts)):
            proj = verts[i].dot(axis)
            if proj < min_proj: min_proj = proj
            if proj > max_proj: max_proj = proj
        return min_proj, max_proj
