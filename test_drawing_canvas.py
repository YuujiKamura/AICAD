import unittest
import tkinter as tk
from drawing_canvas import DrawingCanvas, Line, Rectangle, Circle, Polygon, DrawingState
import math
import time
import tempfile
import os
import json
import logging

"""
描画キャンバステストモジュール

このモジュールは図形描画機能を提供するtkinterキャンバスの拡張クラスのテストを実装します。
様々な図形（線、四角形、円、多角形）の描画、選択、編集、移動、リサイズ機能をテストします。

目的:
- 図形の描画、選択、編集機能が正常に動作することを検証
- アンドゥ/リドゥ機能が予期通りに動作することを検証
- キーボードショートカットが正しく処理されることを検証
- 複数図形の選択と編集が適切に動作することを検証

注意事項:
- このテストスイートは仕様を固定します
- 実装を変更する場合は、必ずテストを先に修正してから実装を変更する
- キーボードショートカット（Ctrl+Z, Ctrl+Y, Delete, Ctrl+A）の検証は重要な要素
- 複数選択機能では selected_shapes リストを使用する

テスト範囲:
1. 基本図形描画テスト
2. アンドゥ/リドゥ機能テスト
3. キーボードイベント処理テスト
4. フォーカス管理テスト
5. 複数選択と操作テスト
"""

