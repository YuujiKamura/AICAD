import tkinter as tk
import logging
import math
from drawing_canvas import DrawingCanvas, Line, Rectangle, Circle, Polygon
from app import DrawingApp
import unittest
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class RectState:
    """四角形の状態を表すデータクラス"""
    x1: int
    y1: int
    x2: int
    y2: int

    def __str__(self):
        return f"x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2}"

@dataclass
class ResizeAction:
    """リサイズ操作を表すデータクラス"""
    handle: str
    to_x: int
    to_y: int
    description: str

    def __str__(self):
        return f"{self.description}: ハンドル {self.handle} を ({self.to_x}, {self.to_y}) に移動"

@dataclass
class ResizeTestCase:
    """リサイズテストケースを表すデータクラス"""
    name: str
    initial: RectState
    action: ResizeAction
    expected: RectState

    def log_test_case(self):
        """テストケースの内容をログに出力"""
        logger.debug(f"=== {self.name} ===")
        logger.debug(f"初期状態: {self.initial}")
        logger.debug(f"操作: {self.action}")
        logger.debug(f"期待値: {self.expected}")

class DrawingTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # ウィンドウを非表示
        self.canvas = DrawingCanvas(self.root)
        self.logger = logger
        
        # 各テストケース用の初期状態をリセット
        self.canvas.reset()  # キャンバスをクリア
        self.canvas.mode = "line"  # デフォルトモードを設定
        self.canvas.current_color = "black"  # デフォルト色を設定
        self.canvas.current_width = 1  # デフォルト線幅を設定
        self.canvas.snap_enabled = True  # スナップをデフォルトで有効に
        self.canvas.snap_types = {  # スナップタイプをデフォルトで設定
            "endpoint": True,
            "midpoint": True,
            "intersection": True
        }
        self.canvas.selected_shape = None  # 選択状態をリセット
        self.canvas.is_moving = False
        self.canvas.is_resizing = False
        self.canvas.resize_handle = None
        self.canvas.last_x = None
        self.canvas.last_y = None
        
    def create_event(self, x, y, ctrl=False):
        """テスト用のイベントオブジェクトを作成"""
        event = type('Event', (), {})()
        event.x = x
        event.y = y
        event.state = 0x0004 if ctrl else 0  # Ctrlキーの状態
        return event
        
    def test_app_launch(self):
        """アプリケーション起動テスト"""
        self.logger.debug("=== アプリケーション起動テスト開始 ===")
        
        app = DrawingApp()
        
        # 1. メインウィンドウの確認
        self.assertIsNotNone(app.root, "メインウィンドウが作成されていません")
        self.assertEqual(app.root.title(), "描画アプリケーション", "ウィンドウタイトルが正しくありません")
        
        # 2. キャンバスの確認
        self.assertIsNotNone(app.canvas, "キャンバスが作成されていません")
        self.assertEqual(int(app.canvas['width']), 800, "キャンバスの幅が正しくありません")
        self.assertEqual(int(app.canvas['height']), 600, "キャンバスの高さが正しくありません")
        self.assertEqual(app.canvas['bg'], "white", "キャンバスの背景色が正しくありません")
        
        # 3. キャンバスの初期状態確認
        self.assertEqual(app.canvas.mode, "line", "初期描画モードが正しくありません")
        self.assertEqual(len(app.canvas.shapes), 0, "図形リストが空ではありません")
        self.assertEqual(len(app.canvas.current_points), 0, "現在の点リストが空ではありません")
        self.assertTrue(app.canvas.snap_enabled, "スナップが有効になっていません")
        
        # 4. イベントバインディングの確認
        events = app.canvas.bind()
        required_events = {
            '<Button-1>': "左クリックイベントがバインドされていません",
            '<Button-3>': "右クリックイベントがバインドされていません",
            '<Motion>': "マウス移動イベントがバインドされていません",
            '<Key-Escape>': "Escキーイベントがバインドされていません",
            '<Control-Button-1>': "Ctrl+クリックイベントがバインドされていません",
            '<B1-Motion>': "ドラッグイベントがバインドされていません",
            '<ButtonRelease-1>': "マウスボタン解放イベントがバインドされていません"
        }
        for event, message in required_events.items():
            self.assertIn(event, events, message)
        
        # 5. ツールバーの確認
        self.assertIsNotNone(app.toolbar, "ツールバーが作成されていません")
        
        # 6. 描画モードボタンの確認
        mode_buttons = ["線", "四角形", "円", "多角形"]
        for mode in mode_buttons:
            found = False
            for child in app.toolbar.winfo_children():
                if isinstance(child, tk.ttk.LabelFrame) and child.winfo_children():
                    for button in child.winfo_children():
                        if isinstance(button, tk.ttk.Button) and button['text'] == mode:
                            found = True
                            break
            self.assertTrue(found, f"{mode}モードのボタンが見つかりません")
        
        # 7. 外観設定の確認
        # 色選択
        self.assertIsNotNone(app.color_var, "色設定が初期化されていません")
        self.assertEqual(app.color_var.get(), "black", "初期色が正しくありません")
        colors = ["black", "red", "blue", "green", "yellow", "purple"]
        for child in app.toolbar.winfo_children():
            if isinstance(child, tk.ttk.LabelFrame):
                for widget in child.winfo_children():
                    if isinstance(widget, tk.ttk.Combobox) and widget['values']:
                        if all(color in widget['values'] for color in colors):
                            break
                else:
                    continue
                break
        else:
            self.fail("色選択コンボボックスが見つかりません")
        
        # 線幅設定
        self.assertIsNotNone(app.line_width_var, "線幅設定が初期化されていません")
        self.assertEqual(app.line_width_var.get(), "1", "初期線幅が正しくありません")
        widths = ["1", "2", "3", "4", "5"]
        for child in app.toolbar.winfo_children():
            if isinstance(child, tk.ttk.LabelFrame):
                for widget in child.winfo_children():
                    if isinstance(widget, tk.ttk.Combobox) and widget['values']:
                        if all(width in widget['values'] for width in widths):
                            break
                else:
                    continue
                break
        else:
            self.fail("線幅選択コンボボックスが見つかりません")
        
        # 線スタイル設定
        styles = ["実線", "破線", "点線", "一点鎖線"]
        for child in app.toolbar.winfo_children():
            if isinstance(child, tk.ttk.LabelFrame):
                for widget in child.winfo_children():
                    if isinstance(widget, tk.ttk.Combobox) and widget['values']:
                        if all(style in widget['values'] for style in styles):
                            break
                else:
                    continue
                break
        else:
            self.fail("線スタイル選択コンボボックスが見つかりません")
        
        # 8. スナップ設定の確認
        snap_types = ["endpoint", "midpoint", "intersection"]
        for snap_type in snap_types:
            self.assertTrue(app.canvas.snap_types[snap_type], 
                           f"{snap_type}スナップが有効になっていません")
        
        # スナップ設定のチェックボックス確認
        snap_labels = ["スナップ有効", "端点", "中点", "交点"]
        for label in snap_labels:
            found = False
            for child in app.toolbar.winfo_children():
                if isinstance(child, tk.ttk.LabelFrame):
                    for widget in child.winfo_children():
                        if isinstance(widget, tk.ttk.Checkbutton) and widget['text'] == label:
                            found = True
                            break
            self.assertTrue(found, f"{label}のチェックボックスが見つかりません")
        
        # 9. 寸法線表示設定の確認
        self.assertTrue(app.dimension_var.get(), "寸法線表示が初期状態で有効になっていません")
        found = False
        for child in app.toolbar.winfo_children():
            if isinstance(child, tk.ttk.LabelFrame):
                for widget in child.winfo_children():
                    if isinstance(widget, tk.ttk.Checkbutton) and widget['text'] == "寸法線表示":
                        found = True
                        break
        self.assertTrue(found, "寸法線表示のチェックボックスが見つかりません")
        
        # 10. アンドゥ/リドゥボタンの確認
        undo_redo_buttons = ["元に戻す", "やり直し"]
        for button_text in undo_redo_buttons:
            found = False
            for child in app.toolbar.winfo_children():
                if isinstance(child, tk.ttk.Frame):
                    for button in child.winfo_children():
                        if isinstance(button, tk.ttk.Button) and button['text'] == button_text:
                            found = True
                            break
            self.assertTrue(found, f"{button_text}ボタンが見つかりません")
        
        # 11. ステータスバーの確認
        self.assertIsNotNone(app.statusbar, "ステータスバーが作成されていません")
        self.assertIsNotNone(app.status_var, "ステータス変数が初期化されていません")
        self.assertEqual(app.status_var.get(), "準備完了", 
                        "ステータスバーの初期メッセージが正しくありません")
        
        app.root.destroy()
        self.logger.debug("=== アプリケーション起動テスト終了 ===")
        
    def test_line(self):
        """線描画のテスト"""
        logger.debug("=== 線描画テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "line"
        
        # 1点目を追加
        event = type('Event', (), {'x': 100, 'y': 100})()
        self.canvas.on_click(event)
        assert len(self.canvas.current_points) == 1
        assert self.canvas.current_points[0] == (100, 100)
        
        # 2点目を追加（線が完成するはず）
        event = type('Event', (), {'x': 200, 'y': 200})()
        self.canvas.on_click(event)
        assert len(self.canvas.shapes) == 1
        shape = self.canvas.shapes[0]
        assert isinstance(shape, Line)
        assert len(shape.points) == 2
        assert shape.points == [(100, 100), (200, 200)]
        
        logger.debug("=== 線描画テスト終了 ===")
        
    def test_rectangle(self):
        """矩形描画のテスト"""
        logger.debug("=== 矩形描画テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "rectangle"
        
        # 1点目を追加（左上）
        event = type('Event', (), {'x': 100, 'y': 100})()
        self.canvas.on_click(event)
        assert len(self.canvas.current_points) == 1
        assert self.canvas.current_points[0] == (100, 100)
        
        # 2点目を追加（右下、矩形が完成するはず）
        event = type('Event', (), {'x': 200, 'y': 200})()
        self.canvas.on_click(event)
        assert len(self.canvas.shapes) == 1
        shape = self.canvas.shapes[0]
        assert isinstance(shape, Rectangle)
        assert len(shape.points) == 4
        assert shape.points == [(100, 100), (200, 100), (200, 200), (100, 200)]
        
        logger.debug("=== 矩形描画テスト終了 ===")
        
    def test_circle(self):
        """円描画のテスト"""
        logger.debug("=== 円描画テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "circle"
        
        # 1点目を追加（中心点）
        event = type('Event', (), {'x': 150, 'y': 150})()
        self.canvas.on_click(event)
        assert len(self.canvas.current_points) == 1
        assert self.canvas.current_points[0] == (150, 150)
        
        # 2点目を追加（半径を決める点、円が完成するはず）
        event = type('Event', (), {'x': 200, 'y': 150})()
        self.canvas.on_click(event)
        assert len(self.canvas.shapes) == 1
        shape = self.canvas.shapes[0]
        assert isinstance(shape, Circle)
        assert len(shape.points) == 2
        assert shape.points == [(150, 150), (200, 150)]
        
        # 半径の検証
        x1, y1 = shape.center_x, shape.center_y
        x2, y2 = shape.x2, shape.y2
        radius = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        assert radius == 50.0
        
        logger.debug("=== 円描画テスト終了 ===")
        
    def test_polygon(self):
        """多角形描画のテスト"""
        logger.debug("=== 多角形描画テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "polygon"
        
        # 3点を追加
        points = [(100, 100), (200, 100), (150, 200)]
        for x, y in points:
            event = type('Event', (), {'x': x, 'y': y})()
            self.canvas.on_click(event)
            
        # 右クリックで完成
        event = type('Event', (), {'x': 0, 'y': 0})()
        self.canvas.on_right_click(event)
        
        assert len(self.canvas.shapes) == 1
        shape = self.canvas.shapes[0]
        assert isinstance(shape, Polygon)
        assert len(shape.points) == 3
        assert shape.points == points
        
        logger.debug("=== 多角形描画テスト終了 ===")
        
    def test_shape_preview(self):
        """図形のプレビュー表示テスト"""
        logger.debug("=== プレビュー表示テスト開始 ===")
        self.canvas.reset()

        # 各図形タイプでプレビューをテスト
        for shape_type in ["line", "rectangle", "circle", "polygon"]:
            self.canvas.mode = shape_type
            
            # 1点目を追加
            event = type('Event', (), {'x': 100, 'y': 100})()
            self.canvas.on_click(event)
            
            # マウス移動でプレビュー表示
            event = type('Event', (), {'x': 150, 'y': 150})()
            self.canvas.on_motion(event)
            
            # プレビューが存在することを確認
            preview = self.canvas.find_withtag("preview")
            assert len(preview) > 0, f"{shape_type}のプレビューが表示されていません"
            
            self.canvas.reset()
            
        logger.debug("=== プレビュー表示テスト終了 ===")

    def test_shape_completion(self):
        """図形の完成条件テスト"""
        logger.debug("=== 図形完成条件テスト開始 ===")
        self.canvas.reset()

        # 2点で完成する図形のテスト
        for shape_type in ["line", "rectangle", "circle"]:
            self.canvas.mode = shape_type
            
            # 1点追加では完成しない
            event = type('Event', (), {'x': 100, 'y': 100})()
            self.canvas.on_click(event)
            assert len(self.canvas.shapes) == 0
            
            # 2点目で完成
            event = type('Event', (), {'x': 200, 'y': 200})()
            self.canvas.on_click(event)
            assert len(self.canvas.shapes) == 1
            
            self.canvas.reset()

        # 多角形の完成条件テスト
        self.canvas.mode = "polygon"
        points = [(100, 100), (200, 100), (150, 200)]
        
        # 2点では完成しない
        for x, y in points[:2]:
            event = type('Event', (), {'x': x, 'y': y})()
            self.canvas.on_click(event)
        assert len(self.canvas.shapes) == 0
        
        # 3点目を追加
        event = type('Event', (), {'x': points[2][0], 'y': points[2][1]})()
        self.canvas.on_click(event)
        
        # 右クリックで完成
        event = type('Event', (), {'x': 0, 'y': 0})()
        self.canvas.on_right_click(event)
        assert len(self.canvas.shapes) == 1
        
        logger.debug("=== 図形完成条件テスト終了 ===")

    def test_shape_style(self):
        """図形のスタイル設定テスト"""
        logger.debug("=== 図形スタイルテスト開始 ===")
        self.canvas.reset()

        # 線の色を設定
        self.canvas.current_color = "red"
        self.canvas.current_width = 2
        self.canvas.mode = "line"

        # 線を描画
        event = type('Event', (), {'x': 100, 'y': 100})()
        self.canvas.on_click(event)
        event = type('Event', (), {'x': 200, 'y': 200})()
        self.canvas.on_click(event)

        # スタイルの確認
        shape = self.canvas.shapes[0]
        assert isinstance(shape, Line)
        assert shape.color == "red", "線の色が正しく設定されていません"
        assert shape.width == 2, "線の太さが正しく設定されていません"

        # 四角形のスタイル
        self.canvas.current_color = "blue"
        self.canvas.current_width = 3
        self.canvas.mode = "rectangle"

        # 四角形を描画
        event = type('Event', (), {'x': 300, 'y': 300})()
        self.canvas.on_click(event)
        event = type('Event', (), {'x': 400, 'y': 400})()
        self.canvas.on_click(event)

        # スタイルの確認
        shape = self.canvas.shapes[1]
        assert isinstance(shape, Rectangle)
        assert shape.color == "blue", "四角形の色が正しく設定されていません"
        assert shape.width == 3, "四角形の線の太さが正しく設定されていません"

        logger.debug("=== 図形スタイルテスト終了 ===")

    def test_line_style(self):
        """線スタイルのテスト"""
        logger.debug("=== 線スタイルテスト開始 ===")
        self.canvas.on_click(self.create_event(100, 100))
        self.canvas.on_click(self.create_event(200, 200))
        shape = self.canvas.shapes[-1]
        assert isinstance(shape, Line), "作成された図形が線分ではありません"
        assert shape.style is None, "デフォルトの線種が実線になっていません"
        logger.debug("=== 線スタイルテスト終了 ===")

    def test_snap(self):
        """スナップ機能のテスト"""
        self.logger.debug("=== スナップ機能テスト開始 ===")
        self.canvas.reset()

        # スナップ設定
        self.canvas.snap_enabled = True
        self.canvas.snap_types["endpoint"] = True
        self.canvas.snap_types["midpoint"] = True
        self.canvas.snap_types["intersection"] = True

        # エラーケースのテスト：交点がない場合
        # 平行な2本の線を描画
        line1 = Line(100, 100, 200, 100)
        line2 = Line(100, 200, 200, 200)
        self.canvas.shapes.append(line1)
        self.canvas.shapes.append(line2)

        # 交点を計算（空のリストが返されるはず）
        intersections = self.canvas.get_intersection_points(line1, line2)
        self.assertEqual(intersections, [], "平行線の交点は空のリストのはずです")

        # get_snap_pointを呼び出し
        event = type('Event', (), {'x': 150, 'y': 150})()
        snap_point = self.canvas.get_snap_point(event.x, event.y)
        self.assertIsNotNone(snap_point, "スナップポイントがNoneになってはいけません")

        # 端点スナップのテスト
        # 最初の線を描画
        line3 = Line(100, 300, 200, 400)
        self.canvas.shapes.append(line3)

        # 端点近くにマウスを移動
        event = type('Event', (), {'x': 98, 'y': 302})()  # 端点(100,300)の近く
        self.canvas.on_motion(event)
        snap_point = self.canvas.get_snap_point(event.x, event.y)
        self.assertEqual(snap_point, (100, 300), "端点へのスナップが機能していません")

        # 中点スナップのテスト
        event = type('Event', (), {'x': 148, 'y': 352})()  # 中点(150,350)の近く
        self.canvas.on_motion(event)
        snap_point = self.canvas.get_snap_point(event.x, event.y)
        self.assertEqual(snap_point, (150, 350), "中点へのスナップが機能していません")

        # 交点スナップのテスト
        # 2本目の線を描画（1本目と交差する）
        line4 = Line(100, 400, 200, 300)
        self.canvas.shapes.append(line4)

        # 交点近くにマウスを移動（交点は(150,350)のはず）
        event = type('Event', (), {'x': 148, 'y': 352})()
        self.canvas.on_motion(event)
        snap_point = self.canvas.get_snap_point(event.x, event.y)
        self.assertEqual(snap_point, (150, 350), "交点へのスナップが機能していません")

        # 円と直線の交点スナップのテスト
        self.canvas.reset()
        
        # 円を描画（中心(200,200)、半径50）
        circle = Circle(200, 200, 250, 200)
        self.canvas.shapes.append(circle)

        # 接線を描画
        line = Line(250, 150, 250, 250)
        self.canvas.shapes.append(line)

        # 交点を計算
        intersections = self.canvas.get_circle_line_intersection(line, circle)
        self.assertEqual(len(intersections), 1, "接線との交点は1点のはずです")

        # 交点の位置を検証
        x, y = intersections[0]
        r = math.sqrt((circle.x2 - circle.center_x) ** 2 + (circle.y2 - circle.center_y) ** 2)
        circle_eq = abs((x - circle.center_x) ** 2 + (y - circle.center_y) ** 2 - r * r)
        self.assertLess(circle_eq, 0.1, "交点が円上にありません")

        if line.x2 != line.x1:
            m = (line.y2 - line.y1) / (line.x2 - line.x1)
            b = line.y1 - m * line.x1
            line_eq = abs(y - (m * x + b))
            self.assertLess(line_eq, 0.1, "交点が直線上にありません")

        self.logger.debug("=== スナップ機能テスト終了 ===")

    def test_circle_line_intersection(self):
        """円と直線の交点計算のテスト"""
        self.logger.debug("=== 円と直線の交点計算テスト開始 ===")
        self.canvas.reset()

        # テストケース1: 2点で交差する場合
        # 中心(200,200)、半径50の円
        circle = Circle(200, 200, 250, 200)
        # 斜めの線（確実に2点で交差）
        line = Line(150, 150, 250, 250)
        
        # 交点を計算
        intersections = self.canvas.get_circle_line_intersection(line, circle)
        self.assertEqual(len(intersections), 2, "斜めの線との交点が2つあるはずです")

        # 交点が円周上にあることを確認
        r = math.sqrt((circle.x2 - circle.center_x) ** 2 + (circle.y2 - circle.center_y) ** 2)
        for x, y in intersections:
            # 円の方程式を満たすか確認
            dist_from_center = math.sqrt((x - circle.center_x) ** 2 + (y - circle.center_y) ** 2)
            self.assertAlmostEqual(dist_from_center, r, delta=0.1, 
                                 msg="交点が円周上にありません")
            
            # 直線上にあるか確認
            if abs(line.x2 - line.x1) > 0.1:  # 垂直でない場合
                m = (line.y2 - line.y1) / (line.x2 - line.x1)
                b = line.y1 - m * line.x1
                y_on_line = m * x + b
                self.assertAlmostEqual(y, y_on_line, delta=0.1,
                                     msg="交点が直線上にありません")

        # テストケース2: 接線の場合
        # 中心(200,200)、半径50の円に対する接線
        # 接点は(235.355, 235.355)となるように設定
        circle = Circle(200, 200, 250, 200)
        # 接線は(200,200)から50√2離れた点を通る
        line = Line(200, 200, 50, 50)  # この線は円に接する
        
        # 交点を計算
        intersections = self.canvas.get_circle_line_intersection(line, circle)
        self.assertEqual(len(intersections), 1, "接線との交点は1点のはずです")

        # 接点の位置を確認
        x, y = intersections[0]
        dist_from_center = math.sqrt((x - circle.center_x) ** 2 + (y - circle.center_y) ** 2)
        self.assertAlmostEqual(dist_from_center, r, delta=0.1,
                              msg="接点が円周上にありません")

        # テストケース3: 交点がない場合
        # 円から十分離れた線
        line = Line(300, 300, 400, 400)
        intersections = self.canvas.get_circle_line_intersection(line, circle)
        self.assertEqual(len(intersections), 0, "交点はないはずです")

        self.logger.debug("=== 円と直線の交点計算テスト終了 ===")

    def test_snap_integration(self):
        """スナップ機能の統合テスト"""
        self.logger.debug("=== スナップ機能統合テスト開始 ===")
        
        # 実際のアプリケーションを起動
        app = DrawingApp()
        
        # スナップ設定の初期状態を確認
        self.assertTrue(app.canvas.snap_enabled, "スナップが有効になっていません")
        self.assertTrue(app.canvas.snap_types["endpoint"], "端点スナップが有効になっていません")
        self.assertTrue(app.canvas.snap_types["midpoint"], "中点スナップが有効になっていません")
        self.assertTrue(app.canvas.snap_types["intersection"], "交点スナップが有効になっていません")
        
        # スナップ設定の切り替えテスト
        # スナップのオン/オフ
        app.toggle_snap()
        self.assertFalse(app.canvas.snap_enabled, "スナップの無効化が機能していません")
        app.toggle_snap()
        self.assertTrue(app.canvas.snap_enabled, "スナップの再有効化が機能していません")
        
        # 各スナップタイプの切り替え
        for snap_type in ["endpoint", "midpoint", "intersection"]:
            app.toggle_snap_type(snap_type)
            self.assertFalse(app.canvas.snap_types[snap_type], 
                            f"{snap_type}スナップの無効化が機能していません")
            app.toggle_snap_type(snap_type)
            self.assertTrue(app.canvas.snap_types[snap_type], 
                            f"{snap_type}スナップの再有効化が機能していません")
        
        # 実際の図形を描画してスナップ動作を確認
        app.canvas.mode = "line"
        
        # 1本目の線を描画
        event1 = type('Event', (), {'x': 100, 'y': 100})()
        event2 = type('Event', (), {'x': 200, 'y': 200})()
        app.canvas.on_click(event1)
        app.canvas.on_click(event2)
        
        # 2本目の線を描画（スナップを使用）
        # 1本目の端点近くにマウスを移動
        event3 = type('Event', (), {'x': 98, 'y': 102})()
        app.canvas.on_motion(event3)
        snap_point = app.canvas.get_snap_point(event3.x, event3.y)
        self.assertEqual(snap_point, (100, 100), 
                        "実際の描画時に端点スナップが機能していません")
        
        # 1本目の中点近くにマウスを移動
        event4 = type('Event', (), {'x': 148, 'y': 152})()
        app.canvas.on_motion(event4)
        snap_point = app.canvas.get_snap_point(event4.x, event4.y)
        self.assertEqual(snap_point, (150, 150), 
                        "実際の描画時に中点スナップが機能していません")
        
        # ステータスバーのメッセージを確認
        self.assertIn("スナップ", app.status_var.get(), 
                     "スナップ操作時のステータス表示が機能していません")
        
        app.root.destroy()
        self.logger.debug("=== スナップ機能統合テスト終了 ===")

    def test_circle_circle_intersection(self):
        """円同士の交点計算のテスト"""
        self.logger.debug("=== 円同士の交点計算テスト開始 ===")
        self.canvas.reset()

        # テストケース1: 2点で交差する場合
        circle1 = Circle(200, 200, 250, 200)  # 中心(200,200)、半径50の円
        circle2 = Circle(250, 200, 300, 200)  # 中心(250,200)、半径50の円
        
        # 交点を計算
        intersections = self.canvas.get_circle_circle_intersection(circle1, circle2)
        self.assertEqual(len(intersections), 2, "2つの円の交点が2つあるはずです")

        # 交点が両方の円周上にあることを確認
        r1 = math.sqrt((circle1.x2 - circle1.center_x) ** 2 + 
                      (circle1.y2 - circle1.center_y) ** 2)
        r2 = math.sqrt((circle2.x2 - circle2.center_x) ** 2 + 
                      (circle2.y2 - circle2.center_y) ** 2)
        
        for x, y in intersections:
            # 円1の方程式を満たすか確認
            dist1 = math.sqrt((x - circle1.center_x) ** 2 + (y - circle1.center_y) ** 2)
            self.assertAlmostEqual(dist1, r1, delta=0.1, 
                                 msg="交点が円1の円周上にありません")
            
            # 円2の方程式を満たすか確認
            dist2 = math.sqrt((x - circle2.center_x) ** 2 + (y - circle2.center_y) ** 2)
            self.assertAlmostEqual(dist2, r2, delta=0.1,
                                 msg="交点が円2の円周上にありません")

        # テストケース2: 1点で接する場合（外接）
        circle3 = Circle(200, 200, 250, 200)  # 中心(200,200)、半径50の円
        circle4 = Circle(300, 200, 350, 200)  # 中心(300,200)、半径50の円
        
        # 交点を計算
        intersections = self.canvas.get_circle_circle_intersection(circle3, circle4)
        self.assertEqual(len(intersections), 1, "接する円の交点は1点のはずです")

        # 接点が両方の円周上にあることを確認
        x, y = intersections[0]
        r3 = math.sqrt((circle3.x2 - circle3.center_x) ** 2 + 
                      (circle3.y2 - circle3.center_y) ** 2)
        r4 = math.sqrt((circle4.x2 - circle4.center_x) ** 2 + 
                      (circle4.y2 - circle4.center_y) ** 2)
        
        dist3 = math.sqrt((x - circle3.center_x) ** 2 + (y - circle3.center_y) ** 2)
        dist4 = math.sqrt((x - circle4.center_x) ** 2 + (y - circle4.center_y) ** 2)
        self.assertAlmostEqual(dist3, r3, delta=0.1, msg="接点が円3の円周上にありません")
        self.assertAlmostEqual(dist4, r4, delta=0.1, msg="接点が円4の円周上にありません")

        # テストケース3: 交点がない場合
        # 離れている円
        circle5 = Circle(200, 200, 250, 200)  # 中心(200,200)、半径50の円
        circle6 = Circle(400, 200, 450, 200)  # 中心(400,200)、半径50の円
        intersections = self.canvas.get_circle_circle_intersection(circle5, circle6)
        self.assertEqual(len(intersections), 0, "離れている円の交点はないはずです")

        # 内包する円
        circle7 = Circle(200, 200, 300, 200)  # 中心(200,200)、半径100の円
        circle8 = Circle(200, 200, 225, 200)  # 中心(200,200)、半径25の円
        intersections = self.canvas.get_circle_circle_intersection(circle7, circle8)
        self.assertEqual(len(intersections), 0, "内包する円の交点はないはずです")

        self.logger.debug("=== 円同士の交点計算テスト終了 ===")

    def test_polygon_preview(self):
        """多角形のプレビュー表示テスト"""
        self.logger.debug("=== 多角形プレビュー表示テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "polygon"

        # 1点目を追加
        event = type('Event', (), {'x': 100, 'y': 100})()
        self.canvas.on_click(event)
        
        # マウス移動でプレビュー表示（1点から現在位置までの線）
        event = type('Event', (), {'x': 150, 'y': 150})()
        self.canvas.on_motion(event)
        preview_lines = self.canvas.find_withtag("preview")
        self.assertEqual(len(preview_lines), 2, "1点目から現在位置までの線と閉じる線が表示されていません")

        # 2点目を追加
        event = type('Event', (), {'x': 200, 'y': 100})()
        self.canvas.on_click(event)
        
        # マウス移動でプレビュー表示（2点を結ぶ線と現在位置までの線）
        event = type('Event', (), {'x': 150, 'y': 200})()
        self.canvas.on_motion(event)
        preview_lines = self.canvas.find_withtag("preview")
        self.assertEqual(len(preview_lines), 3, "2点を結ぶ線と現在位置までの線が表示されていません")

        # 3点目を追加
        event = type('Event', (), {'x': 150, 'y': 200})()
        self.canvas.on_click(event)
        
        # マウス移動でプレビュー表示（3点を結ぶ線、現在位置までの線、最初の点までの点線）
        event = type('Event', (), {'x': 100, 'y': 150})()
        self.canvas.on_motion(event)
        preview_lines = self.canvas.find_withtag("preview")
        self.assertEqual(len(preview_lines), 5, "3点を結ぶ線、現在位置までの線、最初の点までの点線が表示されていません")

        # 右クリックで完成
        event = type('Event', (), {'x': 0, 'y': 0})()
        self.canvas.on_right_click(event)
        
        # プレビューが消えていることを確認
        preview_lines = self.canvas.find_withtag("preview")
        self.assertEqual(len(preview_lines), 0, "完成後もプレビューが残っています")
        
        # 完成した多角形が正しく描画されていることを確認
        shape = self.canvas.shapes[0]
        self.assertEqual(len(shape.points), 3, "頂点の数が正しくありません")
        
        self.logger.debug("=== 多角形プレビュー表示テスト終了 ===")

    def test_rectangle_line_intersection_snap(self):
        """矩形と線の交点スナップテスト"""
        self.logger.debug("=== 矩形と線の交点スナップテスト開始 ===")
        self.canvas.reset()

        # 矩形を描画
        rectangle = Rectangle(100, 100, 200, 200)
        self.canvas.shapes.append(rectangle)

        # 交差する線を描画
        line = Line(50, 150, 250, 150)
        self.canvas.shapes.append(line)

        # 交点を計算
        intersections = self.canvas.get_intersection_points(rectangle, line)
        self.assertEqual(len(intersections), 2, "矩形と線の交点が2つあるはずです")

        # 交点スナップの確認
        for x, y in intersections:
            event = type('Event', (), {'x': x, 'y': y})()
            self.canvas.on_motion(event)
            snap_point = self.canvas.get_snap_point(event.x, event.y)
            self.assertEqual(snap_point, (x, y), "交点へのスナップが機能していません")

        self.logger.debug("=== 矩形と線の交点スナップテスト終了 ===")

    def test_polygon_line_intersection_snap(self):
        """多角形と線の交点スナップテスト"""
        self.logger.debug("=== 多角形と線の交点スナップテスト開始 ===")
        self.canvas.reset()

        # 多角形を描画
        polygon = Polygon([(100, 100), (200, 100), (150, 200)])
        self.canvas.shapes.append(polygon)

        # 交差する線を描画
        line = Line(50, 150, 250, 150)
        self.canvas.shapes.append(line)

        # 交点を計算
        intersections = self.canvas.get_intersection_points(polygon, line)
        self.assertEqual(len(intersections), 2, "多角形と線の交点が2つあるはずです")

        # 交点スナップの確認
        for x, y in intersections:
            event = type('Event', (), {'x': x, 'y': y})()
            self.canvas.on_motion(event)
            snap_point = self.canvas.get_snap_point(event.x, event.y)
            self.assertEqual(snap_point, (x, y), "交点へのスナップが機能していません")

        self.logger.debug("=== 多角形と線の交点スナップテスト終了 ===")

    def test_shape_selection(self):
        """図形の選択機能のテスト"""
        logger.debug("=== 図形選択テスト開始 ===")
        self.canvas.reset()

        # テスト用の図形を作成
        line = Line(100, 100, 200, 200)
        rect = Rectangle(300, 100, 400, 200)
        circle = Circle(500, 150, 550, 150)
        self.canvas.shapes.extend([line, rect, circle])

        # 図形の選択テスト
        event = type('Event', (), {'x': 150, 'y': 150})()  # 線の上の点
        self.canvas.on_select(event)
        self.assertEqual(self.canvas.selected_shape, line, "線の選択に失敗しました")

        event = type('Event', (), {'x': 350, 'y': 100})()  # 四角形の上辺の点
        self.canvas.on_select(event)
        self.assertEqual(self.canvas.selected_shape, rect, "四角形の選択に失敗しました")

        event = type('Event', (), {'x': 550, 'y': 150})()  # 円周上の点
        self.canvas.on_select(event)
        self.assertEqual(self.canvas.selected_shape, circle, "円の選択に失敗しました")

        # 選択解除のテスト
        event = type('Event', (), {'x': 50, 'y': 50})()  # 図形のない場所
        self.canvas.on_select(event)
        self.assertIsNone(self.canvas.selected_shape, "選択解除に失敗しました")

        logger.debug("=== 図形選択テスト終了 ===")

    def test_shape_move(self):
        """図形の移動機能のテスト"""
        logger.debug("=== 図形移動テスト開始 ===")
        self.canvas.reset()
        
        # 矩形を作成
        self.canvas.mode = "rectangle"
        event1 = type('Event', (), {'x': 100, 'y': 100})()
        event2 = type('Event', (), {'x': 200, 'y': 200})()
        self.canvas.on_click(event1)
        self.canvas.on_click(event2)
        
        # 作成された矩形を取得
        rect = self.canvas.shapes[-1]
        self.assertIsInstance(rect, Rectangle, "選択された図形が矩形ではありません")
        
        # 移動前の状態を確認
        self.assertEqual(rect.x1, 100, "初期状態のx1座標が正しくありません")
        self.assertEqual(rect.y1, 100, "初期状態のy1座標が正しくありません")
        self.assertEqual(rect.x2, 200, "初期状態のx2座標が正しくありません")
        self.assertEqual(rect.y2, 200, "初期状態のy2座標が正しくありません")
        
        # 矩形を選択
        select_event = type('Event', (), {'x': 150, 'y': 100})()
        self.canvas.on_select(select_event)
        self.assertEqual(self.canvas.selected_shape, rect, "矩形の選択に失敗しました")
        
        # 移動の準備
        self.canvas.last_x = 150
        self.canvas.last_y = 100
        self.canvas.is_moving = True
        
        # 50ピクセル右下に移動
        drag_event = type('Event', (), {'x': 200, 'y': 150})()
        self.canvas.on_drag(drag_event)
        
        # 移動後の位置を確認
        self.assertEqual(rect.x1, 150, "移動後のx1座標が正しくありません")
        self.assertEqual(rect.y1, 150, "移動後のy1座標が正しくありません")
        self.assertEqual(rect.x2, 250, "移動後のx2座標が正しくありません")
        self.assertEqual(rect.y2, 250, "移動後のy2座標が正しくありません")
        
        logger.debug("=== 図形移動テスト終了 ===")

    def test_shape_resize(self):
        """図形のサイズ変更機能のテスト"""
        logger.debug("=== 図形サイズ変更テスト開始 ===")
        self.canvas.reset()
        
        # 矩形を作成
        self.canvas.mode = "rectangle"
        event1 = type('Event', (), {'x': 100, 'y': 100})()
        event2 = type('Event', (), {'x': 200, 'y': 200})()
        self.canvas.on_click(event1)
        self.canvas.on_click(event2)
        
        # 作成された矩形を取得
        rect = self.canvas.shapes[-1]
        self.assertIsInstance(rect, Rectangle, "作成された図形が矩形ではありません")
        
        # 矩形を選択（右下のハンドルを選択）
        select_event = type('Event', (), {'x': 200, 'y': 200})()
        self.canvas.on_select(select_event)
        self.assertEqual(self.canvas.selected_shape, rect, "矩形の選択に失敗しました")
        
        # リサイズの準備
        self.canvas.resize_handle = "se"  # 右下のハンドル
        self.canvas.is_resizing = True
        
        # リサイズ（右下に100ピクセル拡大）
        resize_event = type('Event', (), {'x': 300, 'y': 300})()
        self.canvas.resize_shape(resize_event.x, resize_event.y)
        
        # リサイズ後のサイズを確認
        self.assertEqual(rect.x1, 100, "リサイズ後のx1座標が正しくありません")
        self.assertEqual(rect.y1, 100, "リサイズ後のy1座標が正しくありません")
        self.assertEqual(rect.x2, 300, "リサイズ後のx2座標が正しくありません")
        self.assertEqual(rect.y2, 300, "リサイズ後のy2座標が正しくありません")
        
        logger.debug("=== 図形サイズ変更テスト終了 ===")

    def test_shape_resize_details(self):
        """図形のリサイズ機能の詳細テスト"""
        logger.debug("=== 図形リサイズ詳細テスト開始 ===")
        
        test_cases = [
            ("se", 300, 300, 100, 100, 300, 300),  # 右下に拡大
            ("sw", 50, 300, 50, 100, 200, 300),    # 左下に拡大
            ("ne", 300, 50, 100, 50, 300, 200),    # 右上に拡大
            ("nw", 50, 50, 50, 50, 200, 200),      # 左上に拡大
            ("n", 150, 50, 100, 50, 200, 200),     # 上に拡大（x座標は変更なし）
            ("s", 150, 300, 100, 100, 200, 300),   # 下に拡大（x座標は変更なし）
            ("e", 300, 150, 100, 100, 300, 200),   # 右に拡大（y座標は変更なし）
            ("w", 50, 150, 50, 100, 200, 200)      # 左に拡大（y座標は変更なし）
        ]
        
        for handle, x, y, exp_x1, exp_y1, exp_x2, exp_y2 in test_cases:
            # 各テストケースで新しい矩形を作成
            self.canvas.reset()
            self.canvas.mode = "rectangle"
            self.canvas.on_click(type('Event', (), {'x': 100, 'y': 100})())
            self.canvas.on_click(type('Event', (), {'x': 200, 'y': 200})())
            rect = self.canvas.shapes[-1]
            
            # リサイズの準備
            self.canvas.selected_shape = rect
            self.canvas.resize_handle = handle
            self.canvas.is_resizing = True
            
            # リサイズ実行
            self.canvas.resize_shape(x, y)
            
            # リサイズ後の座標をログ出力
            logger.debug(f"=== リサイズ結果（{handle}ハンドル） ===")
            logger.debug(f"期待値: x1={exp_x1}, y1={exp_y1}, x2={exp_x2}, y2={exp_y2}")
            logger.debug(f"実際値: x1={rect.x1}, y1={rect.y1}, x2={rect.x2}, y2={rect.y2}")
            
            # リサイズ後のサイズを確認
            self.assertEqual(rect.x1, exp_x1, f"{handle}ハンドルでのリサイズ後のx1座標が正しくありません")
            self.assertEqual(rect.y1, exp_y1, f"{handle}ハンドルでのリサイズ後のy1座標が正しくありません")
            self.assertEqual(rect.x2, exp_x2, f"{handle}ハンドルでのリサイズ後のx2座標が正しくありません")
            self.assertEqual(rect.y2, exp_y2, f"{handle}ハンドルでのリサイズ後のy2座標が正しくありません")
        
        logger.debug("=== 図形リサイズ詳細テスト終了 ===")

    def test_sw_handle_resize_sequence(self):
        """swハンドルのリサイズシーケンスの詳細テスト"""
        logger.debug("=== swハンドルリサイズシーケンステスト開始 ===")
        self.canvas.reset()
        
        # 矩形を作成（100,100 から 200,200）
        self.canvas.mode = "rectangle"
        self.canvas.on_click(type('Event', (), {'x': 100, 'y': 100})())
        self.canvas.on_click(type('Event', (), {'x': 200, 'y': 200})())
        rect = self.canvas.shapes[-1]
        
        # 初期状態の確認
        self.assertEqual((rect.x1, rect.y1, rect.x2, rect.y2), (100, 100, 200, 200),
                         "初期の矩形サイズが正しくありません")
        
        # 矩形を選択してswハンドルを設定
        self.canvas.selected_shape = rect
        self.canvas.resize_handle = "sw"
        self.canvas.is_resizing = True
        
        # テストシーケンス
        test_sequences = [
            # (移動先x, 移動先y, 期待されるx1, y1, x2, y2, 説明)
            (50, 300, 50, 100, 200, 300, "左下に拡大"),
            (150, 250, 150, 100, 200, 250, "右上に縮小"),
            (80, 280, 80, 100, 200, 280, "再度左下に拡大"),
            (120, 220, 120, 100, 200, 220, "少し右上に縮小")
        ]
        
        for x, y, exp_x1, exp_y1, exp_x2, exp_y2, desc in test_sequences:
            # リサイズ実行
            self.canvas.resize_shape(x, y)
            
            # 結果をログ出力
            logger.debug(f"=== {desc} ===")
            logger.debug(f"移動先: ({x}, {y})")
            logger.debug(f"期待値: x1={exp_x1}, y1={exp_y1}, x2={exp_x2}, y2={exp_y2}")
            logger.debug(f"実際値: x1={rect.x1}, y1={rect.y1}, x2={rect.x2}, y2={rect.y2}")
            
            # 座標を検証
            self.assertEqual(rect.x1, exp_x1, f"{desc}: x1座標が正しくありません")
            self.assertEqual(rect.y1, exp_y1, f"{desc}: y1座標が正しくありません")
            self.assertEqual(rect.x2, exp_x2, f"{desc}: x2座標が正しくありません")
            self.assertEqual(rect.y2, exp_y2, f"{desc}: y2座標が正しくありません")
        
        logger.debug("=== swハンドルリサイズシーケンステスト終了 ===")

    def test_resize_constraints(self):
        """リサイズ制約のテスト"""
        logger.debug("=== リサイズ制約テスト開始 ===")
        self.canvas.reset()
        
        # 矩形を作成（100,100 から 200,200）
        self.canvas.mode = "rectangle"
        self.canvas.on_click(type('Event', (), {'x': 100, 'y': 100})())
        self.canvas.on_click(type('Event', (), {'x': 200, 'y': 200})())
        rect = self.canvas.shapes[-1]
        
        # 矩形を選択
        self.canvas.selected_shape = rect
        self.canvas.is_resizing = True
        
        # 最小サイズ制約のテスト
        test_cases = [
            # (ハンドル, x, y, 期待されるx1, y1, x2, y2, 説明)
            ("sw", 195, 200, 190, 100, 200, 200, "最小幅（左）制約"),
            ("ne", 205, 100, 100, 100, 210, 200, "最小幅（右）制約"),
            ("nw", 100, 195, 100, 190, 200, 200, "最小高さ（上）制約"),
            ("se", 200, 205, 100, 100, 200, 210, "最小高さ（下）制約")
        ]
        
        for handle, x, y, exp_x1, exp_y1, exp_x2, exp_y2, desc in test_cases:
            # リサイズハンドルを設定
            self.canvas.resize_handle = handle
            
            # リサイズ実行
            self.canvas.resize_shape(x, y)
            
            # 結果をログ出力
            logger.debug(f"=== {desc} ===")
            logger.debug(f"ハンドル: {handle}, 移動先: ({x}, {y})")
            logger.debug(f"期待値: x1={exp_x1}, y1={exp_y1}, x2={exp_x2}, y2={exp_y2}")
            logger.debug(f"実際値: x1={rect.x1}, y1={rect.y1}, x2={rect.x2}, y2={rect.y2}")
            
            # 座標を検証
            self.assertGreaterEqual(abs(rect.x2 - rect.x1), self.canvas.MIN_SIZE,
                                  f"{desc}: 幅が最小サイズ未満です")
            self.assertGreaterEqual(abs(rect.y2 - rect.y1), self.canvas.MIN_SIZE,
                                  f"{desc}: 高さが最小サイズ未満です")
        
        logger.debug("=== リサイズ制約テスト終了 ===")

    def test_resize_handle_selection(self):
        """リサイズハンドルの選択テスト"""
        logger.debug("=== リサイズハンドル選択テスト開始 ===")
        self.canvas.reset()
        
        # 矩形を作成（100,100 から 200,200）
        self.canvas.mode = "rectangle"
        self.canvas.on_click(type('Event', (), {'x': 100, 'y': 100})())
        self.canvas.on_click(type('Event', (), {'x': 200, 'y': 200})())
        rect = self.canvas.shapes[-1]
        
        # 矩形を選択
        self.canvas.selected_shape = rect
        
        # 各ハンドルの選択をテスト
        test_cases = [
            # (クリック位置x, y, 期待されるハンドル, 説明)
            (100, 100, "nw", "左上ハンドル"),
            (150, 100, "n", "上中央ハンドル"),
            (200, 100, "ne", "右上ハンドル"),
            (200, 150, "e", "右中央ハンドル"),
            (200, 200, "se", "右下ハンドル"),
            (150, 200, "s", "下中央ハンドル"),
            (100, 200, "sw", "左下ハンドル"),
            (100, 150, "w", "左中央ハンドル"),
            (150, 150, None, "ハンドルのない位置")
        ]
        
        for x, y, expected_handle, desc in test_cases:
            # ハンドル選択
            actual_handle = self.canvas.get_resize_handle_at_point(x, y)
            
            # 結果をログ出力
            logger.debug(f"=== {desc} ===")
            logger.debug(f"クリック位置: ({x}, {y})")
            logger.debug(f"期待されるハンドル: {expected_handle}")
            logger.debug(f"実際のハンドル: {actual_handle}")
            
            # 検証
            self.assertEqual(actual_handle, expected_handle,
                            f"{desc}: 選択されたハンドルが正しくありません")
        
        logger.debug("=== リサイズハンドル選択テスト終了 ===")

    def test_line_endpoint_move(self):
        """線分の端点移動テスト"""
        logger.debug("=== 線分端点移動テスト開始 ===")
        self.canvas.reset()
        
        # 線分を作成
        line = Line(100, 100, 200, 200)
        self.canvas.shapes.append(line)
        
        # 移動前の状態を確認
        self.assertEqual(line.x1, 100, "初期状態の始点のx座標が正しくありません")
        self.assertEqual(line.y1, 100, "初期状態の始点のy座標が正しくありません")
        self.assertEqual(line.x2, 200, "初期状態の終点のx座標が正しくありません")
        self.assertEqual(line.y2, 200, "初期状態の終点のy座標が正しくありません")
        
        # 端点を選択
        event = type('Event', (), {'x': 100, 'y': 100})()  # 始点
        self.canvas.on_select(event)
        self.assertEqual(self.canvas.selected_shape, line, "線分の選択に失敗しました")
        
        # 端点を移動
        self.canvas.last_x = 100
        self.canvas.last_y = 100
        event = type('Event', (), {'x': 150, 'y': 150})()
        self.canvas.on_drag(event)
        
        # 移動後の状態を確認
        self.assertEqual(line.x1, 150, "始点のx座標が正しく更新されていません")
        self.assertEqual(line.y1, 150, "始点のy座標が正しく更新されていません")
        self.assertEqual(line.x2, 200, "終点のx座標が変更されています")
        self.assertEqual(line.y2, 200, "終点のy座標が変更されています")
        
        logger.debug("=== 線分端点移動テスト終了 ===")

    def test_shape_selection_display(self):
        """図形選択表示のテスト"""
        logger.debug("=== 図形選択表示テスト開始 ===")
        self.canvas.reset()
        
        # テスト用の図形を作成
        rect = Rectangle(300, 100, 400, 200)
        self.canvas.shapes.append(rect)
        
        # 矩形の辺上でのテスト
        test_points = [
            (350, 100, "上辺"),
            (400, 150, "右辺"),
            (350, 200, "下辺"),
            (300, 150, "左辺")
        ]
        
        for x, y, edge_name in test_points:
            logger.debug(f"{edge_name}での選択テスト")
            event = type('Event', (), {'x': x, 'y': y})()
            self.canvas.on_select(event)
            
            # 選択の確認
            self.assertEqual(self.canvas.selected_shape, rect, f"{edge_name}での選択に失敗しました")
            
            # 選択表示の確認
            selection_outline = self.canvas.find_withtag("selection_outline")
            logger.debug(f"{edge_name}での選択表示アイテム数: {len(selection_outline)}")
            for item in selection_outline:
                item_type = self.canvas.type(item)
                coords = self.canvas.coords(item)
                logger.debug(f"アイテムタイプ: {item_type}, 座標: {coords}")
            self.assertGreater(len(selection_outline), 0, f"{edge_name}での選択表示が描画されていません")
            
            # 選択を解除
            event = type('Event', (), {'x': 0, 'y': 0})()
            self.canvas.on_select(event)
            self.assertIsNone(self.canvas.selected_shape, f"{edge_name}での選択解除に失敗しました")
        
        logger.debug("=== 図形選択表示テスト終了 ===")

    def test_circle_creation(self):
        """円の生成テスト"""
        logger.debug("=== 円生成テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "circle"
        
        # 中心点を設定
        event = type('Event', (), {'x': 200, 'y': 200})()
        self.canvas.on_click(event)
        self.assertEqual(len(self.canvas.current_points), 1, "中心点が設定されていません")
        
        # 半径を決める点を設定
        event = type('Event', (), {'x': 250, 'y': 200})()
        self.canvas.on_click(event)
        
        # 円が生成されたことを確認
        self.assertEqual(len(self.canvas.shapes), 1, "円が生成されていません")
        circle = self.canvas.shapes[0]
        self.assertIsInstance(circle, Circle, "生成された図形が円ではありません")
        
        # 円の属性を確認
        self.assertEqual(circle.center_x, 200, "中心のx座標が正しくありません")
        self.assertEqual(circle.center_y, 200, "中心のy座標が正しくありません")
        self.assertEqual(circle.radius, 50, "半径が正しくありません")
        
        logger.debug("=== 円生成テスト終了 ===")

    def test_polygon_creation(self):
        """多角形の生成テスト"""
        logger.debug("=== 多角形生成テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "polygon"
        
        # 頂点を追加
        points = [(100, 100), (200, 100), (150, 200)]
        for x, y in points:
            event = type('Event', (), {'x': x, 'y': y})()
            self.canvas.on_click(event)
            self.assertIn((x, y), self.canvas.current_points, "頂点が追加されていません")
        
        # 右クリックで多角形を完成
        event = type('Event', (), {'x': 0, 'y': 0})()
        self.canvas.on_right_click(event)
        
        # 多角形が生成されたことを確認
        self.assertEqual(len(self.canvas.shapes), 1, "多角形が生成されていません")
        polygon = self.canvas.shapes[0]
        self.assertIsInstance(polygon, Polygon, "生成された図形が多角形ではありません")
        
        # 頂点の確認
        self.assertEqual(len(polygon.points), 3, "頂点の数が正しくありません")
        self.assertEqual(polygon.points, points, "頂点の座標が正しくありません")
        
        logger.debug("=== 多角形生成テスト終了 ===")

    def test_rectangle_resize_sequence(self):
        """四角形のリサイズシーケンスの詳細テスト"""
        logger.debug("=== 四角形リサイズシーケンステスト開始 ===")
        
        # テストケースを定義
        test_cases = [
            ResizeTestCase(
                name="右下に拡大",
                initial=RectState(100, 100, 200, 200),
                action=ResizeAction("se", 300, 300, "右下ハンドルで拡大"),
                expected=RectState(100, 100, 300, 300)
            ),
            ResizeTestCase(
                name="左下に拡大",
                initial=RectState(100, 100, 200, 200),
                action=ResizeAction("sw", 50, 300, "左下ハンドルで拡大"),
                expected=RectState(50, 100, 200, 300)
            ),
            ResizeTestCase(
                name="右上に拡大",
                initial=RectState(100, 100, 200, 200),
                action=ResizeAction("ne", 300, 50, "右上ハンドルで拡大"),
                expected=RectState(100, 50, 300, 200)
            ),
            ResizeTestCase(
                name="左上に拡大",
                initial=RectState(100, 100, 200, 200),
                action=ResizeAction("nw", 50, 50, "左上ハンドルで拡大"),
                expected=RectState(50, 50, 200, 200)
            )
        ]

        for case in test_cases:
            with self.subTest(case.name):
                # テストケースの内容をログに出力
                case.log_test_case()
                
                # キャンバスをリセット
                self.canvas.reset()
                
                # 初期状態の四角形を作成
                rect = Rectangle(
                    case.initial.x1, case.initial.y1,
                    case.initial.x2, case.initial.y2
                )
                self.canvas.shapes.append(rect)
                self.canvas.selected_shape = rect
                
                # リサイズ操作を実行
                self.canvas.resize_handle = case.action.handle
                self.canvas.resize_shape(case.action.to_x, case.action.to_y)
                
                # 実際の結果をログに出力
                actual = RectState(rect.x1, rect.y1, rect.x2, rect.y2)
                logger.debug(f"実際値: {actual}")
                
                # 結果を検証
                self.assertEqual(rect.x1, case.expected.x1, f"{case.name}: x1座標が正しくありません")
                self.assertEqual(rect.y1, case.expected.y1, f"{case.name}: y1座標が正しくありません")
                self.assertEqual(rect.x2, case.expected.x2, f"{case.name}: x2座標が正しくありません")
                self.assertEqual(rect.y2, case.expected.y2, f"{case.name}: y2座標が正しくありません")
        
        logger.debug("=== 四角形リサイズシーケンステスト終了 ===")

    def test_line_coordinate_persistence(self):
        """線分の座標保持テスト"""
        logger.debug("=== 線分座標保持テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "line"
        
        # 線分を作成
        start_x, start_y = 100, 100
        end_x, end_y = 200, 200
        
        # 1点目を追加
        event1 = type('Event', (), {'x': start_x, 'y': start_y})()
        self.canvas.on_click(event1)
        
        # 2点目を追加
        event2 = type('Event', (), {'x': end_x, 'y': end_y})()
        self.canvas.on_click(event2)
        
        # 作成された線分を取得
        line = self.canvas.shapes[-1]
        
        # 初期座標を保存
        initial_coords = (line.x1, line.y1, line.x2, line.y2)
        
        # キャンバスの再描画
        self.canvas.redraw()
        
        # 座標が変化していないことを確認
        self.assertEqual((line.x1, line.y1, line.x2, line.y2), initial_coords,
                        "再描画後に線分の座標が変化しています")
        
        # 別の図形を追加
        self.canvas.mode = "rectangle"
        event3 = type('Event', (), {'x': 300, 'y': 300})()
        event4 = type('Event', (), {'x': 400, 'y': 400})()
        self.canvas.on_click(event3)
        self.canvas.on_click(event4)
        
        # 再度座標を確認
        self.assertEqual((line.x1, line.y1, line.x2, line.y2), initial_coords,
                        "他の図形追加後に線分の座標が変化しています")
        
        logger.debug("=== 線分座標保持テスト終了 ===")

    def test_circle_creation_and_modification(self):
        """円の生成と編集テスト"""
        logger.debug("=== 円の生成と編集テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "circle"
        
        # 円を生成
        center_x, center_y = 200, 200
        radius_x, radius_y = 250, 200  # 半径50の円
        
        # 中心点を設定
        event1 = type('Event', (), {'x': center_x, 'y': center_y})()
        self.canvas.on_click(event1)
        
        # 半径点を設定
        event2 = type('Event', (), {'x': radius_x, 'y': radius_y})()
        self.canvas.on_click(event2)
        
        # 生成された円を取得
        circle = self.canvas.shapes[-1]
        self.assertIsInstance(circle, Circle, "生成された図形が円ではありません")
        
        # 円の属性を確認
        self.assertEqual(circle.center_x, center_x, "中心のx座標が正しくありません")
        self.assertEqual(circle.center_y, center_y, "中心のy座標が正しくありません")
        self.assertEqual(circle.radius, 50, "半径が正しくありません")
        
        # 円を選択
        self.canvas.selected_shape = circle
        
        # 円の移動をテスト
        dx, dy = 50, 50
        self.canvas.move_shape(dx, dy)
        
        # 移動後の位置を確認
        self.assertEqual(circle.center_x, center_x + dx, "移動後の中心x座標が正しくありません")
        self.assertEqual(circle.center_y, center_y + dy, "移動後の中心y座標が正しくありません")
        
        logger.debug("=== 円の生成と編集テスト終了 ===")

    def test_polygon_creation_and_modification(self):
        """多角形の生成と編集テスト"""
        logger.debug("=== 多角形の生成と編集テスト開始 ===")
        self.canvas.reset()
        self.canvas.mode = "polygon"
        
        # 多角形の頂点
        points = [(100, 100), (200, 100), (150, 200)]
        
        # 頂点を順番に追加
        for x, y in points:
            event = type('Event', (), {'x': x, 'y': y})()
            self.canvas.on_click(event)
            
        # プレビューの状態を確認
        preview_items = self.canvas.find_withtag("preview")
        self.assertGreater(len(preview_items), 0, "プレビューが表示されていません")
        
        # 右クリックで多角形を完成
        event = type('Event', (), {'x': 0, 'y': 0})()
        self.canvas.on_right_click(event)
        
        # 生成された多角形を取得
        polygon = self.canvas.shapes[-1]
        self.assertIsInstance(polygon, Polygon, "生成された図形が多角形ではありません")
        
        # 頂点の確認
        self.assertEqual(polygon.points, points, "頂点の座標が正しくありません")
        
        # 多角形を選択
        self.canvas.selected_shape = polygon
        
        # 多角形の移動をテスト
        dx, dy = 50, 50
        self.canvas.move_shape(dx, dy)
        
        # 移動後の頂点を確認
        expected_points = [(x + dx, y + dy) for x, y in points]
        self.assertEqual(polygon.points, expected_points, "移動後の頂点座標が正しくありません")
        
        logger.debug("=== 多角形の生成と編集テスト終了 ===")

    def test_circle_display(self):
        """円の生成と表示のテスト"""
        logger.debug("=== 円の生成と表示テスト開始 ===")
        
        # 円の描画モードに設定
        self.canvas.mode = "circle"
        
        # 中心点をクリック
        center_x, center_y = 100, 100
        event = self.create_event(center_x, center_y)
        self.canvas.on_click(event)
        
        # 半径を決める点をクリック
        radius_x, radius_y = 150, 100
        event = self.create_event(radius_x, radius_y)
        self.canvas.on_click(event)
        
        # 円が生成されていることを確認
        self.assertEqual(len(self.canvas.shapes), 1, "円が生成されていません")
        circle = self.canvas.shapes[0]
        self.assertIsInstance(circle, Circle, "生成された図形が円ではありません")
        
        # 円の属性を確認
        self.assertEqual(circle.center_x, center_x, "中心のX座標が正しくありません")
        self.assertEqual(circle.center_y, center_y, "中心のY座標が正しくありません")
        self.assertEqual(circle.radius, 50, "半径が正しくありません")
        
        logger.debug("=== 円の生成と表示テスト終了 ===")

    def test_polygon_display(self):
        """多角形の生成と表示のテスト"""
        logger.debug("=== 多角形の生成と表示テスト開始 ===")
        
        # 多角形の描画モードに設定
        self.canvas.mode = "polygon"
        
        # 頂点を追加
        points = [(100, 100), (200, 100), (200, 200)]
        for x, y in points:
            event = self.create_event(x, y)
            self.canvas.on_click(event)
        
        # 右クリックで多角形を完成
        event = self.create_event(0, 0)
        self.canvas.on_right_click(event)
        
        # 多角形が生成されていることを確認
        self.assertEqual(len(self.canvas.shapes), 1, "多角形が生成されていません")
        polygon = self.canvas.shapes[0]
        self.assertIsInstance(polygon, Polygon, "生成された図形が多角形ではありません")
        
        # 頂点の確認
        self.assertEqual(polygon.points, points, "頂点の座標が正しくありません")
        
        # 多角形を選択
        self.canvas.selected_shape = polygon
        
        # 多角形の移動をテスト
        dx, dy = 50, 50
        self.canvas.move_shape(dx, dy)
        
        # 移動後の頂点を確認
        expected_points = [(x + dx, y + dy) for x, y in points]
        self.assertEqual(polygon.points, expected_points, "移動後の頂点座標が正しくありません")
        
        logger.debug("=== 多角形の生成と表示テスト終了 ===")

    def test_mode_change_clears_selection(self):
        """描画モード変更時の選択解除テスト"""
        logger.debug("=== モード変更時の選択解除テスト開始 ===")
        
        # 四角形を描画
        self.canvas.mode = "rectangle"
        event1 = self.create_event(100, 100)
        self.canvas.on_click(event1)
        event2 = self.create_event(200, 200)
        self.canvas.on_click(event2)
        
        # 四角形を選択
        rect = self.canvas.shapes[0]
        self.canvas.selected_shape = rect
        
        # 描画モードを変更
        self.canvas.mode = "line"
        
        # 選択が解除されていることを確認
        self.assertIsNone(self.canvas.selected_shape, "モード変更後も選択が解除されていません")
        
        logger.debug("=== モード変更時の選択解除テスト終了 ===")

    def test_rectangle_resize(self):
        """四角形のリサイズ操作テスト"""
        logger.debug("=== 四角形のリサイズテスト開始 ===")
        
        # 四角形を描画
        self.canvas.mode = "rectangle"
        event1 = self.create_event(100, 100)
        self.canvas.on_click(event1)
        event2 = self.create_event(200, 200)
        self.canvas.on_click(event2)
        
        # 四角形を選択
        rect = self.canvas.shapes[0]
        self.canvas.selected_shape = rect
        
        # 右上（ne）ハンドルをドラッグ
        handle_x, handle_y = 200, 100  # 右上の座標
        event = self.create_event(handle_x, handle_y)
        self.canvas.resize_handle = "ne"
        self.canvas.is_resizing = True
        self.canvas.last_x = handle_x
        self.canvas.last_y = handle_y
        
        # ハンドルを新しい位置にドラッグ
        new_x, new_y = 300, 50
        drag_event = self.create_event(new_x, new_y)
        self.canvas.on_drag(drag_event)
        
        # リサイズ後の座標を確認
        self.assertEqual(rect.x1, 100, "左端のX座標が変更されています")
        self.assertEqual(rect.y1, 50, "上端のY座標が正しくありません")
        self.assertEqual(rect.x2, 300, "右端のX座標が正しくありません")
        self.assertEqual(rect.y2, 200, "下端のY座標が変更されています")
        
        logger.debug("=== 四角形のリサイズテスト終了 ===")

    def tearDown(self):
        """テスト終了時の処理"""
        self.root.destroy()

if __name__ == '__main__':
    unittest.main() 