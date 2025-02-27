import tkinter as tk
import logging
import math
from enum import Enum

"""
描画キャンバスモジュール

このモジュールは図形描画機能を提供するtkinterキャンバスの拡張クラスを実装します。
様々な図形（線、四角形、円、多角形）の描画、選択、編集、移動、リサイズなどの機能があります。

主要な機能:
- 図形の描画（線、四角形、円、多角形）
- 図形の選択と編集
- アンドゥ/リドゥ機能
- スナップ機能（端点、中点、交点）
- キーボードショートカット

キーボードショートカット:
- Ctrl+Z: アンドゥ（直前の操作を取り消し）
- Ctrl+Y: リドゥ（取り消した操作をやり直し）
- Delete: 選択した図形の削除
- Ctrl+A: 全ての図形を選択

使用例:
```python
canvas = DrawingCanvas(root)
canvas.pack(fill="both", expand=True)
canvas.mode = "rectangle"  # 描画モードを四角形に設定
```
"""

logger = logging.getLogger(__name__)

# 描画状態を管理するための列挙型
class DrawingState(Enum):
    IDLE = 0      # 待機状態
    DRAWING = 1   # 描画中
    SELECTING = 2 # 選択中
    MOVING = 3    # 移動中
    RESIZING = 4  # リサイズ中
    ROTATING = 5  # 回転中

class Shape:
    """図形の基底クラス"""
    def __init__(self, color="black", width=1, style=None):
        self.color = color
        self.width = width
        self.style = style  # None: 実線, (5,5): 破線
        self.points = []  # 図形を構成する点のリスト

    def draw(self, canvas):
        """図形を描画する基底メソッド"""
        pass

    def draw_selected(self, canvas):
        """選択状態の図形を描画する基底メソッド"""
        pass

class Line(Shape):
    """線分クラス"""
    def __init__(self, x1, y1, x2, y2, color="black", width=1, style=None):
        super().__init__(color, width, style)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.points = [(x1, y1), (x2, y2)]

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2,
                         fill=self.color, width=self.width, dash=self.style)

    def draw_selected(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2,
                         fill="blue", width=2)
        # 端点のハンドルを描画
        for x, y in [(self.x1, self.y1), (self.x2, self.y2)]:
            canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5,
                                 outline="blue", fill="white", tags="selection_outline")

class Rectangle(Shape):
    """矩形クラス"""
    def __init__(self, x1, y1, x2, y2, color="black", width=1, style=None):
        super().__init__(color, width, style)
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.points = [
            (self.x1, self.y1),
            (self.x2, self.y1),
            (self.x2, self.y2),
            (self.x1, self.y2)
        ]

    def draw(self, canvas):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                             outline=self.color, width=self.width, dash=self.style)

    def draw_selected(self, canvas):
        # 外枠を描画
        canvas.create_rectangle(self.x1 - 2, self.y1 - 2,
                             self.x2 + 2, self.y2 + 2,
                             outline="blue", width=2)
        # 各辺を強調表示
        edges = [
            (self.x1, self.y1, self.x2, self.y1),  # 上辺
            (self.x2, self.y1, self.x2, self.y2),  # 右辺
            (self.x2, self.y2, self.x1, self.y2),  # 下辺
            (self.x1, self.y2, self.x1, self.y1)   # 左辺
        ]
        for x1, y1, x2, y2 in edges:
            canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
        # 頂点のハンドルを描画
        for x, y in self.points:
            canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5,
                                 outline="blue", fill="white", tags="selection_outline")
        # 辺の中点のハンドルを描画
        midpoints = [
            ((self.x1 + self.x2) / 2, self.y1),  # 上辺中点
            ((self.x1 + self.x2) / 2, self.y2),  # 下辺中点
            (self.x1, (self.y1 + self.y2) / 2),  # 左辺中点
            (self.x2, (self.y1 + self.y2) / 2)   # 右辺中点
        ]
        for x, y in midpoints:
            canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5,
                                 outline="blue", fill="white", tags="selection_outline")

class Circle(Shape):
    """円クラス"""
    def __init__(self, center_x, center_y, x2, y2, color="black", width=1, style=None):
        super().__init__(color, width, style)
        self.center_x = center_x
        self.center_y = center_y
        self.x2 = x2
        self.y2 = y2
        self.radius = math.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)
        self.points = [(center_x, center_y), (x2, y2)]

    def draw(self, canvas):
        canvas.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                         self.center_x + self.radius, self.center_y + self.radius,
                         outline=self.color, width=self.width, dash=self.style)

    def draw_selected(self, canvas):
        # 外枠を描画
        canvas.create_oval(self.center_x - self.radius - 2, self.center_y - self.radius - 2,
                         self.center_x + self.radius + 2, self.center_y + self.radius + 2,
                         outline="blue", width=2)
        # 中心点と半径点のハンドルを描画
        for x, y in self.points:
            canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5,
                                 outline="blue", fill="white", tags="selection_outline")

class Polygon(Shape):
    """多角形クラス"""
    def __init__(self, points=None, color="black", width=1, style=None):
        super().__init__(color, width, style)
        self.points = points if points is not None else []

    def draw(self, canvas):
        if len(self.points) >= 2:
            coords = []
            for point in self.points:
                coords.extend(point)
            if len(self.points) >= 3:
                coords.extend(self.points[0])  # 最初の点に戻る
            canvas.create_line(*coords, fill=self.color, width=self.width, dash=self.style)

    def draw_selected(self, canvas):
        # 頂点のハンドルを描画
        for x, y in self.points:
            canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5,
                                 outline="blue", fill="white", tags="selection_outline")
        # 辺を強調表示
        if len(self.points) >= 2:
            coords = []
            for point in self.points:
                coords.extend(point)
            if len(self.points) >= 3:
                coords.extend(self.points[0])  # 最初の点に戻る
            canvas.create_line(*coords, fill="blue", width=2)