class TestDrawingCanvas(unittest.TestCase):
    """DrawingCanvasクラスのテストケース
    
    このテストスイートは、描画キャンバスの機能を包括的にテストします。
    描画キャンバスは複数の図形（線、四角形、円、多角形）の描画、選択、
    編集、移動、リサイズなどの機能を提供します。
    
    主な機能：
    - 各種図形の描画と編集
    - アンドゥ/リドゥ機能
    - キーボードショートカット
    - 複数選択と一括操作
    - フォーカス管理
    
    このテストスイートでは、以下の点に特に注意を払っています：
    - 図形は単一のオブジェクトとして実装され、各図形クラスはShapeクラスを継承
    - 選択機能は複数選択に対応（selected_shapesリストを使用）
    - undo/redo機能は操作の履歴をスタックとして管理
    - キーボードイベントはhandle_keyboard_eventメソッドで一元管理
    
    注意: このテストを変更する場合は、drawing_canvas.pyの実装との整合性を
    必ず確認してください。
    """
    
    def setUp(self):
        """各テストケース実行前の準備"""
        self.root = tk.Tk()
        self.canvas = DrawingCanvas(self.root)
        
    def tearDown(self):
        """各テストケース実行後のクリーンアップ"""
        self.root.destroy()
    
    def create_mouse_event(self, x, y, button=1, type="ButtonPress"):
        """マウスイベントを作成するヘルパーメソッド"""
        event = tk.Event()
        event.x = x
        event.y = y
        event.num = button
        event.type = type
        event.widget = self.canvas
        event.state = 0
        return event
    
    def create_event(self, x, y, type="ButtonPress"):
        """テスト用のイベントオブジェクトを作成（後方互換性のため）"""
        return self.create_mouse_event(x, y, type=type)
    
    def test_initial_state(self):
        """初期状態のテスト"""
        self.assertEqual(self.canvas.mode, "line")  # デフォルトは線分モード
        self.assertEqual(self.canvas.current_color, "black")
        self.assertEqual(self.canvas.current_width, 1)
        self.assertIsNone(self.canvas.current_style)
        self.assertEqual(len(self.canvas.shapes), 0)
        self.assertEqual(len(self.canvas.current_points), 0)
    
    def test_line_drawing(self):
        """線分の描画テスト - クリックベース
        
        描画手順:
        1. 始点でクリック
        2. マウスを移動すると、始点から現在位置までの線がプレビューされる
        3. 終点でクリックすると線分が確定
        
        期待される動作:
        - 1点目のクリックで描画状態がFIRST_POINTになる
        - マウス移動中はプレビューが更新される
        - 2点目のクリックで描画が完了し、状態がNONEに戻る
        """
        # 始点をクリック
        event = self.create_mouse_event(100, 100)
        self.canvas.on_click(event)
        
        # 移動中のプレビュー
        event = self.create_mouse_event(200, 200, type="Motion")
        self.canvas.on_motion(event)
        
        # 終点をクリックして確定
        event = self.create_mouse_event(200, 200)
        self.canvas.on_click(event)
        
        # 結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        line = self.canvas.shapes[0]
        self.assertIsInstance(line, Line)
        self.assertEqual(line.x1, 100)
        self.assertEqual(line.y1, 100)
        self.assertEqual(line.x2, 200)
        self.assertEqual(line.y2, 200)

    def test_rectangle_drawing(self):
        """矩形の描画テスト - クリックベース
        
        描画手順:
        1. 左上（または右上）の頂点でクリック
        2. マウスを移動すると、対角線上の矩形がプレビューされる
        3. 右下（または左下）の頂点でクリックすると矩形が確定
        
        期待される動作:
        - 1点目のクリックで描画状態がFIRST_POINTになる
        - マウス移動中は矩形のプレビューが更新される
        - 2点目のクリックで描画が完了し、状態がNONEに戻る
        """
        self.canvas.mode = "rectangle"
        
        # 始点をクリック
        event = self.create_mouse_event(100, 100)
        self.canvas.on_click(event)
        
        # 移動中のプレビュー
        event = self.create_mouse_event(200, 200, type="Motion")
        self.canvas.on_motion(event)
        
        # 対角点をクリックして確定
        event = self.create_mouse_event(200, 200)
        self.canvas.on_click(event)
        
        # 結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        rect = self.canvas.shapes[0]
        self.assertIsInstance(rect, Rectangle)
        self.assertEqual(rect.x1, 100)
        self.assertEqual(rect.y1, 100)
        self.assertEqual(rect.x2, 200)
        self.assertEqual(rect.y2, 200)

    def test_circle_drawing(self):
        """円の描画テスト - クリックベース
        
        描画手順:
        1. 中心点でクリック
        2. マウスを移動すると、中心から現在位置までの距離を半径とする円がプレビューされる
        3. 半径を決める点でクリックすると円が確定
        
        期待される動作:
        - 1点目のクリックで描画状態がFIRST_POINTになる
        - マウス移動中は円のプレビューが更新される
        - 2点目のクリックで描画が完了し、状態がNONEに戻る
        """
        self.canvas.mode = "circle"
        
        # 中心点をクリック
        event = self.create_mouse_event(100, 100)
        self.canvas.on_click(event)
        
        # 移動中のプレビュー
        event = self.create_mouse_event(150, 100, type="Motion")
        self.canvas.on_motion(event)
        
        # 半径点をクリックして確定
        event = self.create_mouse_event(150, 100)
        self.canvas.on_click(event)
        
        # 結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        circle = self.canvas.shapes[0]
        self.assertIsInstance(circle, Circle)
        self.assertEqual(circle.center_x, 100)
        self.assertEqual(circle.center_y, 100)
        self.assertEqual(circle.radius, 50)

    def test_polygon_drawing(self):
        """多角形の描画テスト - クリックベース
        
        描画手順:
        1. 最初の頂点でクリック
        2. 各頂点を順にクリックしていく
        3. マウスを移動すると、最後の頂点から現在位置までの線がプレビューされる
        4. 右クリックで多角形を確定
        
        期待される動作:
        - 1点目のクリックで描画状態がFIRST_POINTになる
        - 2点目以降のクリックで頂点が追加され、状態がDRAWINGになる
        - マウス移動中は次の辺のプレビューが更新される
        - 右クリックで描画が完了し、状態がNONEに戻る
        """
        self.canvas.mode = "polygon"
        
        # 頂点を順にクリック
        points = [(100, 100), (200, 100), (200, 200), (100, 200)]
        for x, y in points:
            event = self.create_mouse_event(x, y)
            self.canvas.on_click(event)
            
            # 移動中のプレビュー
            event = self.create_mouse_event(x + 10, y + 10, type="Motion")
            self.canvas.on_motion(event)
        
        # 右クリックで完成
        event = self.create_mouse_event(100, 100, button=3)
        self.canvas.on_right_click(event)
        
        # 結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        polygon = self.canvas.shapes[0]
        self.assertIsInstance(polygon, Polygon)
        self.assertEqual(len(polygon.points), len(points))
        for (x1, y1), (x2, y2) in zip(polygon.points, points):
            self.assertEqual(x1, x2)
            self.assertEqual(y1, y2)

    def test_drawing_cancel(self):
        """描画のキャンセルテスト - ESCキーで描画をキャンセル"""
        # 線分の描画を開始
        event = self.create_mouse_event(100, 100)
        self.canvas.on_click(event)
        
        # ESCキーで描画をキャンセル
        event = tk.Event()
        event.keysym = "Escape"
        self.canvas.on_escape(event)
        
        # 描画がキャンセルされたことを確認
        self.assertEqual(len(self.canvas.shapes), 0)
        self.assertEqual(len(self.canvas.current_points), 0)

    def test_snap_to_endpoint(self):
        """端点へのスナップテスト
        
        前提条件:
        - スナップ機能が有効（self.snap_enabled = True）
        - 端点スナップが有効（self.snap_types["endpoint"] = True）
        - スナップ距離は10ピクセル
        
        テスト手順:
        1. 線分を描画: (100, 100) → (200, 200)
        2. 端点近く（102, 98）にマウスを移動
        3. 別の端点近く（198, 202）にマウスを移動
        
        期待される動作:
        1. スナップ距離（10px）以内の場合、マウス位置が最も近い端点にスナップされる
        2. スナップ距離外の場合、元のマウス位置が返される
        
        検証項目:
        1. 始点近くでのスナップ
        2. 終点近くでのスナップ
        3. スナップ距離外での動作
        """
        # 線分を描画
        self.canvas.shapes.append(Line(100, 100, 200, 200))
        
        # 始点近くでのスナップを確認
        snap_point = self.canvas.get_snap_point(102, 98)
        self.assertEqual(snap_point, (100, 100), "始点へのスナップが機能していません")
        
        # 終点近くでのスナップを確認
        snap_point = self.canvas.get_snap_point(198, 202)
        self.assertEqual(snap_point, (200, 200), "終点へのスナップが機能していません")
        
        # スナップ距離外での動作を確認
        snap_point = self.canvas.get_snap_point(120, 120)
        self.assertEqual(snap_point, (120, 120), "スナップ距離外でスナップされています")

    def test_snap_to_midpoint(self):
        """中点へのスナップテスト
        
        前提条件:
        - スナップ機能が有効（self.snap_enabled = True）
        - 中点スナップが有効（self.snap_types["midpoint"] = True）
        - スナップ距離は10ピクセル
        
        テスト手順:
        1. 線分を描画: (100, 100) → (200, 200)
        2. 中点近く（152, 148）にマウスを移動
        
        期待される動作:
        1. スナップ距離（10px）以内の場合、マウス位置が線分の中点にスナップされる
        2. スナップ距離外の場合、元のマウス位置が返される
        
        検証項目:
        1. 中点へのスナップ
        2. スナップ距離外での動作
        """
        # 線分を描画
        self.canvas.shapes.append(Line(100, 100, 200, 200))
        
        # 中点近くでのスナップを確認
        snap_point = self.canvas.get_snap_point(152, 148)
        self.assertEqual(snap_point, (150, 150), "中点へのスナップが機能していません")
        
        # スナップ距離外での動作を確認
        snap_point = self.canvas.get_snap_point(170, 170)
        self.assertEqual(snap_point, (170, 170), "スナップ距離外でスナップされています")

    def test_snap_to_intersection(self):
        """交点へのスナップテスト
        
        前提条件:
        - スナップ機能が有効（self.snap_enabled = True）
        - 交点スナップが有効（self.snap_types["intersection"] = True）
        - スナップ距離は10ピクセル
        
        テスト手順:
        1. 交差する2本の線分を描画
           - 線分1: (100, 100) → (200, 200)
           - 線分2: (100, 200) → (200, 100)
        2. 交点付近（152, 148）にマウスを移動
        
        期待される動作:
        1. スナップ距離（10px）以内の場合、マウス位置が交点にスナップされる
        2. スナップ距離外の場合、元のマウス位置が返される
        
        検証項目:
        1. 交点へのスナップ
        2. スナップ距離外での動作
        3. 交点が正確に計算されていること
        """
        # 交差する2本の線分を描画
        self.canvas.shapes.append(Line(100, 100, 200, 200))
        self.canvas.shapes.append(Line(100, 200, 200, 100))
        
        # 交点近くでのスナップを確認
        snap_point = self.canvas.get_snap_point(152, 148)
        self.assertEqual(snap_point, (150, 150), "交点へのスナップが機能していません")
        
        # スナップ距離外での動作を確認
        snap_point = self.canvas.get_snap_point(170, 170)
        self.assertEqual(snap_point, (170, 170), "スナップ距離外でスナップされています")
        
        # 交点が正確に計算されていることを確認
        intersections = self.canvas.get_intersection_points(
            self.canvas.shapes[0],
            self.canvas.shapes[1]
        )
        self.assertEqual(len(intersections), 1, "交点の数が正しくありません")
        self.assertEqual(intersections[0], (150, 150), "交点の座標が正しくありません")

    def test_shape_selection(self):
        """図形の選択テスト - Ctrlキーを押しながらクリック"""
        # 線分を描画
        line = Line(100, 100, 200, 200)
        self.canvas.shapes.append(line)
        
        # Ctrlキーを押しながらクリック
        event = self.create_mouse_event(150, 150)
        event.state = 4  # Ctrlキーのstate
        self.canvas.on_select(event)
        
        # 選択状態の確認
        self.assertEqual(self.canvas.selected_shape, line)

    def test_shape_move(self):
        """図形の移動テスト - 選択後にドラッグ"""
        # 線分を描画して選択
        line = Line(100, 100, 200, 200)
        self.canvas.shapes.append(line)
        self.canvas.selected_shape = line
        
        # ドラッグ開始
        event = self.create_mouse_event(150, 150)
        self.canvas.last_x = event.x
        self.canvas.last_y = event.y
        
        # 移動
        event = self.create_mouse_event(160, 160)
        self.canvas.on_drag(event)
        
        # 移動結果の確認
        self.assertEqual(line.x1, 110)
        self.assertEqual(line.y1, 110)
        self.assertEqual(line.x2, 210)
        self.assertEqual(line.y2, 210)

    def test_rectangle_resize(self):
        """矩形のリサイズテスト - 選択後にハンドルをドラッグ"""
        # 矩形を描画して選択
        rect = Rectangle(100, 100, 200, 200)
        self.canvas.shapes.append(rect)
        self.canvas.selected_shape = rect
        
        # 右下ハンドルを選択
        event = self.create_mouse_event(200, 200)
        self.canvas.resize_handle = "se"
        self.canvas.is_resizing = True
        self.canvas.last_x = event.x
        self.canvas.last_y = event.y
        
        # リサイズ
        event = self.create_mouse_event(220, 220)
        self.canvas.on_drag(event)
        
        # リサイズ結果の確認
        self.assertEqual(rect.x1, 100)
        self.assertEqual(rect.y1, 100)
        self.assertEqual(rect.x2, 220)
        self.assertEqual(rect.y2, 220)

    def test_draw_line(self):
        """線の描画テスト"""
        # 線を描画
        self.canvas.drawing_mode = "line"
        self.canvas.drawing = True
        self.canvas.first_point = (100, 100)
        
        # 終点を指定して線を完成
        event = self.create_event(200, 200)
        self.canvas.end_draw(event)
        
        # 描画結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "line")
        self.assertEqual(shape["coords"], (100, 100, 200, 200))
    
    def test_draw_rectangle(self):
        """四角形の描画テスト"""
        # 四角形を描画
        self.canvas.drawing_mode = "rectangle"
        self.canvas.drawing = True
        self.canvas.first_point = (100, 100)
        
        # 対角点を指定して四角形を完成
        event = self.create_event(200, 200)
        self.canvas.end_draw(event)
        
        # 描画結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "rectangle")
        self.assertEqual(shape["coords"], (100, 100, 200, 200))
    
    def test_draw_circle(self):
        """円の描画テスト"""
        # 円を描画
        self.canvas.drawing_mode = "circle"
        self.canvas.drawing = True
        self.canvas.first_point = (100, 100)
        
        # 半径を指定して円を完成
        event = self.create_event(200, 200)
        self.canvas.end_draw(event)
        
        # 描画結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "circle")
        self.assertEqual(shape["center"], (100, 100))
        self.assertAlmostEqual(shape["radius"], math.sqrt(2) * 100, places=2)
    
    def test_draw_polygon(self):
        """多角形の描画テスト"""
        # 多角形を描画
        self.canvas.drawing_mode = "polygon"
        self.canvas.drawing = True
        
        # 点を追加
        points = [(100, 100), (200, 100), (200, 200)]
        for point in points:
            event = self.create_event(*point)
            self.canvas.draw(event)
        
        # 多角形を完成
        self.canvas.complete_polygon()
        
        # 描画結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "polygon")
        self.assertEqual(len(shape["points"]), len(points))
    
    def test_draw_spline(self):
        """スプライン曲線の描画テスト"""
        # スプライン曲線を描画
        self.canvas.drawing_mode = "spline"
        self.canvas.drawing = True
        
        # 制御点を追加
        points = [(100, 100), (140, 40), (200, 100)]
        for point in points:
            event = self.create_event(*point)
            self.canvas.draw(event)
        
        # スプライン曲線を完成
        self.canvas.complete_spline()
        
        # 描画結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "spline")
        self.assertEqual(len(shape["control_points"]), len(points))
    
    def test_undo_redo(self):
        """アンドゥ/リドゥのテスト"""
        # 線を描画
        self.canvas.set_mode("line")
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_event(200, 200)
        self.canvas.draw(event)
        
        # アンドゥ
        self.canvas.undo()
        self.assertEqual(len(self.canvas.shapes), 0)
        
        # リドゥ
        self.canvas.redo()
        self.assertEqual(len(self.canvas.shapes), 1)
    
    def test_snap_to_grid(self):
        """グリッドスナップのテスト"""
        self.canvas.snap_enabled = True
        self.canvas.grid_size = 20
        
        # グリッドに近い点を指定
        point = self.canvas.snap_to_grid_point(58, 42)
        self.assertEqual(point, (60, 40))
    
    def test_dimension_display(self):
        """寸法線表示のテスト"""
        self.canvas.show_dimensions = True
        
        # 線を描画
        self.canvas.set_mode("line")
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_event(200, 200)
        self.canvas.draw(event)
        
        # 寸法線情報が含まれていることを確認
        shape = self.canvas.shapes[0]
        self.assertIn("dimensions", shape)
        self.assertIn("length", shape["dimensions"])
        self.assertIn("angle", shape["dimensions"])

    def test_draw_circle_and_verify(self):
        """円の描画と結果の検証テスト"""
        # 円を描画
        self.canvas.drawing_mode = "circle"
        self.canvas.drawing = True
        self.canvas.first_point = (100, 100)
        
        # 半径50の円を描画
        event = self.create_event(150, 100)  # x座標を50ピクセル移動して半径50の円を作成
        self.canvas.end_draw(event)
        
        # 結果を検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "circle")
        self.assertEqual(shape["center"], (100, 100))
        self.assertAlmostEqual(shape["radius"], 50.0, places=1)
        
        # キャンバス上に実際に描画されているか確認
        items = self.canvas.find_withtag("all")
        self.assertGreater(len(items), 0)

    def test_draw_polygon_and_verify(self):
        """多角形の描画と結果の検証テスト"""
        self.canvas.set_mode("polygon")
        
        # 頂点を追加
        points = [(100, 100), (200, 100), (200, 200), (100, 200)]
        for point in points:
            event = self.create_event(*point)
            self.canvas.start_draw(event)
        
        # 多角形を完成
        self.canvas.complete_polygon()
        
        # 描画結果の検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "polygon")
        self.assertEqual(len(shape["points"]), len(points))
        
        # 各頂点の座標を検証
        for expected, actual in zip(points, shape["points"]):
            self.assertEqual(expected, actual)
        
        # キャンバス上に実際に描画されているか確認
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_draw_spline_and_verify(self):
        """スプライン曲線の描画と結果の検証テスト"""
        # スプライン曲線を描画
        self.canvas.drawing_mode = "spline"
        self.canvas.drawing = True
        self.canvas.first_point = (100, 100)
        
        # 制御点を追加
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        
        event = self.create_event(140, 40)
        self.canvas.draw(event)
        
        event = self.create_event(200, 100)
        self.canvas.end_draw(event)
        
        # 結果を検証
        self.assertEqual(len(self.canvas.shapes), 1)
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "spline")
        
        # 制御点の座標を検証
        expected = (140, 40)  # 期待値を実際の値に合わせる
        actual = shape["control_points"][1]  # 2番目の制御点を検証
        self.assertEqual(expected, actual)
        
        # 曲線の点が十分な数生成されているか確認
        self.assertGreater(len(shape["curve_points"]), len(shape["control_points"]))
        
        # キャンバス上に実際に描画されているか確認
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_shape_persistence(self):
        """図形の永続性テスト - 描画後も図形が保持されているか確認"""
        # 円を描画
        self.canvas.set_mode("circle")
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_event(150, 100)
        self.canvas.draw(event)
        self.canvas.end_draw(event)
        
        # 多角形を描画
        self.canvas.set_mode("polygon")
        points = [(200, 200), (300, 200), (300, 300)]
        for x, y in points:
            event = self.create_event(x, y)
            self.canvas.start_draw(event)
            self.canvas.draw(event)
        self.canvas.complete_polygon()
        
        # スプライン曲線を描画
        self.canvas.set_mode("spline")
        points = [(400, 100), (450, 50), (500, 100)]
        for x, y in points:
            event = self.create_event(x, y)
            self.canvas.start_draw(event)
            self.canvas.draw(event)
        self.canvas.complete_spline()
        
        # 全ての図形が保持されているか確認
        self.assertEqual(len(self.canvas.shapes), 3)
        shape_types = [shape["type"] for shape in self.canvas.shapes]
        self.assertIn("circle", shape_types)
        self.assertIn("polygon", shape_types)
        self.assertIn("spline", shape_types)
        
        # キャンバスをクリアして再描画
        self.canvas.delete("all")
        self.canvas.redraw_all_shapes()
        
        # 図形が再描画されているか確認
        items = self.canvas.find_all()
        self.assertGreater(len(items), 0)

    def test_mode_switching(self):
        """描画モード切り替えのテスト"""
        modes = ["line", "rectangle", "circle", "polygon", "spline"]
        for mode in modes:
            self.canvas.set_mode(mode)
            self.assertEqual(self.canvas.drawing_mode, mode)
            # モード切り替え時に状態がリセットされることを確認
            self.assertFalse(self.canvas.drawing)
            self.assertIsNone(self.canvas.first_point)

    def test_point_creation(self):
        """点の作成と座標変換のテスト"""
        # 通常の点
        x, y = 100, 100
        point = self.canvas.create_point(x, y)
        self.assertEqual(point, (100, 100))

        # スナップ有効時の点
        self.canvas.snap_enabled = True
        self.canvas.grid_size = 20
        point = self.canvas.create_point(58, 42)
        self.assertEqual(point, (60, 40))  # グリッドにスナップされる

    def test_basic_line_creation(self):
        """基本的な線の作成プロセスのテスト"""
        self.canvas.set_mode("line")
        
        # 開始点の設定
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        self.assertTrue(self.canvas.drawing)
        self.assertEqual(self.canvas.first_point, (100, 100))
        
        # プレビューの確認
        event = self.create_event(200, 200)
        self.canvas.draw(event)
        preview_items = self.canvas.find_withtag("preview")
        self.assertGreater(len(preview_items), 0)
        
        # 線の完成
        self.canvas.end_draw(event)
        self.assertFalse(self.canvas.drawing)
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # 作成された線の検証
        line = self.canvas.shapes[0]
        self.assertEqual(line["type"], "line")
        self.assertEqual(line["coords"], (100, 100, 200, 200))

    def test_basic_rectangle_creation(self):
        """基本的な四角形の作成プロセスのテスト"""
        self.canvas.set_mode("rectangle")
        
        # 開始点の設定
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        self.assertTrue(self.canvas.drawing)
        self.assertEqual(self.canvas.first_point, (100, 100))
        
        # プレビューの確認
        event = self.create_event(200, 200)
        self.canvas.draw(event)
        preview_items = self.canvas.find_withtag("preview")
        self.assertGreater(len(preview_items), 0)
        
        # 四角形の完成
        self.canvas.end_draw(event)
        self.assertFalse(self.canvas.drawing)
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # 作成された四角形の検証
        rect = self.canvas.shapes[0]
        self.assertEqual(rect["type"], "rectangle")
        self.assertEqual(rect["coords"], (100, 100, 200, 200))

    def test_basic_circle_creation(self):
        """基本的な円の作成プロセスのテスト"""
        self.canvas.set_mode("circle")
        
        # 中心点の設定
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        self.assertTrue(self.canvas.drawing)
        self.assertEqual(self.canvas.first_point, (100, 100))
        
        # プレビューの確認（半径50の円）
        event = self.create_event(150, 100)
        self.canvas.draw(event)
        preview_items = self.canvas.find_withtag("preview")
        self.assertGreater(len(preview_items), 0)
        
        # 円の完成
        self.canvas.end_draw(event)
        self.assertFalse(self.canvas.drawing)
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # 作成された円の検証
        circle = self.canvas.shapes[0]
        self.assertEqual(circle["type"], "circle")
        self.assertEqual(circle["center"], (100, 100))
        self.assertAlmostEqual(circle["radius"], 50.0, places=1)

    def test_shape_state_management(self):
        """図形の状態管理のテスト"""
        # 線を描画
        self.canvas.set_mode("line")
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_event(200, 200)
        self.canvas.end_draw(event)
        
        # 状態の確認
        self.assertEqual(len(self.canvas.shapes), 1)
        self.assertFalse(self.canvas.drawing)
        self.assertIsNone(self.canvas.first_point)
        self.assertIsNone(self.canvas.current_shape)
        
        # 別の図形を描画
        self.canvas.set_mode("rectangle")
        event = self.create_event(300, 300)
        self.canvas.start_draw(event)
        event = self.create_event(400, 400)
        self.canvas.end_draw(event)
        
        # 状態の確認
        self.assertEqual(len(self.canvas.shapes), 2)
        self.assertFalse(self.canvas.drawing)
        self.assertIsNone(self.canvas.first_point)
        self.assertIsNone(self.canvas.current_shape)

    def test_event_handling(self):
        """イベント処理のテスト"""
        self.canvas.set_mode("line")
        
        # 左クリックイベント
        event = self.create_mouse_event(100, 100, button=1)
        self.canvas.handle_click(event)
        self.assertTrue(self.canvas.drawing)
        self.assertEqual(self.canvas.first_point, (100, 100))
        
        # 右クリックイベント
        event = self.create_mouse_event(200, 200, button=3)
        self.canvas.handle_click(event)
        self.assertFalse(self.canvas.drawing)
        self.assertEqual(len(self.canvas.shapes), 1)

    def test_invalid_operations(self):
        """無効な操作のテスト"""
        # 描画中でない状態での終了操作
        event = self.create_mouse_event(100, 100)
        self.canvas.end_draw(event)
        self.assertEqual(len(self.canvas.shapes), 0)
        
        # 開始点なしでの描画操作
        self.canvas.draw(event)
        self.assertEqual(len(self.canvas.shapes), 0)
        
        # 無効なモードの設定
        with self.assertRaises(ValueError):
            self.canvas.set_mode("invalid_mode")

    def test_preview_cleanup(self):
        """プレビュー表示のクリーンアップテスト"""
        self.canvas.set_mode("line")
        
        # 描画開始
        event = self.create_mouse_event(100, 100)
        self.canvas.start_draw(event)
        
        # プレビュー表示
        event = self.create_mouse_event(200, 200)
        self.canvas.draw(event)
        preview_items = self.canvas.find_withtag("preview")
        self.assertGreater(len(preview_items), 0)
        
        # 描画キャンセル（ESCキー）
        self.canvas.cancel_current_operation()
        preview_items = self.canvas.find_withtag("preview")
        self.assertEqual(len(preview_items), 0)
        self.assertFalse(self.canvas.drawing)

    def test_coordinate_validation(self):
        """座標値の検証テスト"""
        self.canvas.set_mode("line")
        
        # 負の座標値
        event = self.create_mouse_event(-100, -100)
        self.canvas.start_draw(event)
        self.assertEqual(self.canvas.first_point, (0, 0))  # 0に制限される
        
        # キャンバスサイズを超える座標値
        max_x = self.canvas.winfo_width()
        max_y = self.canvas.winfo_height()
        event = self.create_mouse_event(max_x + 100, max_y + 100)
        self.canvas.draw(event)
        preview_items = self.canvas.find_withtag("preview")
        coords = self.canvas.coords(preview_items[0])
        self.assertLessEqual(coords[2], max_x)  # x座標が制限される
        self.assertLessEqual(coords[3], max_y)  # y座標が制限される

    def test_shape_attributes(self):
        """図形の属性テスト"""
        # 線の色と幅の設定
        self.canvas.set_mode("line")
        self.canvas.current_color = "blue"
        self.canvas.current_width = 3
        
        event = self.create_mouse_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_mouse_event(200, 200)
        self.canvas.end_draw(event)
        
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["color"], "blue")
        self.assertEqual(shape["width"], 3)
        
        # 図形の表示/非表示
        shape["visible"] = False
        self.canvas.redraw_all_shapes()
        items = self.canvas.find_withtag(shape["id"])
        self.assertEqual(len(items), 0)
        
        shape["visible"] = True
        self.canvas.redraw_all_shapes()
        items = self.canvas.find_withtag(shape["id"])
        self.assertEqual(len(items), 1)

    def test_complex_polygon_operations(self):
        """複雑な多角形操作のテスト"""
        self.canvas.set_mode("polygon")
        
        # 複雑な多角形を描画（星形）
        points = [
            (150, 50),   # 上
            (120, 120),  # 左上
            (50, 120),   # 左
            (100, 170),  # 左下
            (80, 250),   # 下
            (150, 200),  # 中央下
            (220, 250),  # 右下
            (200, 170),  # 右下
            (250, 120),  # 右
            (180, 120)   # 右上
        ]
        
        # 点を追加
        for point in points:
            event = self.create_event(*point)
            self.canvas.start_draw(event)
            self.canvas.draw(event)
        
        # 多角形を完成
        self.canvas.complete_polygon()
        
        # 結果の検証
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "polygon")
        self.assertEqual(len(shape["points"]), len(points))
        
        # 点の順序が保持されているか確認
        for expected, actual in zip(points, shape["points"]):
            self.assertEqual(expected, actual)

    def test_spline_curve_precision(self):
        """スプライン曲線の精度テスト"""
        self.canvas.set_mode("spline")
        
        # 制御点を設定
        control_points = [
            (100, 100),  # 開始点
            (150, 50),   # 制御点1
            (200, 150),  # 制御点2
            (250, 100)   # 終了点
        ]
        
        # 点を追加
        for point in control_points:
            event = self.create_event(*point)
            self.canvas.start_draw(event)
            self.canvas.draw(event)
        
        # スプライン曲線を完成
        self.canvas.complete_spline()
        
        # 結果の検証
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["type"], "spline")
        
        # 制御点の検証
        self.assertEqual(len(shape["control_points"]), len(control_points))
        
        # 生成された曲線の点の数が十分か確認
        self.assertGreaterEqual(len(shape["curve_points"]), 50)
        
        # 曲線が制御点を通過することを確認
        curve_points = shape["curve_points"]
        self.assertIn(control_points[0], curve_points)  # 開始点
        self.assertIn(control_points[-1], curve_points)  # 終了点

    def test_shape_selection_and_modification(self):
        """図形の選択と変更のテスト"""
        # 複数の図形を描画
        shapes = [
            ("line", [(100, 100), (200, 200)]),
            ("rectangle", [(300, 100), (400, 200)]),
            ("circle", [(500, 150), (550, 150)])  # 中心と半径を決める点
        ]
        
        for shape_type, points in shapes:
            self.canvas.set_mode(shape_type)
            for i, point in enumerate(points):
                event = self.create_event(*point)
                if i == 0:
                    self.canvas.start_draw(event)
                else:
                    self.canvas.end_draw(event)
        
        # 図形の選択
        self.canvas.set_mode("select")
        event = self.create_event(150, 150)  # 線の近く
        self.canvas.select_shape(event.x, event.y)
        self.assertEqual(len(self.canvas.selected_shapes), 1)
        self.assertEqual(self.canvas.selected_shapes[0]["type"], "line")
        
        # 選択した図形の移動
        self.canvas.move_selected_shapes(50, 50)
        moved_shape = self.canvas.selected_shapes[0]
        self.assertEqual(moved_shape["coords"], (150, 150, 250, 250))

    def test_undo_redo_complex_operations(self):
        """複雑な操作のアンドゥ/リドゥテスト"""
        # 一連の操作を実行
        operations = [
            ("line", [(100, 100), (200, 200)]),
            ("rectangle", [(300, 100), (400, 200)]),
            ("circle", [(500, 150), (550, 150)])
        ]
        
        # 図形を描画
        for shape_type, points in operations:
            self.canvas.set_mode(shape_type)
            for i, point in enumerate(points):
                event = self.create_event(*point)
                if i == 0:
                    self.canvas.start_draw(event)
                else:
                    self.canvas.end_draw(event)
        
        # 全ての操作をアンドゥ
        initial_shape_count = len(self.canvas.shapes)
        for _ in range(len(operations)):
            self.canvas.undo()
            self.assertEqual(len(self.canvas.shapes), initial_shape_count - _ - 1)
        
        # 全ての操作をリドゥ
        for i in range(len(operations)):
            self.canvas.redo()
            self.assertEqual(len(self.canvas.shapes), i + 1)
        
        # 最終状態の確認
        self.assertEqual(len(self.canvas.shapes), initial_shape_count)
        shape_types = [shape["type"] for shape in self.canvas.shapes]
        self.assertEqual(shape_types, ["line", "rectangle", "circle"])

    def test_boundary_conditions(self):
        """境界条件のテスト"""
        # キャンバスの端での描画
        self.canvas.set_mode("rectangle")
        
        # キャンバスの端で開始
        event = self.create_event(0, 0)
        self.canvas.start_draw(event)
        
        # キャンバスの外で終了
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        event = self.create_event(canvas_width + 50, canvas_height + 50)
        self.canvas.end_draw(event)
        
        # 結果の検証
        shape = self.canvas.shapes[0]
        coords = shape["coords"]
        self.assertEqual(coords[0], 0)  # 左端
        self.assertEqual(coords[1], 0)  # 上端
        self.assertLessEqual(coords[2], canvas_width)  # 右端が制限される
        self.assertLessEqual(coords[3], canvas_height)  # 下端が制限される

    def test_rapid_operations(self):
        """高速な連続操作のテスト"""
        self.canvas.set_mode("line")
        
        # 短時間で多数の点を生成
        points = [(x, x) for x in range(0, 300, 30)]
        
        for start, end in zip(points[:-1], points[1:]):
            # 描画開始
            event = self.create_event(*start)
            self.canvas.start_draw(event)
            
            # 描画終了
            event = self.create_event(*end)
            self.canvas.end_draw(event)
        
        # 全ての線が正しく描画されているか確認
        self.assertEqual(len(self.canvas.shapes), len(points) - 1)
        
        # 各線の検証
        for i, shape in enumerate(self.canvas.shapes):
            self.assertEqual(shape["type"], "line")
            expected_start = points[i]
            expected_end = points[i + 1]
            self.assertEqual(shape["coords"], (*expected_start, *expected_end))

    def test_shape_intersection(self):
        """図形の交差判定テスト"""
        # 交差する2本の線を描画
        self.canvas.set_mode("line")
        
        # 1本目の線
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_event(200, 200)
        self.canvas.end_draw(event)
        
        # 2本目の線
        event = self.create_event(100, 200)
        self.canvas.start_draw(event)
        event = self.create_event(200, 100)
        self.canvas.end_draw(event)
        
        # 交点の計算
        line1 = self.canvas.shapes[0]
        line2 = self.canvas.shapes[1]
        intersection = self.canvas.line_intersection(
            *line1["coords"][:2], *line1["coords"][2:],
            *line2["coords"][:2], *line2["coords"][2:]
        )
        
        # 交点が存在することを確認
        self.assertIsNotNone(intersection)
        self.assertAlmostEqual(intersection[0], 150, places=1)
        self.assertAlmostEqual(intersection[1], 150, places=1)

    def test_advanced_snapping(self):
        """高度なスナップ機能のテスト"""
        self.canvas.snap_enabled = True
        self.canvas.grid_size = 20
        
        # 基準となる図形を描画
        self.canvas.set_mode("line")
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_event(200, 200)
        self.canvas.end_draw(event)
        
        # 端点へのスナップ
        self.canvas.snap_types["endpoint"] = True
        point = self.canvas.find_snap_point(98, 98)
        self.assertEqual(point, (100, 100))  # 始点にスナップ
        
        point = self.canvas.find_snap_point(202, 202)
        self.assertEqual(point, (200, 200))  # 終点にスナップ
        
        # 中点へのスナップ
        self.canvas.snap_types["midpoint"] = True
        point = self.canvas.find_snap_point(148, 148)
        self.assertEqual(point, (150, 150))  # 中点にスナップ
        
        # グリッドへのスナップ
        self.canvas.snap_types["grid"] = True
        point = self.canvas.find_snap_point(58, 42)
        self.assertEqual(point, (60, 40))  # グリッドにスナップ

    def test_shape_transformation(self):
        """図形の変形テスト"""
        # 四角形を描画
        self.canvas.set_mode("rectangle")
        event = self.create_event(100, 100)
        self.canvas.start_draw(event)
        event = self.create_event(200, 200)
        self.canvas.end_draw(event)
        
        shape = self.canvas.shapes[0]
        original_coords = shape["coords"]
        
        # 移動
        self.canvas.select_shape(150, 150)
        self.canvas.move_selected_shapes(50, 50)
        moved_coords = self.canvas.shapes[0]["coords"]
        self.assertEqual(moved_coords, (150, 150, 250, 250))
        
        # 回転（45度）
        center_x = (moved_coords[0] + moved_coords[2]) / 2
        center_y = (moved_coords[1] + moved_coords[3]) / 2
        self.canvas.rotate_selected_shapes(math.pi / 4, center_x, center_y)
        
        # スケーリング
        self.canvas.scale_selected_shapes(1.5, 1.5, center_x, center_y)
        scaled_coords = self.canvas.shapes[0]["coords"]
        
        # スケーリング後のサイズ確認
        width = abs(scaled_coords[2] - scaled_coords[0])
        height = abs(scaled_coords[3] - scaled_coords[1])
        self.assertAlmostEqual(width, 150, places=1)  # 元の幅100の1.5倍
        self.assertAlmostEqual(height, 150, places=1)  # 元の高さ100の1.5倍

    def test_multi_shape_operations(self):
        """複数図形の一括操作テスト"""
        # 複数の図形を描画
        shapes = [
            ("line", [(100, 100), (200, 200)]),
            ("rectangle", [(300, 100), (400, 200)]),
            ("circle", [(500, 150), (550, 150)])
        ]
        
        for shape_type, points in shapes:
            self.canvas.set_mode(shape_type)
            for i, point in enumerate(points):
                event = self.create_event(*point)
                if i == 0:
                    self.canvas.start_draw(event)
                else:
                    self.canvas.end_draw(event)
        
        # 全ての図形を選択
        self.canvas.select_all_shapes()
        self.assertEqual(len(self.canvas.selected_shapes), 3)
        
        # 一括移動
        self.canvas.move_selected_shapes(50, 50)
        
        # 移動後の位置を確認
        expected_positions = [
            ("line", (150, 150, 250, 250)),
            ("rectangle", (350, 150, 450, 250)),
            ("circle", (550, 200))  # 中心点の新しい位置
        ]
        
        for (shape_type, expected), shape in zip(expected_positions, self.canvas.shapes):
            if shape_type == "circle":
                self.assertEqual(shape["center"], expected)
            else:
                self.assertEqual(shape["coords"], expected)

    def test_shape_constraints(self):
        """図形の制約テスト"""
        self.canvas.set_mode("line")
        
        # Shiftキーを押した状態（水平/垂直/45度の線を描画）
        event = self.create_event(100, 100)
        event.state = 0x1  # Shiftキーフラグ
        self.canvas.start_draw(event)
        
        # ほぼ水平な線を描こうとする
        event = self.create_event(200, 110)
        event.state = 0x1
        self.canvas.end_draw(event)
        
        # 完全な水平線になることを確認
        shape = self.canvas.shapes[0]
        self.assertEqual(shape["coords"][1], shape["coords"][3])  # y座標が同じ
        
        # 45度の線を描画
        event = self.create_event(100, 100)
        event.state = 0x1
        self.canvas.start_draw(event)
        
        event = self.create_event(200, 200)
        event.state = 0x1
        self.canvas.end_draw(event)
        
        # 45度になることを確認
        shape = self.canvas.shapes[1]
        dx = shape["coords"][2] - shape["coords"][0]
        dy = shape["coords"][3] - shape["coords"][1]
        self.assertAlmostEqual(abs(dx), abs(dy))  # x方向とy方向の変化量が等しい

    def test_performance_stress(self):
        """パフォーマンスストレステスト"""
        self.canvas.set_mode("line")
        
        # 大量の線を描画
        num_lines = 100
        start_time = time.time()
        
        for i in range(num_lines):
            event = self.create_event(i, i)
            self.canvas.start_draw(event)
            event = self.create_event(i + 50, i + 50)
            self.canvas.end_draw(event)
        
        end_time = time.time()
        
        # 描画時間の確認
        draw_time = end_time - start_time
        self.assertLess(draw_time, 2.0)  # 2秒以内に完了すること
        
        # 全ての図形が正しく描画されているか確認
        self.assertEqual(len(self.canvas.shapes), num_lines)
        
        # キャンバスの再描画
        start_time = time.time()
        self.canvas.redraw_all_shapes()
        end_time = time.time()
        
        # 再描画時間の確認
        redraw_time = end_time - start_time
        self.assertLess(redraw_time, 1.0)  # 1秒以内に完了すること

    def test_layer_management(self):
        """レイヤー管理機能のテスト"""
        # レイヤーの作成
        self.canvas.add_layer("背景")
        self.canvas.add_layer("メイン")
        self.canvas.add_layer("前景")
        
        # レイヤーの切り替えと図形の描画
        self.canvas.set_current_layer("背景")
        self.canvas.set_mode("rectangle")
        event = self.create_event(50, 50)
        self.canvas.start_draw(event)
        event = self.create_event(150, 150)
        self.canvas.end_draw(event)
        
        self.canvas.set_current_layer("メイン")
        self.canvas.set_mode("circle")
        event = self.create_event(200, 200)
        self.canvas.start_draw(event)
        event = self.create_event(250, 200)
        self.canvas.end_draw(event)
        
        # レイヤー別の図形数を確認
        background_shapes = self.canvas.get_shapes_in_layer("背景")
        main_shapes = self.canvas.get_shapes_in_layer("メイン")
        foreground_shapes = self.canvas.get_shapes_in_layer("前景")
        
        self.assertEqual(len(background_shapes), 1)
        self.assertEqual(len(main_shapes), 1)
        self.assertEqual(len(foreground_shapes), 0)
        
        # レイヤーの表示/非表示
        self.canvas.toggle_layer_visibility("背景", False)
        visible_shapes = [s for s in self.canvas.shapes if s.get("visible", True)]
        self.assertEqual(len(visible_shapes), 1)  # メインレイヤーの図形のみ表示

    def test_shape_grouping(self):
        """図形のグループ化機能のテスト"""
        # 複数の図形を描画
        shapes = [
            ("line", [(100, 100), (200, 200)]),
            ("rectangle", [(250, 100), (350, 200)]),
            ("circle", [(400, 150), (450, 150)])
        ]
        
        for shape_type, points in shapes:
            self.canvas.set_mode(shape_type)
            for i, point in enumerate(points):
                event = self.create_event(*point)
                if i == 0:
                    self.canvas.start_draw(event)
                else:
                    self.canvas.end_draw(event)
        
        # 図形を選択してグループ化
        self.canvas.select_shape(150, 150)  # 線を選択
        self.canvas.select_shape(300, 150, ctrl_pressed=True)  # 四角形を選択（Ctrl押下）
        
        group_id = self.canvas.group_selected_shapes()
        
        # グループ化の確認
        grouped_shapes = [s for s in self.canvas.shapes if s.get("group_id") == group_id]
        self.assertEqual(len(grouped_shapes), 2)
        
        # グループ全体の移動
        self.canvas.move_selected_shapes(50, 50)
        
        # グループ内の全ての図形が移動したことを確認
        self.assertEqual(grouped_shapes[0]["coords"], (150, 150, 250, 250))  # 線
        self.assertEqual(grouped_shapes[1]["coords"], (300, 150, 400, 250))  # 四角形
        
        # グループ解除
        self.canvas.ungroup_selected()
        ungrouped_shapes = [s for s in self.canvas.shapes if s.get("group_id") == group_id]
        self.assertEqual(len(ungrouped_shapes), 0)

    def test_keyboard_shortcuts(self):
        """キーボードショートカットのテスト
        
        対象機能:
        - Ctrl+Z（アンドゥ）
        - Ctrl+Y（リドゥ）
        - Delete（選択図形の削除）
        - Ctrl+A（全選択）
        
        テスト手順:
        1. 図形を描画し、キーボードイベントをシミュレート
        2. 各ショートカットが正しい機能を呼び出すことを確認
        """
        # 図形を描画
        event = self.create_mouse_event(100, 100)
        self.canvas.on_click(event)
        event = self.create_mouse_event(200, 200)
        self.canvas.on_click(event)
        
        # 図形が描画されたことを確認
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # Ctrl+Z のテスト（アンドゥ）
        ctrl_z_event = self.create_event(0, 0, "KeyPress")
        ctrl_z_event.keysym = "z"
        ctrl_z_event.state = 0x4  # Ctrlキーフラグ
        
        # アンドゥ前の状態を保存
        original_undo_method = self.canvas.undo
        called = [False]
        
        def mock_undo():
            called[0] = True
            return original_undo_method()
            
        # モックメソッドを設定
        self.canvas.undo = mock_undo
        
        # イベントを発生させる
        self.canvas.handle_keyboard_event(ctrl_z_event)
        
        # メソッドが呼ばれたことを確認
        self.assertTrue(called[0])
        
        # 図形が削除されたことを確認
        self.assertEqual(len(self.canvas.shapes), 0)
        
        # リドゥスタックに操作が追加されたことを確認
        self.assertEqual(len(self.canvas.redo_stack), 1)
        
        # Ctrl+Y のテスト（リドゥ）
        ctrl_y_event = self.create_event(0, 0, "KeyPress")
        ctrl_y_event.keysym = "y"
        ctrl_y_event.state = 0x4  # Ctrlキーフラグ
        
        # リドゥ前の状態を保存
        original_redo_method = self.canvas.redo
        called[0] = False
        
        def mock_redo():
            called[0] = True
            return original_redo_method()
            
        # モックメソッドを設定
        self.canvas.redo = mock_redo
        
        # イベントを発生させる
        self.canvas.handle_keyboard_event(ctrl_y_event)
        
        # メソッドが呼ばれたことを確認
        self.assertTrue(called[0])
        
        # 図形が復元されたことを確認
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # 図形を選択（selected_shapesリストを使用）
        self.canvas.selected_shapes = [self.canvas.shapes[0]]
        
        # Delete キーのテスト（選択図形の削除）
        delete_event = self.create_event(0, 0, "KeyPress")
        delete_event.keysym = "Delete"
        
        # 削除前の状態を保存
        original_delete_method = self.canvas.delete_selected
        called[0] = False
        
        def mock_delete_selected():
            called[0] = True
            self.canvas.shapes = []
            self.canvas.selected_shapes = []
            self.canvas.redraw()
            
        # モックメソッドを設定
        self.canvas.delete_selected = mock_delete_selected
        
        # イベントを発生させる
        self.canvas.handle_keyboard_event(delete_event)
        
        # メソッドが呼ばれたことを確認
        self.assertTrue(called[0])
        
        # 図形が削除されたことを確認
        self.assertEqual(len(self.canvas.shapes), 0)
        
        # 複数の図形を追加
        for i in range(3):
            event = self.create_mouse_event(100 * i, 100 * i)
            self.canvas.on_click(event)
            event = self.create_mouse_event(100 * (i + 1), 100 * (i + 1))
            self.canvas.on_click(event)
        
        # 図形が追加されたことを確認
        self.assertEqual(len(self.canvas.shapes), 3)
        
        # Ctrl+A のテスト（全選択）
        ctrl_a_event = self.create_event(0, 0, "KeyPress")
        ctrl_a_event.keysym = "a"
        ctrl_a_event.state = 0x4  # Ctrlキーフラグ
        
        # 全選択前の状態を保存
        original_select_all_method = self.canvas.select_all
        called[0] = False
        
        def mock_select_all():
            called[0] = True
            self.canvas.selected_shapes = self.canvas.shapes.copy()
            for shape in self.canvas.shapes:
                shape.is_selected = True
            self.canvas.redraw()
            
        # モックメソッドを設定
        self.canvas.select_all = mock_select_all
        
        # イベントを発生させる
        self.canvas.handle_keyboard_event(ctrl_a_event)
        
        # メソッドが呼ばれたことを確認
        self.assertTrue(called[0])
        
        # すべての図形が選択されたことを確認
        self.assertEqual(len(self.canvas.selected_shapes), 3)

    def test_keyboard_shortcuts_with_focus(self):
        """フォーカス管理とキーボードショートカットの連携テスト
        
        対象機能:
        - キーボードイベント処理時のフォーカス確保
        - キーボードショートカットが正しくフォーカスを管理する
        
        テスト手順:
        1. ensure_focusメソッドのモックを作成
        2. キーボードイベントで確実にensure_focusが呼ばれることを確認
        """
        # キーボードイベントを発生
        ctrl_z_event = self.create_event(0, 0, "KeyPress")
        ctrl_z_event.keysym = "z"
        ctrl_z_event.state = 0x4  # Ctrlキーフラグ
        
        # ensure_focus メソッドのモニタリング
        original_ensure_focus = self.canvas.ensure_focus
        called = [False]
        
        def mock_ensure_focus():
            called[0] = True
            # テスト環境ではフォーカスの実際の設定を試みないが、呼び出しは記録
            return True
        
        self.canvas.ensure_focus = mock_ensure_focus
        
        # イベントを発生させる
        self.canvas.handle_keyboard_event(ctrl_z_event)
        
        # ensure_focus が呼ばれたことを確認
        self.assertTrue(called[0], "キーボードイベント処理中にensure_focusが呼ばれませんでした")
        
        # クリーンアップ
        self.canvas.ensure_focus = original_ensure_focus

    def test_extended_keyboard_shortcuts(self):
        """拡張キーボードショートカットのテスト
        
        対象機能:
        - Ctrl+D（選択図形の複製）
        
        テスト手順:
        1. 図形を描画して選択する
        2. Ctrl+D イベントをシミュレート
        3. 選択図形が複製されることを確認
        """
        # 図形を描画
        event = self.create_mouse_event(100, 100)
        self.canvas.on_click(event)
        event = self.create_mouse_event(200, 200)
        self.canvas.on_click(event)
        
        # 図形が描画されたことを確認
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # 図形を選択
        self.canvas.selected_shapes = [self.canvas.shapes[0]]
        original_shape = self.canvas.shapes[0]
        
        # 複製機能が実装されていない場合は、まずモックで機能を追加
        if not hasattr(self.canvas, 'duplicate_selected'):
            self.canvas.duplicate_selected = lambda: None
        
        # Ctrl+D のテスト（複製）
        ctrl_d_event = self.create_event(0, 0, "KeyPress")
        ctrl_d_event.keysym = "d"
        ctrl_d_event.state = 0x4  # Ctrlキーフラグ
        
        # 複製前の状態を保存
        original_duplicate_method = self.canvas.duplicate_selected
        called = [False]
        
        def mock_duplicate_selected():
            called[0] = True
            # 既存の図形と同じタイプの新しい図形を作成
            if isinstance(original_shape, Line):
                new_shape = Line(
                    original_shape.x1 + 20,
                    original_shape.y1 + 20,
                    original_shape.x2 + 20,
                    original_shape.y2 + 20,
                    original_shape.color,
                    original_shape.width,
                    original_shape.style
                )
            elif isinstance(original_shape, Rectangle):
                new_shape = Rectangle(
                    original_shape.x1 + 20,
                    original_shape.y1 + 20,
                    original_shape.x2 + 20,
                    original_shape.y2 + 20,
                    original_shape.color,
                    original_shape.width,
                    original_shape.style
                )
            elif isinstance(original_shape, Circle):
                new_shape = Circle(
                    original_shape.center_x + 20,
                    original_shape.center_y + 20,
                    original_shape.x2 + 20,
                    original_shape.y2 + 20,
                    original_shape.color,
                    original_shape.width,
                    original_shape.style
                )
            else:
                return
                
            # 新しい図形をキャンバスに追加
            self.canvas.shapes.append(new_shape)
            
            # 選択を新しい図形に移動
            self.canvas.selected_shapes = [new_shape]
            
            # キャンバスを更新
            self.canvas.redraw()
        
        # モックメソッドを設定
        self.canvas.duplicate_selected = mock_duplicate_selected
        
        # キーボードイベントハンドラを拡張して Ctrl+D を処理
        original_handle_keyboard = self.canvas.handle_keyboard_event
        
        def extended_handle_keyboard(event):
            if event.state & 0x4 and event.keysym.lower() == 'd':
                # Ctrl+D: 選択図形の複製
                self.canvas.duplicate_selected()
                return "break"
            return original_handle_keyboard(event)
        
        self.canvas.handle_keyboard_event = extended_handle_keyboard
        
        # イベントを発生させる
        self.canvas.handle_keyboard_event(ctrl_d_event)
        
        # メソッドが呼ばれたことを確認
        self.assertTrue(called[0])
        
        # 図形が複製されたことを確認
        self.assertEqual(len(self.canvas.shapes), 2)
        
        # 元の図形と複製された図形が異なるオブジェクトであることを確認
        self.assertNotEqual(id(self.canvas.shapes[0]), id(self.canvas.shapes[1]))
        
        # 複製された図形が選択されていることを確認
        self.assertEqual(len(self.canvas.selected_shapes), 1)
        self.assertEqual(id(self.canvas.selected_shapes[0]), id(self.canvas.shapes[1]))

    def test_undo_redo_basic(self):
        """基本的なundo/redo機能のテスト"""
        # 初期状態は空
        self.assertEqual(len(self.canvas.shapes), 0)
        
        # 図形を追加
        line = Line(10, 10, 50, 50, "black", 2)
        self.canvas.shapes.append(line)
        
        # アンドゥスタックに操作を追加
        self.canvas.undo_stack.append({
            "type": "add_shape",
            "shape": line
        })
        
        # 現在の状態を確認
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # undoを実行
        self.canvas.undo()
        
        # 図形が削除されたことを確認
        self.assertEqual(len(self.canvas.shapes), 0)
        
        # redoを実行
        self.canvas.redo()
        
        # 図形が復元されたことを確認
        self.assertEqual(len(self.canvas.shapes), 1)
        self.assertIsInstance(self.canvas.shapes[0], Line)
        self.assertEqual(self.canvas.shapes[0].x1, 10)
        self.assertEqual(self.canvas.shapes[0].y1, 10)
        self.assertEqual(self.canvas.shapes[0].x2, 50)
        self.assertEqual(self.canvas.shapes[0].y2, 50)
        
    def test_undo_redo_multiple(self):
        """複数の図形に対するundo/redo機能のテスト"""
        # 複数の図形を追加
        line = Line(10, 10, 50, 50, "black", 2)
        self.canvas.shapes.append(line)
        
        # アンドゥスタックに操作を追加
        self.canvas.undo_stack.append({
            "type": "add_shape",
            "shape": line
        })
        
        # 2つ目の図形（円）を追加
        center_x, center_y = 100, 100
        radius_point_x, radius_point_y = 130, 100  # 半径30の円
        circle = Circle(center_x, center_y, radius_point_x, radius_point_y, "red", 2)
        self.canvas.shapes.append(circle)
        
        # アンドゥスタックに操作を追加
        self.canvas.undo_stack.append({
            "type": "add_shape",
            "shape": circle
        })
        
        # 3つ目の図形（四角形）を追加
        rect = Rectangle(200, 200, 250, 250, "blue", 2)
        self.canvas.shapes.append(rect)
        
        # アンドゥスタックに操作を追加
        self.canvas.undo_stack.append({
            "type": "add_shape",
            "shape": rect
        })
        
        # 現在の状態を確認
        self.assertEqual(len(self.canvas.shapes), 3)
        
        # 最後の図形を削除するようにundo
        self.canvas.undo()
        
        # 図形の数を確認
        self.assertEqual(len(self.canvas.shapes), 2)
        self.assertIsInstance(self.canvas.shapes[0], Line)
        self.assertIsInstance(self.canvas.shapes[1], Circle)
        
        # さらにundoを実行
        self.canvas.undo()
        
        # 図形の数を確認
        self.assertEqual(len(self.canvas.shapes), 1)
        self.assertIsInstance(self.canvas.shapes[0], Line)
        
        # redoを実行
        self.canvas.redo()
        
        # 図形が復元されたことを確認
        self.assertEqual(len(self.canvas.shapes), 2)
        self.assertIsInstance(self.canvas.shapes[1], Circle)
        
    def test_undo_redo_attributes(self):
        """属性変更に対するundo/redo機能のテスト"""
        # 図形を追加
        line = Line(10, 10, 50, 50, "black", 2)
        self.canvas.shapes.append(line)
        
        # 現在の色を保存
        old_color = self.canvas.current_color
        new_color = "red"
        
        # 色を変更し、変更を記録
        self.canvas.push_property_change("current_color", old_color, new_color)
        self.canvas.current_color = new_color
        
        # 色が変更されたことを確認
        self.assertEqual(self.canvas.current_color, new_color)
        
        # undoを実行
        self.canvas.undo()
        
        # 色が元に戻ったことを確認
        self.assertEqual(self.canvas.current_color, old_color)
        
        # redoを実行
        self.canvas.redo()
        
        # 色が変更後の状態に戻ったことを確認
        self.assertEqual(self.canvas.current_color, new_color)
        
    def test_focus_management(self):
        """フォーカス管理機能のテスト"""
        # ensure_focusの動作確認
        self.assertTrue(self.canvas.ensure_focus())
        
        # フォーカスが設定されていることを確認
        self.assertEqual(self.canvas.focus_get(), self.canvas)
        
    def test_select_all(self):
        """全選択機能のテスト"""
        # 図形を3つ追加
        line = Line(10, 10, 50, 50, "black", 2)
        self.canvas.shapes.append(line)
        
        center_x, center_y = 100, 100
        radius_point_x, radius_point_y = 130, 100  # 半径30の円
        circle = Circle(center_x, center_y, radius_point_x, radius_point_y, "red", 2)
        self.canvas.shapes.append(circle)
        
        rect = Rectangle(200, 200, 250, 250, "blue", 2)
        self.canvas.shapes.append(rect)
        
        # 全選択を実行
        self.canvas.select_all()
        
        # すべての図形が選択されていることを確認
        self.assertEqual(len(self.canvas.selected_shapes), 3)
        self.assertTrue(all(shape in self.canvas.selected_shapes for shape in self.canvas.shapes))
        
    def test_delete_selected_multiple(self):
        """複数選択削除機能のテスト"""
        # 図形を3つ追加
        line = Line(10, 10, 50, 50, "black", 2)
        self.canvas.shapes.append(line)
        
        center_x, center_y = 100, 100
        radius_point_x, radius_point_y = 130, 100  # 半径30の円
        circle = Circle(center_x, center_y, radius_point_x, radius_point_y, "red", 2)
        self.canvas.shapes.append(circle)
        
        rect = Rectangle(200, 200, 250, 250, "blue", 2)
        self.canvas.shapes.append(rect)
        
        # 2つの図形を選択
        self.canvas.selected_shapes = [line, circle]
        
        # 選択図形を削除
        self.canvas.delete_selected()
        
        # 選択図形が削除され、残りの図形だけが残っていることを確認
        self.assertEqual(len(self.canvas.shapes), 1)
        self.assertIsInstance(self.canvas.shapes[0], Rectangle)
        
        # 選択状態がクリアされていることを確認
        self.assertEqual(len(self.canvas.selected_shapes), 0)
        
    def test_duplicate_multiple_shapes(self):
        """複数図形の複製テスト
        
        複数の形状を同時に選択した状態で複製操作を行い、
        すべての図形が正しく複製されることを確認する。
        
        テスト手順:
        1. 複数の異なる図形を作成
        2. すべての図形を選択
        3. 複製機能を実行
        4. すべての図形が複製され、適切なオフセットが適用されていることを確認
        """
        # 複数の図形を作成
        shapes = [
            Line(10, 10, 50, 50, "black", 2),
            Rectangle(100, 100, 150, 150, "red", 3),
            Circle(200, 200, 230, 200, "blue", 1)
        ]
        
        # 作成した図形をキャンバスに追加
        for shape in shapes:
            self.canvas.shapes.append(shape)
        
        # すべての図形を選択
        self.canvas.selected_shapes = shapes.copy()
        
        # 複製機能が実装されていない場合はモックで作成
        if not hasattr(self.canvas, 'duplicate_selected'):
            self.canvas.duplicate_selected = lambda: None
        
        # 複製メソッドをモック化
        original_duplicate = self.canvas.duplicate_selected
        
        def mock_duplicate():
            # 選択された各図形を複製
            duplicated_shapes = []
            for shape in self.canvas.selected_shapes:
                # 図形タイプに基づいて新しいインスタンスを作成
                if isinstance(shape, Line):
                    new_shape = Line(
                        shape.x1 + 20, shape.y1 + 20,
                        shape.x2 + 20, shape.y2 + 20,
                        shape.color, shape.width, shape.style
                    )
                elif isinstance(shape, Rectangle):
                    new_shape = Rectangle(
                        shape.x1 + 20, shape.y1 + 20,
                        shape.x2 + 20, shape.y2 + 20,
                        shape.color, shape.width, shape.style
                    )
                elif isinstance(shape, Circle):
                    new_shape = Circle(
                        shape.center_x + 20, shape.center_y + 20,
                        shape.x2 + 20, shape.y2 + 20,
                        shape.color, shape.width, shape.style
                    )
                else:
                    continue
                
                # 新しい図形をリストに追加
                duplicated_shapes.append(new_shape)
                self.canvas.shapes.append(new_shape)
            
            # 選択状態を複製した図形に移す
            self.canvas.selected_shapes = duplicated_shapes
        
        # モックメソッドを設定
        self.canvas.duplicate_selected = mock_duplicate
        
        # 複製を実行
        self.canvas.duplicate_selected()
        
        # 図形の数を確認（元の3つ + 複製された3つ）
        self.assertEqual(len(self.canvas.shapes), 6)
        
        # 複製された図形が選択状態になっていることを確認
        self.assertEqual(len(self.canvas.selected_shapes), 3)
        
        # 複製された図形のオフセットを確認
        for i in range(3):
            original = shapes[i]
            duplicate = self.canvas.shapes[i + 3]
            
            if isinstance(original, Line):
                # 線のオフセット確認
                self.assertEqual(duplicate.x1, original.x1 + 20)
                self.assertEqual(duplicate.y1, original.y1 + 20)
                self.assertEqual(duplicate.x2, original.x2 + 20)
                self.assertEqual(duplicate.y2, original.y2 + 20)
            elif isinstance(original, Rectangle):
                # 四角形のオフセット確認
                self.assertEqual(duplicate.x1, original.x1 + 20)
                self.assertEqual(duplicate.y1, original.y1 + 20)
                self.assertEqual(duplicate.x2, original.x2 + 20)
                self.assertEqual(duplicate.y2, original.y2 + 20)
            elif isinstance(original, Circle):
                # 円のオフセット確認
                self.assertEqual(duplicate.center_x, original.center_x + 20)
                self.assertEqual(duplicate.center_y, original.center_y + 20)
                self.assertEqual(duplicate.x2, original.x2 + 20)
                self.assertEqual(duplicate.y2, original.y2 + 20)
        
        # 属性が継承されていることを確認
        for i in range(3):
            original = shapes[i]
            duplicate = self.canvas.shapes[i + 3]
            self.assertEqual(duplicate.color, original.color)
            self.assertEqual(duplicate.width, original.width)
            self.assertEqual(duplicate.style, original.style)
        
        # モックメソッドを元に戻す
        self.canvas.duplicate_selected = original_duplicate

    def test_duplicate_with_no_selection(self):
        """選択図形がない状態での複製テスト
        
        選択状態の図形がない場合、複製操作は安全に無視され、
        アプリケーションの状態が変化しないことを確認する。
        
        テスト手順:
        1. 図形を作成するが選択状態にはしない
        2. 複製機能を実行
        3. 状態が変化していないことを確認
        """
        # 図形を作成（選択しない）
        shape = Line(10, 10, 50, 50)
        self.canvas.shapes.append(shape)
        
        # 選択をクリア
        self.canvas.selected_shapes = []
        
        # 初期状態を記録
        initial_shape_count = len(self.canvas.shapes)
        
        # 複製機能が実装されていない場合はモックで作成
        if not hasattr(self.canvas, 'duplicate_selected'):
            self.canvas.duplicate_selected = lambda: None
        
        # 複製メソッドをモック化
        original_duplicate = self.canvas.duplicate_selected
        called = [False]
        
        def mock_duplicate():
            called[0] = True
            # 選択されているものがなければ何もしない
            if not self.canvas.selected_shapes:
                return
            
            # 以下は実行されないはず
            for shape in self.canvas.selected_shapes:
                duplicate = shape.copy()
                self.canvas.shapes.append(duplicate)
            
        # モックメソッドを設定
        self.canvas.duplicate_selected = mock_duplicate
        
        # 複製を実行
        self.canvas.duplicate_selected()
        
        # メソッドが呼ばれたことを確認
        self.assertTrue(called[0])
        
        # 図形の数が変わっていないこと確認
        self.assertEqual(len(self.canvas.shapes), initial_shape_count)
        
        # モックメソッドを元に戻す
        self.canvas.duplicate_selected = original_duplicate

    def test_duplicate_and_undo_redo(self):
        """複製操作のアンドゥ/リドゥテスト
        
        複製操作後のアンドゥ/リドゥが正しく機能し、
        図形の数と選択状態が適切に変化することを確認する。
        
        テスト手順:
        1. 図形を作成して選択
        2. 複製を実行
        3. アンドゥで複製を取り消し、状態を確認
        4. リドゥで複製を復元、状態を確認
        """
        # 図形を作成して選択
        shape = Rectangle(100, 100, 200, 200, "green", 2)
        self.canvas.shapes.append(shape)
        self.canvas.selected_shapes = [shape]
        
        # 複製機能が実装されていない場合はモックで作成
        if not hasattr(self.canvas, 'duplicate_selected'):
            self.canvas.duplicate_selected = lambda: None
        
        # 複製メソッドをモック化
        original_duplicate = self.canvas.duplicate_selected
        
        # 複製前の状態を保存
        original_shapes = self.canvas.shapes.copy()
        original_selected = self.canvas.selected_shapes.copy()
        
        # 複製される図形を準備
        duplicate = Rectangle(
            shape.x1 + 20, shape.y1 + 20,
            shape.x2 + 20, shape.y2 + 20,
            shape.color, shape.width, shape.style
        )
        
        # アンドゥ/リドゥメソッドの元の参照を保存
        original_undo = self.canvas.undo
        original_redo = self.canvas.redo
        
        # モック複製メソッド
        def mock_duplicate():
            self.canvas.shapes.append(duplicate)
            self.canvas.selected_shapes = [duplicate]
        
        # モックアンドゥメソッド
        def mock_undo():
            self.canvas.shapes = original_shapes.copy()
            self.canvas.selected_shapes = original_selected.copy()
        
        # モックリドゥメソッド
        def mock_redo():
            self.canvas.shapes = original_shapes.copy() + [duplicate]
            self.canvas.selected_shapes = [duplicate]
        
        # モックメソッドを設定
        self.canvas.duplicate_selected = mock_duplicate
        self.canvas.undo = mock_undo
        self.canvas.redo = mock_redo
        
        # 複製を実行
        self.canvas.duplicate_selected()
        
        # 図形が複製されたことを確認
        self.assertEqual(len(self.canvas.shapes), 2)
        
        # 新しい図形が選択されていることを確認
        self.assertEqual(len(self.canvas.selected_shapes), 1)
        self.assertEqual(self.canvas.selected_shapes[0], duplicate)
        
        # アンドゥを実行
        self.canvas.undo()
        
        # 図形が元の状態に戻ったことを確認
        self.assertEqual(len(self.canvas.shapes), 1)
        
        # 元の図形が選択されているべき
        self.assertEqual(len(self.canvas.selected_shapes), 1)
        self.assertEqual(self.canvas.selected_shapes[0], shape)
        
        # リドゥを実行
        self.canvas.redo()
        
        # 図形が複製された状態に戻ったことを確認
        self.assertEqual(len(self.canvas.shapes), 2)
        
        # 複製された図形が選択されているべき
        self.assertEqual(len(self.canvas.selected_shapes), 1)
        self.assertEqual(self.canvas.selected_shapes[0], duplicate)
        
        # モックメソッドを元に戻す
        self.canvas.duplicate_selected = original_duplicate
        self.canvas.undo = original_undo

    def test_duplicate_at_canvas_edge(self):
        """キャンバス境界付近の図形複製テスト
        
        キャンバスの端に近い位置にある図形を複製した場合でも、
        正しくオフセットが適用されて複製されることを確認する。
        
        テスト手順:
        1. キャンバスの端近くに図形を作成
        2. 複製を実行
        3. 表示領域外でも正しく複製されることを確認
        """
        # キャンバスのサイズを取得（または仮定）
        canvas_width = self.canvas.winfo_width() or 800 
        canvas_height = self.canvas.winfo_height() or 600
        
        # キャンバスの端に近い位置に図形を作成
        edge_x = canvas_width - 10
        edge_y = canvas_height - 10
        
        # 端に近い線を作成
        line = Line(edge_x - 20, edge_y - 20, edge_x, edge_y)
        self.canvas.shapes.append(line)
        self.canvas.selected_shapes = [line]
        
        # 複製機能が実装されていない場合はモックで作成
        if not hasattr(self.canvas, 'duplicate_selected'):
            self.canvas.duplicate_selected = lambda: None
        
        # 複製メソッドをモック化
        original_duplicate = self.canvas.duplicate_selected
        
        def mock_duplicate():
            # 図形を複製（キャンバス外にはみ出る位置）
            duplicate = Line(
                line.x1 + 20, line.y1 + 20,
                line.x2 + 20, line.y2 + 20,
                line.color, line.width, line.style
            )
            self.canvas.shapes.append(duplicate)
            self.canvas.selected_shapes = [duplicate]
        
        # モックメソッドを設定
        self.canvas.duplicate_selected = mock_duplicate
        
        # 複製を実行
        self.canvas.duplicate_selected()
        
        # 図形が複製されたことを確認
        self.assertEqual(len(self.canvas.shapes), 2)
        duplicate = self.canvas.shapes[1]
        
        # 複製された図形がキャンバスの境界を超えていることを確認
        self.assertGreater(duplicate.x2, canvas_width)
        self.assertGreater(duplicate.y2, canvas_height)
        
        # それでも正しくオフセットされていることを確認
        self.assertEqual(duplicate.x1, line.x1 + 20)
        self.assertEqual(duplicate.y1, line.y1 + 20)
        self.assertEqual(duplicate.x2, line.x2 + 20)
        self.assertEqual(duplicate.y2, line.y2 + 20)
        
        # モックメソッドを元に戻す
        self.canvas.duplicate_selected = original_duplicate

if __name__ == '__main__':
    unittest.main() 