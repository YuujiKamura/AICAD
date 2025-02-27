import tkinter as tk
from drawing_canvas import DrawingCanvas
import logging
import traceback
import sys

# ログの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_app.log')
    ]
)

class TestApp:
    def __init__(self):
        try:
            logging.info("アプリケーションの初期化を開始")
            self.root = tk.Tk()
            self.root.title("描画キャンバステスト")
            
            # メインツールバーの作成
            logging.debug("メインツールバーの作成")
            main_toolbar = tk.Frame(self.root)
            main_toolbar.pack(side=tk.TOP, fill=tk.X)
            
            # 描画スタイル選択
            style_frame = tk.LabelFrame(main_toolbar, text="描画スタイル")
            style_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            self.draw_style = tk.StringVar(value="click")
            tk.Radiobutton(style_frame, text="クリック", variable=self.draw_style, 
                          value="click", command=self.update_draw_style).pack(side=tk.LEFT)
            tk.Radiobutton(style_frame, text="ドラッグ", variable=self.draw_style, 
                          value="drag", command=self.update_draw_style).pack(side=tk.LEFT)
            
            # 描画モードボタン
            logging.debug("描画モードボタンの作成")
            mode_frame = tk.LabelFrame(main_toolbar, text="描画モード")
            mode_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            modes = [
                ("線", "line"),
                ("四角形", "rectangle"),
                ("円", "circle"),
                ("多角形", "polygon"),
                ("スプライン", "spline")
            ]
            for label, mode in modes:
                btn = tk.Button(mode_frame, text=label, command=lambda m=mode: self.set_mode(m))
                btn.pack(side=tk.LEFT, padx=2)
            
            # スナップ設定
            logging.debug("スナップ設定の作成")
            snap_frame = tk.LabelFrame(main_toolbar, text="スナップ")
            snap_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            # スナップの有効/無効
            self.snap_var = tk.BooleanVar(value=True)
            snap_cb = tk.Checkbutton(snap_frame, text="スナップ有効", 
                                   variable=self.snap_var,
                                   command=self.toggle_snap)
            snap_cb.pack(side=tk.LEFT)
            
            # スナップタイプ
            snap_types = [
                ("端点", "endpoint"),
                ("中点", "midpoint"),
                ("交点", "intersection"),
                ("グリッド", "grid")
            ]
            self.snap_type_vars = {}
            for label, snap_type in snap_types:
                var = tk.BooleanVar(value=True)
                self.snap_type_vars[snap_type] = var
                cb = tk.Checkbutton(snap_frame, text=label, 
                                  variable=var,
                                  command=lambda t=snap_type: self.toggle_snap_type(t))
                cb.pack(side=tk.LEFT)
            
            # 表示設定
            logging.debug("表示設定の作成")
            view_frame = tk.LabelFrame(main_toolbar, text="表示")
            view_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            # グリッド表示
            self.grid_var = tk.BooleanVar(value=False)
            grid_cb = tk.Checkbutton(view_frame, text="グリッド表示", 
                                   variable=self.grid_var,
                                   command=self.toggle_grid)
            grid_cb.pack(side=tk.LEFT)
            
            # 寸法線表示
            self.dimension_var = tk.BooleanVar(value=True)
            dimension_cb = tk.Checkbutton(view_frame, text="寸法線表示",
                                        variable=self.dimension_var,
                                        command=self.toggle_dimensions)
            dimension_cb.pack(side=tk.LEFT)
            
            # グリッドサイズ
            tk.Label(view_frame, text="グリッドサイズ:").pack(side=tk.LEFT)
            self.grid_size_var = tk.StringVar(value="20")
            grid_size_entry = tk.Entry(view_frame, textvariable=self.grid_size_var, width=4)
            grid_size_entry.pack(side=tk.LEFT)
            grid_size_entry.bind('<Return>', self.update_grid_size)
            
            # ビューリセット
            reset_btn = tk.Button(view_frame, text="ビューリセット", 
                                command=lambda: self.canvas.reset_view())
            reset_btn.pack(side=tk.LEFT, padx=5)
            
            # キャンバスの作成
            logging.debug("キャンバスの作成")
            self.canvas = DrawingCanvas(self.root, width=800, height=600, bg="white")
            self.canvas.pack(expand=True, fill=tk.BOTH)
            
            # アンドゥ/リドゥボタン
            logging.debug("アンドゥ/リドゥボタンの作成")
            edit_frame = tk.Frame(main_toolbar)
            edit_frame.pack(side=tk.RIGHT, padx=5)
            
            undo_btn = tk.Button(edit_frame, text="元に戻す", command=self.undo)
            undo_btn.pack(side=tk.LEFT)
            redo_btn = tk.Button(edit_frame, text="やり直し", command=self.redo)
            redo_btn.pack(side=tk.LEFT)
            
            # ステータスバーの作成
            logging.debug("ステータスバーの作成")
            self.status_var = tk.StringVar()
            self.status_var.set("準備完了")
            self.statusbar = tk.Label(self.root, textvariable=self.status_var, 
                                    bd=1, relief=tk.SUNKEN, anchor=tk.W)
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # キャンバスにステータス更新コールバックを設定
            self.canvas.set_status_callback(self.update_status)
            
            logging.info("アプリケーションの初期化が完了")
            
        except Exception as e:
            logging.error(f"初期化中にエラーが発生: {str(e)}")
            logging.error(traceback.format_exc())
            raise
    
    def toggle_snap(self):
        """スナップの有効/無効を切り替え"""
        try:
            self.canvas.snap_enabled = self.snap_var.get()
            state = "有効" if self.canvas.snap_enabled else "無効"
            self.update_status(f"スナップを{state}にしました")
        except Exception as e:
            logging.error(f"スナップ切り替え中にエラー: {str(e)}")
            logging.error(traceback.format_exc())
    
    def toggle_snap_type(self, snap_type):
        """スナップタイプの有効/無効を切り替え"""
        try:
            self.canvas.snap_types[snap_type] = self.snap_type_vars[snap_type].get()
            state = "有効" if self.canvas.snap_types[snap_type] else "無効"
            self.update_status(f"{snap_type}スナップを{state}にしました")
        except Exception as e:
            logging.error(f"スナップタイプ切り替え中にエラー: {str(e)}")
            logging.error(traceback.format_exc())
    
    def toggle_grid(self):
        """グリッド表示の切り替え"""
        try:
            if self.grid_var.get():
                self.draw_grid()
            else:
                self.canvas.delete("grid")
            self.update_status("グリッド表示を切り替えました")
        except Exception as e:
            logging.error(f"グリッド表示切り替え中にエラー: {str(e)}")
            logging.error(traceback.format_exc())
    
    def update_grid_size(self, event=None):
        """グリッドサイズの更新"""
        try:
            size = int(self.grid_size_var.get())
            if size > 0:
                self.canvas.grid_size = size
                if self.grid_var.get():
                    self.draw_grid()
                self.update_status(f"グリッドサイズを{size}に更新しました")
            else:
                self.update_status("グリッドサイズは正の整数を指定してください")
        except ValueError:
            self.update_status("無効なグリッドサイズです")
        except Exception as e:
            logging.error(f"グリッドサイズ更新中にエラー: {str(e)}")
            logging.error(traceback.format_exc())
    
    def draw_grid(self):
        """グリッドを描画"""
        try:
            self.canvas.delete("grid")
            
            # キャンバスのサイズを取得
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            # グリッドサイズを取得
            grid_size = self.canvas.grid_size
            
            # 垂直線を描画
            for x in range(0, width, grid_size):
                self.canvas.create_line(x, 0, x, height, 
                                     fill="lightgray", tags="grid")
            
            # 水平線を描画
            for y in range(0, height, grid_size):
                self.canvas.create_line(0, y, width, y, 
                                     fill="lightgray", tags="grid")
            
            # 原点を強調表示
            self.canvas.create_line(0, 0, width, 0, 
                                  fill="gray", width=2, tags="grid")
            self.canvas.create_line(0, 0, 0, height, 
                                  fill="gray", width=2, tags="grid")
            
        except Exception as e:
            logging.error(f"グリッド描画中にエラー: {str(e)}")
            logging.error(traceback.format_exc())
    
    def update_status(self, message):
        """ステータスバーのメッセージを更新"""
        try:
            self.status_var.set(message)
        except Exception as e:
            logging.error(f"ステータス更新中にエラーが発生: {str(e)}")
    
    def set_mode(self, mode):
        """描画モードを設定"""
        try:
            logging.info(f"描画モードを変更: {mode}")
            self.canvas.set_mode(mode)
            mode_names = {
                "line": "線",
                "rectangle": "四角形",
                "circle": "円",
                "polygon": "多角形",
                "spline": "スプライン"
            }
            mode_instructions = {
                "line": "左クリックで始点を指定し、右クリックで終点を指定してください",
                "rectangle": "左クリックで1点目を指定し、右クリックで対角点を指定してください",
                "circle": "左クリックで中心を指定し、右クリックで半径を指定してください",
                "polygon": "左クリックで頂点を追加し、右クリックで多角形を完成させてください",
                "spline": "左クリックで制御点を追加し、右クリックでスプライン曲線を完成させてください"
            }
            self.update_status(f"{mode_names.get(mode, mode)}モード - {mode_instructions.get(mode, '')}")
        except Exception as e:
            logging.error(f"モード変更中にエラーが発生: {str(e)}")
            logging.error(traceback.format_exc())
    
    def undo(self):
        """アンドゥを実行"""
        try:
            logging.info("アンドゥを実行")
            self.canvas.undo()
            self.update_status("操作を元に戻しました")
        except Exception as e:
            logging.error(f"アンドゥ中にエラーが発生: {str(e)}")
            logging.error(traceback.format_exc())
    
    def redo(self):
        """リドゥを実行"""
        try:
            logging.info("リドゥを実行")
            self.canvas.redo()
            self.update_status("操作をやり直しました")
        except Exception as e:
            logging.error(f"リドゥ中にエラーが発生: {str(e)}")
            logging.error(traceback.format_exc())
    
    def toggle_dimensions(self):
        """寸法線表示の切り替え"""
        try:
            self.canvas.show_dimensions = self.dimension_var.get()
            self.canvas.redraw_all_shapes()
            state = "表示" if self.canvas.show_dimensions else "非表示"
            self.update_status(f"寸法線を{state}にしました")
        except Exception as e:
            logging.error(f"寸法線表示切り替え中にエラー: {str(e)}")
            logging.error(traceback.format_exc())
    
    def update_draw_style(self):
        """描画スタイルを更新"""
        try:
            style = self.draw_style.get()
            self.canvas.set_draw_style(style)
            style_names = {
                "click": "クリック",
                "drag": "ドラッグ"
            }
            self.update_status(f"描画スタイルを{style_names.get(style, style)}に変更しました")
        except Exception as e:
            logging.error(f"描画スタイル更新中にエラー: {str(e)}")
            logging.error(traceback.format_exc())
    
    def run(self):
        try:
            logging.info("アプリケーションを起動")
            self.root.mainloop()
        except Exception as e:
            logging.error(f"実行中にエラーが発生: {str(e)}")
            logging.error(traceback.format_exc())
            raise

if __name__ == "__main__":
    try:
        logging.info("プログラムを開始")
        app = TestApp()
        app.run()
    except Exception as e:
        logging.error(f"予期せぬエラーが発生: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(1) 