class DrawingCanvas(tk.Canvas):
    """描画用キャンバスクラス"""
    MIN_SIZE = 10  # 図形の最小サイズ

    def __init__(self, master=None, **kwargs):
        """描画キャンバスの初期化"""
        super().__init__(master, **kwargs)
        
        self.shapes = []  # 描画された図形のリスト
        self.current_points = []  # 現在の描画中の点のリスト
        self.mode = "line"  # 描画モード（line, rectangle, circle, polygon）
        
        self.current_color = "black"  # 現在の描画色
        self.current_width = 1  # 現在の線幅
        self.current_style = None  # 現在の線スタイル
        
        # 選択中の図形を単一からリストに変更
        self.selected_shapes = []  # 選択中の図形のリスト
        self.selected_endpoint = None  # 選択中の端点（0: 始点, 1: 終点）
        self.is_moving = False  # 図形を移動中かどうか
        self.is_resizing = False  # 図形をリサイズ中かどうか
        self.resize_handle = None  # リサイズ中のハンドル
        self.last_x = None  # 最後のマウスX座標
        self.last_y = None  # 最後のマウスY座標
        
        # アンドゥ/リドゥスタックを初期化
        self.undo_stack = []  # 元に戻す操作のスタック
        self.redo_stack = []  # やり直す操作のスタック
        
        # イベントバインド
        self.bind("<Button-1>", self.on_click)  # 左クリック
        self.bind("<Button-3>", self.on_right_click)  # 右クリック
        self.bind("<Motion>", self.on_motion)  # マウス移動
        self.bind("<Escape>", self.on_escape)  # ESCキー
        
        logger.debug("描画キャンバスを初期化")
        
        # スタイル設定
        self.snap_enabled = True  # スナップを有効化
        self.snap_distance = 10  # スナップする距離（ピクセル）
        self.snap_types = {
            "endpoint": True,  # 端点
            "midpoint": True,  # 中点
            "intersection": True  # 交点
        }
        
        # 編集用のイベントバインドを追加
        self.bind("<Control-Button-1>", self.on_select)  # Ctrl+クリックで選択
        self.bind("<B1-Motion>", self.on_drag)  # ドラッグ処理
        self.bind("<ButtonRelease-1>", self.on_release)  # マウスボタン解放
        
        # キーボードショートカットの追加
        self.bind("<KeyPress>", self.handle_keyboard_event)
        self.bind("<Control-z>", lambda event: self.undo())  # Ctrl+Z: アンドゥ
        self.bind("<Control-y>", lambda event: self.redo())  # Ctrl+Y: リドゥ
        self.bind("<Delete>", lambda event: self.delete_selected())  # Delete: 選択図形の削除
        self.bind("<Control-a>", lambda event: self.select_all())  # Ctrl+A: 全選択
        
        # フォーカス関連の設定
        self.focus_set()  # 初期フォーカスをキャンバスに設定
        self.bind("<FocusIn>", lambda event: logger.info("キャンバスがフォーカスを取得"))
        self.bind("<FocusOut>", lambda event: logger.info("キャンバスがフォーカスを失いました"))
        
        # オリジナルのクリックハンドラを保存
        self._orig_on_click = self.on_click
        self._orig_on_right_click = self.on_right_click
        
        # 元のハンドラにフォーカス設定を追加
        def click_with_focus(event):
            self.focus_set()
            return self._orig_on_click(event)
            
        def right_click_with_focus(event):
            self.focus_set()
            return self._orig_on_right_click(event)
            
        # イベントハンドラを上書き
        self.on_click = click_with_focus
        self.on_right_click = right_click_with_focus
        
    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        """描画モードを設定し、選択状態をクリア"""
        self._mode = value
        self.selected_shapes = []
        self.selected_endpoint = None
        self.is_moving = False
        self.is_resizing = False
        self.resize_handle = None
        self.redraw()
        
    def set_color(self, color):
        """描画色を設定"""
        old_color = self.current_color
        self.current_color = color
        logger.debug(f"描画色を変更: {old_color} -> {color}")
        
        # 色の変更を記録
        self.push_property_change("current_color", old_color, color)
        
    def set_width(self, width):
        """線幅を設定"""
        old_width = self.current_width
        self.current_width = width
        logger.debug(f"線幅を変更: {old_width} -> {width}")
        
        # 線幅の変更を記録
        self.push_property_change("current_width", old_width, width)
        
    def set_style(self, style):
        """線スタイルを設定"""
        old_style = self.current_style
        self.current_style = style
        logger.debug(f"線スタイルを変更: {old_style} -> {style}")
        
        # 線スタイルの変更を記録
        self.push_property_change("current_style", old_style, style)
        
    def reset(self):
        """キャンバスの状態をリセット"""
        self.shapes = []
        self.current_points = []
        self.delete("all")  # キャンバス上の全ての図形を削除
        
    def get_line_intersection(self, line1, line2):
        """2つの線分の交点を計算"""
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2
        
        # 線分の方程式: P = P1 + t(P2-P1), 0 <= t <= 1
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:  # 平行または重なっている
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
        
        # 交点が両方の線分上にある場合のみ
        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (x, y)
            
    def get_circle_line_intersection(self, line, circle):
        """円と直線の交点を計算する"""
        # 円の中心座標と半径を取得
        cx, cy = circle.center_x, circle.center_y
        r = circle.radius

        # 直線の始点と終点を取得
        x1, y1 = line.x1, line.y1
        x2, y2 = line.x2, line.y2

        # 垂直な線の場合
        if x2 - x1 == 0:
            x = x1
            a = 1
            b = -2 * cy
            c = cy * cy + (x - cx) * (x - cx) - r * r
            D = b * b - 4 * a * c
            if D < -0.1:  # 交点なし
                return []
            elif abs(D) <= 0.1:  # 1点で接する
                y = -b / (2 * a)
                if min(y1, y2) <= y <= max(y1, y2):
                    return [(x, y)]
                return []
            else:  # 2点で交わる
                y1_int = (-b + math.sqrt(D)) / (2 * a)
                y2_int = (-b - math.sqrt(D)) / (2 * a)
                points = []
                if min(y1, y2) <= y1_int <= max(y1, y2):
                    points.append((x, y1_int))
                if min(y1, y2) <= y2_int <= max(y1, y2):
                    points.append((x, y2_int))
                return points

        # 水平な線の場合
        if y2 - y1 == 0:
            y = y1
            a = 1
            b = -2 * cx
            c = cx * cx + (y - cy) * (y - cy) - r * r
            D = b * b - 4 * a * c
            if D < -0.1:  # 交点なし
                return []
            elif abs(D) <= 0.1:  # 1点で接する
                x = -b / (2 * a)
                if min(x1, x2) <= x <= max(x1, x2):
                    return [(x, y)]
                return []
            else:  # 2点で交わる
                x1_int = (-b + math.sqrt(D)) / (2 * a)
                x2_int = (-b - math.sqrt(D)) / (2 * a)
                points = []
                if min(x1, x2) <= x1_int <= max(x1, x2):
                    points.append((x1_int, y))
                if min(x1, x2) <= x2_int <= max(x1, x2):
                    points.append((x2_int, y))
                return points

        # 一般の場合
        m = (y2 - y1) / (x2 - x1)  # 傾き
        b = y1 - m * x1  # y切片

        # 円の方程式と直線の方程式を連立して解く
        # 円の方程式: (x - cx)^2 + (y - cy)^2 = r^2
        # 直線の方程式: y = mx + b
        # 代入して整理すると: (x - cx)^2 + (mx + b - cy)^2 = r^2

        # 2次方程式の係数を計算
        A = 1 + m * m
        B = 2 * (m * (b - cy) - cx)
        C = cx * cx + (b - cy) * (b - cy) - r * r

        # 判別式を計算
        D = B * B - 4 * A * C

        if D < -0.1:  # 交点なし
            return []
        elif abs(D) <= 0.1:  # 1点で接する
            x = -B / (2 * A)
            y = m * x + b
            if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
                return [(x, y)]
            return []
        else:  # 2点で交わる
            x1_int = (-B + math.sqrt(D)) / (2 * A)
            x2_int = (-B - math.sqrt(D)) / (2 * A)
            points = []
            for x in [x1_int, x2_int]:
                y = m * x + b
                if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
                    points.append((x, y))
            return points

    def is_point_on_line_segment(self, x, y, x1, y1, x2, y2):
        """点が線分上にあるかどうかを判定する"""
        # 点が直線上にあり、かつ線分の端点の間にあるかを確認
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            # 線分の長さと、点から両端点までの距離の和を比較
            line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            dist_to_p1 = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
            dist_to_p2 = math.sqrt((x - x2) ** 2 + (y - y2) ** 2)
            return abs(line_length - (dist_to_p1 + dist_to_p2)) < 0.1
        return False

    def get_snap_point(self, x, y):
        """マウス位置に最も近いスナップポイントを返す"""
        if not self.snap_enabled:
            return (x, y)

        snap_distance = 10  # スナップする距離の閾値
        
        # 既存の図形の端点や交点を探す
        snap_points = []
        
        # 各図形の端点を追加
        for shape in self.shapes:
            if isinstance(shape, Line):
                if self.snap_types["endpoint"]:
                    snap_points.extend([(shape.x1, shape.y1), (shape.x2, shape.y2)])
                # 中点を追加
                if self.snap_types["midpoint"]:
                    mid_x = (shape.x1 + shape.x2) / 2
                    mid_y = (shape.y1 + shape.y2) / 2
                    snap_points.append((mid_x, mid_y))
            elif isinstance(shape, Rectangle):
                points = [
                    (shape.x1, shape.y1),  # 左上
                    (shape.x2, shape.y1),  # 右上
                    (shape.x2, shape.y2),  # 右下
                    (shape.x1, shape.y2)   # 左下
                ]
                if self.snap_types["endpoint"]:
                    snap_points.extend(points)
                # 各辺の中点を追加
                if self.snap_types["midpoint"]:
                    for i in range(4):
                        p1 = points[i]
                        p2 = points[(i + 1) % 4]
                        mid_x = (p1[0] + p2[0]) / 2
                        mid_y = (p1[1] + p2[1]) / 2
                        snap_points.append((mid_x, mid_y))
            elif isinstance(shape, Circle):
                if self.snap_types["endpoint"]:
                    snap_points.append((shape.center_x, shape.center_y))  # 中心点
            elif isinstance(shape, Polygon):
                if self.snap_types["endpoint"]:
                    snap_points.extend(shape.points)
                # 各辺の中点を追加
                if self.snap_types["midpoint"]:
                    for i in range(len(shape.points)):
                        p1 = shape.points[i]
                        p2 = shape.points[(i + 1) % len(shape.points)]
                        mid_x = (p1[0] + p2[0]) / 2
                        mid_y = (p1[1] + p2[1]) / 2
                        snap_points.append((mid_x, mid_y))

        # 図形同士の交点を追加
        if self.snap_types["intersection"]:
            for i, shape1 in enumerate(self.shapes):
                for shape2 in self.shapes[i+1:]:
                    intersections = self.get_intersection_points(shape1, shape2)
                    if intersections is not None:  # Noneチェックを追加
                        snap_points.extend(intersections)

        # 最も近いスナップポイントを探す
        closest_point = None
        min_distance = float('inf')
        
        for point in snap_points:
            distance = ((x - point[0]) ** 2 + (y - point[1]) ** 2) ** 0.5
            if distance < min_distance and distance <= snap_distance:
                min_distance = distance
                closest_point = point

        return closest_point if closest_point else (x, y)

    def get_intersection_points(self, shape1, shape2):
        """2つの図形の交点を計算する"""
        # 円と線分の交点を計算する場合
        if isinstance(shape1, Circle) and (isinstance(shape2, Line) or isinstance(shape2, Rectangle) or isinstance(shape2, Polygon)):
            lines = self.get_shape_lines(shape2)
            intersections = []
            for line in lines:
                line_obj = Line(line[0][0], line[0][1], line[1][0], line[1][1])
                points = self.get_circle_line_intersection(line_obj, shape1)
                intersections.extend(points)
            return intersections
            
        # 線分と円の交点を計算する場合（順序が逆の場合）
        if (isinstance(shape1, Line) or isinstance(shape1, Rectangle) or isinstance(shape1, Polygon)) and isinstance(shape2, Circle):
            return self.get_intersection_points(shape2, shape1)  # 順序を入れ替えて再帰的に呼び出し
            
        # 円同士の交点を計算する場合
        if isinstance(shape1, Circle) and isinstance(shape2, Circle):
            return self.get_circle_circle_intersection(shape1, shape2)

        # それ以外の場合（線分同士の交点）
        lines1 = self.get_shape_lines(shape1)
        lines2 = self.get_shape_lines(shape2)
        intersections = []

        logger.debug(f"図形1の線分: {lines1}")
        logger.debug(f"図形2の線分: {lines2}")

        for line1 in lines1:
            for line2 in lines2:
                intersection = self.get_line_line_intersection(line1, line2)
                logger.debug(f"線分1: {line1}, 線分2: {line2}, 交点: {intersection}")
                if intersection:
                    intersections.extend(intersection)

        logger.debug(f"見つかった交点: {intersections}")
        return intersections

    def get_line_line_intersection(self, line1, line2):
        """2つの線分の交点を計算する"""
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:  # 平行または重なっている
            return []
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
        
        if 0 <= t <= 1 and 0 <= u <= 1:  # 線分の範囲内で交差
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return [(x, y)]
        return []

    def get_circle_circle_intersection(self, circle1, circle2):
        """2つの円の交点を計算する"""
        # 円1の中心と半径
        x1, y1 = circle1.center_x, circle1.center_y
        r1 = circle1.radius
        
        # 円2の中心と半径
        x2, y2 = circle2.center_x, circle2.center_y
        r2 = circle2.radius
        
        # 中心間の距離
        d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        # 交点なしの場合
        if d > r1 + r2:  # 円が離れている
            return []
        if d < abs(r1 - r2):  # 一方が他方の内部にある
            return []
        if d == 0 and r1 == r2:  # 同じ円
            return []
            
        # 1点で接する場合
        if d == r1 + r2 or d == abs(r1 - r2):
            # 接点の座標を計算
            t = r1 / d
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return [(x, y)]
            
        # 2点で交わる場合
        # 余弦定理を使用して角度を計算
        a = math.acos((r1 * r1 + d * d - r2 * r2) / (2 * r1 * d))
        
        # 中心を結ぶ線分の角度
        base_angle = math.atan2(y2 - y1, x2 - x1)
        
        # 2つの交点の座標を計算
        x3 = x1 + r1 * math.cos(base_angle + a)
        y3 = y1 + r1 * math.sin(base_angle + a)
        x4 = x1 + r1 * math.cos(base_angle - a)
        y4 = y1 + r1 * math.sin(base_angle - a)
        
        return [(x3, y3), (x4, y4)]

    def get_shape_lines(self, shape):
        """図形を構成する線分のリストを取得"""
        points = shape.points
        lines = []
        
        if isinstance(shape, Line):
            lines.append((points[0], points[1]))
        elif isinstance(shape, Rectangle):
            # 四角形の4辺を追加（4つの点を使用）
            for i in range(4):
                p1 = points[i]
                p2 = points[(i + 1) % 4]  # 最後の点は最初の点と接続
                lines.append((p1, p2))
        elif isinstance(shape, Polygon):
            # 多角形の各辺を追加
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]  # 最後の点は最初の点と接続
                lines.append((p1, p2))
        
        return lines

    def show_snap_marker(self, x, y):
        """スナップマーカーを表示"""
        self.delete("snap_marker")
        if not self.snap_enabled:
            return

        snap_x, snap_y = self.get_snap_point(x, y)
        if (snap_x, snap_y) != (x, y):
            # 十字マーカーを描画
            size = 5
            self.create_line(snap_x - size, snap_y, snap_x + size, snap_y,
                           fill="red", tags="snap_marker")
            self.create_line(snap_x, snap_y - size, snap_x, snap_y + size,
                           fill="red", tags="snap_marker")
            
    def on_click(self, event):
        """マウスクリックイベントの処理"""
        x, y = event.x, event.y
        
        # スナップ位置を取得
        snap_x, snap_y = self.get_snap_point(x, y)
        
        # リサイズハンドルのチェック
        if self.selected_shapes and isinstance(self.selected_shapes[0], Rectangle):
            handle = self.get_resize_handle_at_point(x, y)
            if handle:
                self.is_resizing = True
                self.resize_handle = handle
                self.last_x = x
                self.last_y = y
                return

        if self.mode == "line":
            if not self.current_points:
                self.current_points = [(snap_x, snap_y)]
            else:
                x1, y1 = self.current_points[0]
                line = Line(x1, y1, snap_x, snap_y, self.current_color, self.current_width, self.current_style)
                self.shapes.append(line)
                
                # アンドゥスタックに操作を追加
                self.undo_stack.append({
                    "type": "add_shape",
                    "shape": line
                })
                
                # 新しい操作を追加したので、リドゥスタックをクリア
                self.redo_stack.clear()
                
                self.current_points = []
                self.redraw()
        
        elif self.mode == "rectangle":
            if not self.current_points:
                self.current_points = [(snap_x, snap_y)]
            else:
                x1, y1 = self.current_points[0]
                rect = Rectangle(x1, y1, snap_x, snap_y, self.current_color, self.current_width, self.current_style)
                self.shapes.append(rect)
                
                # アンドゥスタックに操作を追加
                self.undo_stack.append({
                    "type": "add_shape",
                    "shape": rect
                })
                
                # 新しい操作を追加したので、リドゥスタックをクリア
                self.redo_stack.clear()
                
                self.current_points = []
                self.redraw()
        elif self.mode == "circle":
            if not self.current_points:
                self.current_points = [(snap_x, snap_y)]
            else:
                x1, y1 = self.current_points[0]
                circle = Circle(x1, y1, snap_x, snap_y, self.current_color, self.current_width, self.current_style)
                self.shapes.append(circle)
                
                # アンドゥスタックに操作を追加
                self.undo_stack.append({
                    "type": "add_shape",
                    "shape": circle
                })
                
                # 新しい操作を追加したので、リドゥスタックをクリア
                self.redo_stack.clear()
                
                self.current_points = []
                self.redraw()
        elif self.mode == "polygon":
            self.current_points.append((snap_x, snap_y))
            self.redraw()
            self.update_preview(x, y)
            
    def on_right_click(self, event):
        """右クリックイベントの処理（多角形の完成）"""
        if self.mode == "polygon" and len(self.current_points) >= 3:
            # 多角形を完成させる（最初の点は追加しない）
            self.complete_shape()
            
    def on_motion(self, event):
        """マウス移動イベントの処理"""
        # スナップマーカーの表示
        self.show_snap_marker(event.x, event.y)
        
        if len(self.current_points) > 0:
            # 現在の点を一時的に保存
            snap_x, snap_y = self.get_snap_point(event.x, event.y)
            temp_point = (snap_x, snap_y)
            
            if self.mode in ["line", "rectangle", "circle"]:
                # 2点目として扱う
                if len(self.current_points) == 1:
                    self.current_points.append(temp_point)
                    self.update_preview(event.x, event.y)
                    self.current_points.pop()  # 一時的な点を削除
            elif self.mode == "polygon":
                # 次の頂点候補として扱う
                self.current_points.append(temp_point)
                self.update_preview(event.x, event.y)
                self.current_points.pop()  # 一時的な点を削除
                
    def on_escape(self, event):
        """Escキーイベントの処理"""
        self.current_points = []
        self.update_preview()
        
    def complete_shape(self):
        """図形を完成させる"""
        if not self.current_points:
            return

        shape = None
        
        if self.mode == "line" and len(self.current_points) == 2:
            x1, y1 = self.current_points[0]
            x2, y2 = self.current_points[1]
            shape = Line(x1, y1, x2, y2, self.current_color, self.current_width, self.current_style)
            self.shapes.append(shape)
        elif self.mode == "rectangle" and len(self.current_points) == 2:
            x1, y1 = self.current_points[0]
            x2, y2 = self.current_points[1]
            shape = Rectangle(x1, y1, x2, y2, self.current_color, self.current_width, self.current_style)
            self.shapes.append(shape)
        elif self.mode == "circle" and len(self.current_points) == 2:
            center_x, center_y = self.current_points[0]
            x2, y2 = self.current_points[1]
            shape = Circle(center_x, center_y, x2, y2, self.current_color, self.current_width, self.current_style)
            self.shapes.append(shape)
        elif self.mode == "polygon" and len(self.current_points) >= 3:
            shape = Polygon(self.current_points, self.current_color, self.current_width, self.current_style)
            self.shapes.append(shape)

        # アンドゥスタックに操作を追加
        if shape:
            self.undo_stack.append({
                "type": "add_shape",
                "shape": shape
            })
            
            # 新しい操作を追加したので、リドゥスタックをクリア
            self.redo_stack.clear()
            
            logger.debug(f"{self.mode}を作成してundo_stackに追加")

        self.current_points = []
        self.delete("preview")  # プレビューを明示的に削除
        self.redraw()
        
    def update_preview(self, mouse_x=None, mouse_y=None):
        """プレビューの更新"""
        self.delete("preview")
        if len(self.current_points) < 1:
            return
            
        style = {
            "width": self.current_width,
            "tags": "preview"
        }
        
        if self.current_style is not None:
            style["dash"] = self.current_style
            
        if self.mode == "line":
            if len(self.current_points) == 2:
                x1, y1 = self.current_points[0]
                x2, y2 = self.current_points[1]
                style["fill"] = self.current_color
                self.create_line(x1, y1, x2, y2, **style)
        elif self.mode == "rectangle":
            if len(self.current_points) == 2:
                x1, y1 = self.current_points[0]
                x2, y2 = self.current_points[1]
                style["outline"] = self.current_color
                style["fill"] = ""
                self.create_rectangle(x1, y1, x2, y2, **style)
        elif self.mode == "circle":
            if len(self.current_points) == 2:
                x1, y1 = self.current_points[0]  # 中心点
                x2, y2 = self.current_points[1]  # 半径を決める点
                radius = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                style["outline"] = self.current_color
                style["fill"] = ""
                self.create_oval(x1 - radius, y1 - radius,
                               x1 + radius, y1 + radius, **style)
        elif self.mode == "polygon":
            style["fill"] = self.current_color
            
            # 1. 既存の点を結ぶ線を描画（2点以上ある場合のみ）
            if len(self.current_points) >= 2:
                for i in range(len(self.current_points) - 1):
                    x1, y1 = self.current_points[i]
                    x2, y2 = self.current_points[i + 1]
                    self.create_line(x1, y1, x2, y2, **style)
            
            # 2. 最後の点からマウス位置までの線を描画（1点以上ある場合）
            if len(self.current_points) >= 1 and mouse_x is not None and mouse_y is not None:
                last_x, last_y = self.current_points[-1]
                temp_style = style.copy()
                self.create_line(last_x, last_y, mouse_x, mouse_y, **temp_style)
            
            # 3. 閉じる線を描画（3点以上ある場合のみ）
            if len(self.current_points) >= 3 and mouse_x is not None and mouse_y is not None:
                first_x, first_y = self.current_points[0]
                if len(self.current_points) > 3 or (
                    len(self.current_points) == 3 and 
                    (mouse_x != self.current_points[-1][0] or mouse_y != self.current_points[-1][1])
                ):
                    dash_style = style.copy()
                    dash_style["dash"] = (4, 4)
                    self.create_line(mouse_x, mouse_y, first_x, first_y, **dash_style)
                
    def redraw(self):
        """キャンバスの再描画"""
        self.delete("all")
        
        # 完成した図形を描画
        for shape in self.shapes:
            shape.draw(self)
        
        # 選択された図形のハイライト表示
        if self.selected_shapes:
            for shape in self.selected_shapes:
                shape.draw_selected(self)
            
        # プレビューの更新
        self.update_preview()

    def on_select(self, event):
        """図形の選択処理"""
        x, y = event.x, event.y
        logger.debug(f"選択処理開始: クリック位置 ({x}, {y})")
        
        # 既存の選択を解除
        old_selected = self.selected_shapes
        self.selected_shapes = []
        self.selected_endpoint = None  # 端点選択も解除
        
        # クリックされた位置にある図形を探す
        for shape in reversed(self.shapes):
            if isinstance(shape, Rectangle):
                # 矩形の辺上のクリックを検出
                x1, y1 = shape.x1, shape.y1
                x2, y2 = shape.x2, shape.y2
                
                # 各辺との距離を計算
                distances = [
                    self.distance_to_line((x, y), (x1, y1), (x2, y1)),  # 上辺
                    self.distance_to_line((x, y), (x2, y1), (x2, y2)),  # 右辺
                    self.distance_to_line((x, y), (x2, y2), (x1, y2)),  # 下辺
                    self.distance_to_line((x, y), (x1, y2), (x1, y1))   # 左辺
                ]
                
                # いずれかの辺との距離が閾値以下なら選択
                min_distance = min(distances)
                if min_distance < 5:  # 5ピクセル以内なら選択
                    self.selected_shapes.append(shape)
                    logger.debug(f"矩形を選択: 最小距離 = {min_distance:.2f}px")
                    logger.debug(f"矩形の座標: ({x1}, {y1}) - ({x2}, {y2})")
                    break
            elif isinstance(shape, Line):
                # 端点の選択をチェック
                if abs(x - shape.x1) < 5 and abs(y - shape.y1) < 5:  # 始点
                    self.selected_shapes.append(shape)
                    self.selected_endpoint = 0
                    break
                elif abs(x - shape.x2) < 5 and abs(y - shape.y2) < 5:  # 終点
                    self.selected_shapes.append(shape)
                    self.selected_endpoint = 1
                    break
                # 線分との距離が一定以下なら選択
                d = self.distance_to_line((x, y), (shape.x1, shape.y1), (shape.x2, shape.y2))
                if d < 5:  # 5ピクセル以内なら選択
                    self.selected_shapes.append(shape)
                    break
            elif isinstance(shape, Circle):
                # 円の中心からの距離が半径以下なら選択
                center_x, center_y = shape.center_x, shape.center_y
                radius = math.sqrt((shape.x2 - center_x)**2 + (shape.y2 - center_y)**2)
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if distance <= radius:
                    self.selected_shapes.append(shape)
                    break
        
        # 選択状態の変化をログ出力
        if old_selected != self.selected_shapes:
            if not self.selected_shapes:
                logger.debug("図形の選択を解除")
            else:
                logger.debug(f"新しい図形を選択: {[type(shape).__name__ for shape in self.selected_shapes]}")
        
        self.redraw()
        self.update_selection_display()

    def on_drag(self, event):
        """ドラッグ時の処理"""
        if not self.selected_shapes:
            return
            
        # 現在のマウス位置
        x, y = event.x, event.y
        
        # 前回のマウス位置からの移動量を計算
        if self.last_x is not None and self.last_y is not None:
            dx = x - self.last_x
            dy = y - self.last_y
            
            if self.is_resizing and isinstance(self.selected_shapes[0], Rectangle):
                # リサイズ処理
                self.resize_shape(x, y)
            elif isinstance(self.selected_shapes[0], Line) and self.selected_endpoint is not None:
                # 線分の端点移動
                if self.selected_endpoint == 0:  # 始点
                    for shape in self.selected_shapes:
                        shape.x1 = x
                        shape.y1 = y
                else:  # 終点
                    for shape in self.selected_shapes:
                        shape.x2 = x
                        shape.y2 = y
                for shape in self.selected_shapes:
                    shape.points = [(shape.x1, shape.y1), (shape.x2, shape.y2)]
            else:
                # 移動処理
                self.move_shape(dx, dy)
        
        # 現在の位置を保存
        self.last_x = x
        self.last_y = y
        
        # キャンバスを更新
        self.redraw()
        self.update_selection_display()

    def on_release(self, event):
        """マウスボタン解放時の処理"""
        self.is_moving = False
        self.is_resizing = False
        self.resize_handle = None
        self.last_x = None
        self.last_y = None

    def on_move_start(self, event):
        """図形の移動開始時の処理"""
        if self.selected_shapes:
            self.is_moving = True
            self.last_x = event.x
            self.last_y = event.y

    def on_resize_start(self, event):
        """図形のリサイズ開始時の処理"""
        if not self.selected_shapes:
            return
        
        handle = self.get_resize_handle_at_point(event.x, event.y)
        if handle:
            self.is_resizing = True
            self.resize_handle = handle
            self.last_x = event.x
            self.last_y = event.y

    def get_resize_handle_at_point(self, x, y):
        """指定された座標にあるリサイズハンドルを取得"""
        if not self.selected_shapes:
            return None

        handles = self.get_resize_handles()
        for handle_name, (hx, hy) in handles.items():
            if abs(x - hx) <= 5 and abs(y - hy) <= 5:
                return handle_name
        return None

    def redraw_all_shapes(self):
        """全ての図形を再描画"""
        self.delete("shape")
        for shape in self.shapes:
            shape.draw(self)
        self.update_selection_display()

    def get_resize_handles(self):
        """選択された図形のリサイズハンドルの位置を取得"""
        if not self.selected_shapes:
            return {}
        
        if isinstance(self.selected_shapes[0], Rectangle):
            rect = self.selected_shapes[0]
            handles = {
                "nw": (rect.x1, rect.y1),  # 左上
                "n": (rect.x1 + (rect.x2 - rect.x1) / 2, rect.y1),  # 上中央
                "ne": (rect.x2, rect.y1),  # 右上
                "e": (rect.x2, rect.y1 + (rect.y2 - rect.y1) / 2),  # 右中央
                "se": (rect.x2, rect.y2),  # 右下
                "s": (rect.x1 + (rect.x2 - rect.x1) / 2, rect.y2),  # 下中央
                "sw": (rect.x1, rect.y2),  # 左下
                "w": (rect.x1, rect.y1 + (rect.y2 - rect.y1) / 2)   # 左中央
            }
            return handles
        return {}

    def draw_selection_outline(self):
        """選択された図形の周りに選択表示を描画"""
        if not self.selected_shapes:
            return
        
        for shape in self.selected_shapes:
            if isinstance(shape, Line):
                # 線分の端点に選択ハンドルを表示
                self.create_rectangle(
                    shape.x1 - 5, shape.y1 - 5,
                    shape.x1 + 5, shape.y1 + 5,
                    outline="blue", fill="white", tags="selection_outline"
                )
                self.create_rectangle(
                    shape.x2 - 5, shape.y2 - 5,
                    shape.x2 + 5, shape.y2 + 5,
                    outline="blue", fill="white", tags="selection_outline"
                )
                # 線分自体も強調表示
                self.create_line(
                    shape.x1, shape.y1,
                    shape.x2, shape.y2,
                    fill="blue", width=2, tags="selection_outline"
                )
            elif isinstance(shape, Rectangle):
                # 矩形の外枠を描画
                self.create_rectangle(
                    shape.x1 - 2, shape.y1 - 2,
                    shape.x2 + 2, shape.y2 + 2,
                    outline="blue", width=2, tags="selection_outline"
                )
                
                # 各辺を個別に強調表示（確実に描画されるように）
                # 上辺
                self.create_line(
                    shape.x1, shape.y1,
                    shape.x2, shape.y1,
                    fill="blue", width=2, tags="selection_outline"
                )
                # 右辺
                self.create_line(
                    shape.x2, shape.y1,
                    shape.x2, shape.y2,
                    fill="blue", width=2, tags="selection_outline"
                )
                # 下辺
                self.create_line(
                    shape.x2, shape.y2,
                    shape.x1, shape.y2,
                    fill="blue", width=2, tags="selection_outline"
                )
                # 左辺
                self.create_line(
                    shape.x1, shape.y2,
                    shape.x1, shape.y1,
                    fill="blue", width=2, tags="selection_outline"
                )
                
                # 各頂点にハンドルを表示
                corners = [
                    (shape.x1, shape.y1),  # 左上
                    (shape.x2, shape.y1),  # 右上
                    (shape.x2, shape.y2),  # 右下
                    (shape.x1, shape.y2)   # 左下
                ]
                for x, y in corners:
                    self.create_rectangle(
                        x - 5, y - 5,
                        x + 5, y + 5,
                        outline="blue", fill="white", tags="selection_outline"
                    )
                
                # 各辺の中点にハンドルを表示
                midpoints = [
                    ((shape.x1 + shape.x2) / 2, shape.y1),  # 上辺中点
                    ((shape.x1 + shape.x2) / 2, shape.y2),  # 下辺中点
                    (shape.x1, (shape.y1 + shape.y2) / 2),  # 左辺中点
                    (shape.x2, (shape.y1 + shape.y2) / 2)   # 右辺中点
                ]
                for x, y in midpoints:
                    self.create_rectangle(
                        x - 5, y - 5,
                        x + 5, y + 5,
                        outline="blue", fill="white", tags="selection_outline"
                    )
            elif isinstance(shape, Circle):
                # 円の外枠を描画
                radius = math.sqrt((shape.x2 - shape.center_x)**2 + 
                                 (shape.y2 - shape.center_y)**2)
                self.create_oval(
                    shape.center_x - radius - 2,
                    shape.center_y - radius - 2,
                    shape.center_x + radius + 2,
                    shape.center_y + radius + 2,
                    outline="blue", width=2, tags="selection_outline"
                )
                # 中心点と半径点にハンドルを表示
                self.create_rectangle(
                    shape.center_x - 5, shape.center_y - 5,
                    shape.center_x + 5, shape.center_y + 5,
                    outline="blue", fill="white", tags="selection_outline"
                )
                self.create_rectangle(
                    shape.x2 - 5, shape.y2 - 5,
                    shape.x2 + 5, shape.y2 + 5,
                    outline="blue", fill="white", tags="selection_outline"
                )
            elif isinstance(shape, Polygon):
                # 多角形の各頂点にハンドルを表示
                for x, y in shape.points:
                    self.create_rectangle(
                        x - 5, y - 5,
                        x + 5, y + 5,
                        outline="blue", fill="white", tags="selection_outline"
                    )
                # 多角形の辺を強調表示
                points = []
                for point in shape.points:
                    points.extend(point)
                if len(points) >= 4:
                    self.create_line(
                        *points,
                        fill="blue", width=2, tags="selection_outline"
                    )

    def update_selection_display(self):
        """選択表示を更新"""
        self.delete("selection_outline")
        self.delete("resize_handle")
        if self.selected_shapes:
            self.draw_selection_outline()
            self.draw_resize_handles()

    def draw_resize_handles(self):
        """リサイズハンドルを描画"""
        if not self.selected_shapes:
            return

        handles = self.get_resize_handles()
        for position, (x, y) in handles.items():
            self.create_rectangle(x - 5, y - 5, x + 5, y + 5,
                                fill="white", outline="blue",
                                tags="resize_handle")

    def distance_to_line(self, point, line_start, line_end):
        """点と線分との距離を計算"""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # 線分の長さの2乗
        l2 = (x2 - x1)**2 + (y2 - y1)**2
        if l2 == 0:
            return math.sqrt((x - x1)**2 + (y - y1)**2)
        
        # 点と線分の最短距離を計算
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / l2))
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        return math.sqrt((x - px)**2 + (y - py)**2)

    def move_shape(self, dx, dy):
        """図形を移動"""
        if not self.selected_shapes:
            return
        
        if isinstance(self.selected_shapes[0], Rectangle):
            for shape in self.selected_shapes:
                shape.x1 += dx
                shape.y1 += dy
                shape.x2 += dx
                shape.y2 += dy
                # 点のリストも更新
                shape.points = [
                    (shape.x1, shape.y1),
                    (shape.x2, shape.y1),
                    (shape.x2, shape.y2),
                    (shape.x1, shape.y2)
                ]
        elif isinstance(self.selected_shapes[0], Line):
            for shape in self.selected_shapes:
                shape.x1 += dx
                shape.y1 += dy
                shape.x2 += dx
                shape.y2 += dy
                # 点のリストも更新
                shape.points = [
                    (shape.x1, shape.y1),
                    (shape.x2, shape.y2)
                ]
        elif isinstance(self.selected_shapes[0], Circle):
            for shape in self.selected_shapes:
                shape.center_x += dx
                shape.center_y += dy
                shape.x2 += dx
                shape.y2 += dy
                # 点のリストも更新
                shape.points = [
                    (shape.center_x, shape.center_y),
                    (shape.x2, shape.y2)
                ]
        elif isinstance(self.selected_shapes[0], Polygon):
            # 全ての頂点を移動
            for shape in self.selected_shapes:
                shape.points = [
                    (x + dx, y + dy) for x, y in shape.points
                ]
        
        self.redraw()

    def resize_shape(self, x, y):
        """図形のサイズを変更"""
        if not self.selected_shapes:
            return
        
        # 現在の座標を保存
        old_x1 = self.selected_shapes[0].x1
        old_y1 = self.selected_shapes[0].y1
        old_x2 = self.selected_shapes[0].x2
        old_y2 = self.selected_shapes[0].y2
        
        # スナップ位置を取得
        snap_x, snap_y = self.get_snap_point(x, y)
        
        # ハンドル名に応じて対応する座標のみを更新
        if "n" in self.resize_handle:
            for shape in self.selected_shapes:
                shape.y1 = snap_y
        if "s" in self.resize_handle:
            for shape in self.selected_shapes:
                shape.y2 = snap_y
        if "w" in self.resize_handle:
            for shape in self.selected_shapes:
                shape.x1 = snap_x
        if "e" in self.resize_handle:
            for shape in self.selected_shapes:
                shape.x2 = snap_x
            
        # 最小サイズの制約を適用
        width = abs(self.selected_shapes[0].x2 - self.selected_shapes[0].x1)
        height = abs(self.selected_shapes[0].y2 - self.selected_shapes[0].y1)
        
        if width < self.MIN_SIZE or height < self.MIN_SIZE:
            # 制約を満たさない場合は元のサイズに戻す
            for shape in self.selected_shapes:
                shape.x1 = old_x1
                shape.y1 = old_y1
                shape.x2 = old_x2
                shape.y2 = old_y2
            return
            
        # 点のリストを更新
        for shape in self.selected_shapes:
            shape.points = [
                (shape.x1, shape.y1),
                (shape.x2, shape.y1),
                (shape.x2, shape.y2),
                (shape.x1, shape.y2)
            ]
        
        self.redraw()
        self.update_selection_display()

    def undo(self):
        """最後の操作を元に戻す"""
        if not self.undo_stack:
            logger.debug("元に戻す操作がありません")
            return
            
        # スタックから最後の操作を取得
        operation = self.undo_stack.pop()
        
        # 操作をリドゥスタックに追加
        self.redo_stack.append(operation)
        
        # 操作を元に戻す
        logger.debug(f"操作を元に戻す: {operation['type']}")
        
        if operation["type"] == "add_shape":
            # 図形の追加を元に戻す（図形を削除）
            shape = operation["shape"]
            self.shapes.remove(shape)
        elif operation["type"] == "delete_shape":
            # 図形の削除を元に戻す（図形を復元）
            shape = operation["shape"]
            self.shapes.append(shape)
        elif operation["type"] == "delete_shapes":
            # 複数図形の削除を元に戻す（すべて復元）
            for i, shape in zip(operation["indices"], operation["shapes"]):
                if i < len(self.shapes):
                    self.shapes.insert(i, shape)
                else:
                    self.shapes.append(shape)
            logger.debug(f"{len(operation['shapes'])}個の図形を復元しました")
        elif operation["type"] == "move_shape":
            # 図形の移動を元に戻す
            shape = operation["shape"]
            dx = operation["original_position"]["x1"] - shape.x1
            dy = operation["original_position"]["y1"] - shape.y1
            self.move_shape_by(shape, dx, dy)
        elif operation["type"] == "resize_shape":
            # 図形のリサイズを元に戻す
            shape = operation["shape"]
            shape.x1 = operation["original_position"]["x1"]
            shape.y1 = operation["original_position"]["y1"]
            shape.x2 = operation["original_position"]["x2"]
            shape.y2 = operation["original_position"]["y2"]
            if hasattr(shape, "points"):
                shape.points = [
                    (shape.x1, shape.y1),
                    (shape.x2, shape.y1),
                    (shape.x2, shape.y2),
                    (shape.x1, shape.y2)
                ]
        elif operation["type"] == "change_property":
            # プロパティの変更を元に戻す
            setattr(self, operation["property"], operation["old_value"])
        
        # キャンバスを更新
        self.redraw()

    def redo(self):
        """取り消した操作をやり直す"""
        if not self.redo_stack:
            logger.debug("やり直す操作がありません")
            return
            
        # リドゥスタックから操作を取得
        operation = self.redo_stack.pop()
        
        # 操作をアンドゥスタックに追加
        self.undo_stack.append(operation)
        
        # 操作をやり直す
        logger.debug(f"操作をやり直す: {operation['type']}")
        
        if operation["type"] == "add_shape":
            # 図形の追加をやり直す
            shape = operation["shape"]
            self.shapes.append(shape)
        elif operation["type"] == "delete_shape":
            # 図形の削除をやり直す
            shape = operation["shape"]
            self.shapes.remove(shape)
        elif operation["type"] == "delete_shapes":
            # 複数図形の削除をやり直す
            for shape in operation["shapes"]:
                if shape in self.shapes:
                    self.shapes.remove(shape)
            logger.debug(f"{len(operation['shapes'])}個の図形を削除しました")
        elif operation["type"] == "move_shape":
            # 図形の移動をやり直す
            shape = operation["shape"]
            dx = operation["new_position"]["x1"] - shape.x1
            dy = operation["new_position"]["y1"] - shape.y1
            self.move_shape_by(shape, dx, dy)
        elif operation["type"] == "resize_shape":
            # 図形のリサイズをやり直す
            shape = operation["shape"]
            shape.x1 = operation["new_position"]["x1"]
            shape.y1 = operation["new_position"]["y1"]
            shape.x2 = operation["new_position"]["x2"]
            shape.y2 = operation["new_position"]["y2"]
            if hasattr(shape, "points"):
                shape.points = [
                    (shape.x1, shape.y1),
                    (shape.x2, shape.y1),
                    (shape.x2, shape.y2),
                    (shape.x1, shape.y2)
                ]
        elif operation["type"] == "change_property":
            # プロパティの変更をやり直す
            setattr(self, operation["property"], operation["new_value"])
        
        # キャンバスを更新
        self.redraw()

    def push_state(self):
        """現在の状態を保存する（属性変更時に使用）"""
        logger.debug("現在の状態を保存")
        
        # このメソッドは一般的に属性変更の後に呼ばれる
        # 例: color変更後、width変更後、style変更後など
        # 呼び出し箇所で対象の属性と新旧の値を設定する必要がある
        
        # アンドゥスタックをクリアするだけで実際の保存は呼び出し側で行う
        # リドゥスタックをクリア
        self.redo_stack.clear()
        
    def push_property_change(self, property_name, old_value, new_value):
        """属性変更を記録する"""
        logger.debug(f"属性変更を記録: {property_name} = {old_value} -> {new_value}")
        
        # プロパティの変更を記録
        self.undo_stack.append({
            "type": "change_property",
            "property": property_name,
            "old_value": old_value,
            "new_value": new_value
        })
        
        # 新しい操作を記録したので、リドゥスタックをクリア
        self.redo_stack.clear()

    def move_shape_by(self, shape, dx, dy):
        """図形を指定した量だけ移動する（アンドゥ/リドゥ用）"""
        if isinstance(shape, Rectangle):
            shape.x1 += dx
            shape.y1 += dy
            shape.x2 += dx
            shape.y2 += dy
            shape.points = [
                (shape.x1, shape.y1),
                (shape.x2, shape.y1),
                (shape.x2, shape.y2),
                (shape.x1, shape.y2)
            ]
        elif isinstance(shape, Line):
            shape.x1 += dx
            shape.y1 += dy
            shape.x2 += dx
            shape.y2 += dy
            shape.points = [(shape.x1, shape.y1), (shape.x2, shape.y2)]
        elif isinstance(shape, Circle):
            shape.center_x += dx
            shape.center_y += dy
            shape.x2 += dx
            shape.y2 += dy
            shape.points = [(shape.center_x, shape.center_y), (shape.x2, shape.y2)]
        elif isinstance(shape, Polygon):
            shape.points = [(x + dx, y + dy) for x, y in shape.points]
        
        self.redraw()

    def handle_keyboard_event(self, event):
        """キーボードイベント処理
        
        Ctrl+Z: アンドゥ
        Ctrl+Y: リドゥ
        Delete: 選択図形の削除
        Ctrl+A: 全選択
        
        Parameters
        ----------
        event : Event
            キーボードイベント情報を含むイベントオブジェクト
            
        Returns
        -------
        str
            "break"を返して、イベント処理を停止します
        """
        try:
            logger.debug(f"キーボードイベント: {event.keysym}, state={event.state}")
            logger.info(f"キーボードイベント受信: {event.keysym}, state={event.state:x}")
            
            # フォーカスを確保
            self.ensure_focus()
            
            # Ctrlキーが押されているかどうか
            ctrl_pressed = (event.state & 0x4) != 0
            
            if ctrl_pressed and event.keysym.lower() == 'z':
                # Ctrl+Z: アンドゥ
                logger.info("アンドゥ操作を実行")
                self.undo()
                return "break"  # イベント伝播を停止
            elif ctrl_pressed and event.keysym.lower() == 'y':
                # Ctrl+Y: リドゥ
                logger.info("リドゥ操作を実行")
                self.redo()
                return "break"
            elif ctrl_pressed and event.keysym.lower() == 'a':
                # Ctrl+A: 全選択
                logger.info("全選択操作を実行")
                self.select_all()
                return "break"
            elif ctrl_pressed and event.keysym.lower() == 'd':
                # Ctrl+D: 図形の複製
                logger.info("複製操作を実行")
                self.duplicate_selected()
                return "break"
            elif event.keysym == 'Delete':
                # Delete: 選択図形の削除
                logger.info("選択図形を削除")
                self.delete_selected()
                return "break"
        except Exception as e:
            logger.error(f"キーボードイベント処理中にエラーが発生しました: {str(e)}", exc_info=True)
        
        return None  # 他のハンドラにイベントを伝播

    def ensure_focus(self):
        """キャンバスが確実にフォーカスを持つようにする
        
        キーボードイベントを処理するために、キャンバスがフォーカスを持っていることを
        確認します。フォーカスがない場合は取得を試みます。
        
        Returns
        -------
        bool
            フォーカスの取得に成功したかどうか
        """
        if self.focus_get() != self:
            self.focus_set()
            logger.debug("キャンバスにフォーカスを設定しました")
        return self.focus_get() == self

    def duplicate_selected(self):
        """選択された図形を複製する
        
        選択された図形を複製し、複製された図形を元の図形より20pxずつ右下にオフセットして配置します。
        複製後は、複製された図形が選択状態になります。
        """
        if not self.selected_shapes:
            logger.info("複製する図形がありません")
            return
            
        # 選択された図形のリスト
        selected = self.selected_shapes.copy()
        
        # 状態を保存
        self.push_state()
        
        # 新しく複製された図形のリスト
        new_shapes = []
        
        # 各図形を複製
        for shape in selected:
            # 図形のタイプに応じた複製処理
            if isinstance(shape, Rectangle):
                # 四角形の複製
                new_shape = Rectangle(
                    shape.x1 + 20, shape.y1 + 20,
                    shape.x2 + 20, shape.y2 + 20,
                    shape.color, shape.width, shape.style
                )
            elif isinstance(shape, Line):
                # 線の複製
                new_shape = Line(
                    shape.x1 + 20, shape.y1 + 20,
                    shape.x2 + 20, shape.y2 + 20,
                    shape.color, shape.width, shape.style
                )
            elif isinstance(shape, Circle):
                # 円の複製
                new_shape = Circle(
                    shape.center_x + 20, shape.center_y + 20,
                    shape.center_x + 20 + shape.radius, shape.center_y + 20,
                    shape.color, shape.width, shape.style
                )
            elif isinstance(shape, Polygon):
                # 多角形の複製
                new_points = [(x + 20, y + 20) for x, y in shape.points]
                new_shape = Polygon(new_points, shape.color, shape.width, shape.style)
            else:
                logger.warning(f"未対応の図形タイプ: {type(shape)}")
                continue
                
            # 新しい図形をリストに追加
            new_shapes.append(new_shape)
            self.shapes.append(new_shape)
            
        # 元の図形の選択状態を解除
        for shape in selected:
            if shape in self.selected_shapes:
                self.selected_shapes.remove(shape)
                
        # 複製された図形を選択状態にする
        self.selected_shapes = new_shapes
        
        # 再描画
        self.redraw()
        logger.info(f"{len(new_shapes)}個の図形を複製しました")
            
    def delete_selected(self):
        """選択された図形をすべて削除する
        
        現在選択されている図形をすべて削除します。
        複数の図形が選択されている場合はすべて削除されます。
        削除操作はアンドゥスタックに記録され、後で取り消すことができます。
        """
        if not self.selected_shapes:
            logger.debug("削除対象の図形が選択されていません")
            return
            
        # 削除前に操作を記録
        deleted_shapes = self.selected_shapes.copy()
        deleted_indices = [self.shapes.index(shape) for shape in deleted_shapes]
        
        self.undo_stack.append({
            "type": "delete_shapes",
            "shapes": deleted_shapes,
            "indices": deleted_indices
        })
        
        # 図形を削除
        for shape in deleted_shapes:
            if shape in self.shapes:  # 念のためチェック
                self.shapes.remove(shape)
        
        # 選択をクリア
        self.selected_shapes = []
        
        # 新しい操作を記録したので、リドゥスタックをクリア
        self.redo_stack.clear()
        
        # キャンバスを更新
        self.redraw()
        logger.info(f"{len(deleted_shapes)}個の図形を削除しました")
        
    def select_all(self):
        """すべての図形を選択する
        
        キャンバス上のすべての図形を選択状態にします。
        これにより、削除や移動などの操作をまとめて行うことができます。
        """
        if not self.shapes:
            logger.debug("選択可能な図形がありません")
            return
            
        # 現在の選択状態を解除
        for shape in self.selected_shapes:
            shape.is_selected = False
        self.selected_shapes = []
        
        # すべての図形を選択
        self.selected_shapes = self.shapes.copy()
        for shape in self.shapes:
            shape.is_selected = True
        
        # キャンバスを更新
        self.redraw()
        logger.info(f"すべての図形を選択しました（{len(self.shapes)}個）")

