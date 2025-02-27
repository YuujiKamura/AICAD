import tkinter as tk
from tkinter import ttk
import logging
from drawing_canvas import DrawingCanvas

# ロガーの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DrawingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("描画アプリケーション")
        
        # メインフレーム
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # ツールバー
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(side="top", fill="x", pady=5)
        
        # 描画モードボタン
        self.create_mode_buttons()
        
        # 色と線種の設定
        self.create_appearance_settings()
        
        # スナップ設定
        self.create_snap_settings()
        
        # 表示設定
        self.create_display_settings()
        
        # キャンバス
        self.canvas = DrawingCanvas(self.main_frame, width=800, height=600, bg="white")
        self.canvas.pack(expand=True, fill="both")
        
        # アンドゥ/リドゥボタン
        self.create_undo_redo_buttons()
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        self.statusbar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        self.statusbar.pack(side="bottom", fill="x")

    def create_mode_buttons(self):
        mode_frame = ttk.LabelFrame(self.toolbar, text="描画モード")
        mode_frame.pack(side="left", padx=5)
        
        modes = [
            ("線", "line"),
            ("四角形", "rectangle"),
            ("円", "circle"),
            ("多角形", "polygon")
        ]
        
        for text, mode in modes:
            btn = ttk.Button(mode_frame, text=text, command=lambda m=mode: self.set_mode(m))
            btn.pack(side="left", padx=2)

    def create_appearance_settings(self):
        appearance_frame = ttk.LabelFrame(self.toolbar, text="外観")
        appearance_frame.pack(side="left", padx=5)
        
        # 色の選択
        ttk.Label(appearance_frame, text="色:").pack(side="left")
        self.color_var = tk.StringVar(value="black")
        colors = ["black", "red", "blue", "green", "yellow", "purple"]
        color_combo = ttk.Combobox(appearance_frame, textvariable=self.color_var, 
                                 values=colors, width=8, state="readonly")
        color_combo.pack(side="left", padx=2)
        color_combo.bind('<<ComboboxSelected>>', self.update_color)
        
        # 線の太さの選択
        ttk.Label(appearance_frame, text="線の太さ:").pack(side="left")
        self.line_width_var = tk.StringVar(value="1")
        widths = ["1", "2", "3", "4", "5"]
        width_combo = ttk.Combobox(appearance_frame, textvariable=self.line_width_var,
                                 values=widths, width=3, state="readonly")
        width_combo.pack(side="left", padx=2)
        width_combo.bind('<<ComboboxSelected>>', self.update_line_width)

        # 線スタイルの選択
        ttk.Label(appearance_frame, text="線スタイル:").pack(side="left")
        self.line_style_var = tk.StringVar(value="実線")
        styles = [
            ("実線", None),
            ("破線", (5, 5)),
            ("点線", (2, 2)),
            ("一点鎖線", (7, 4, 2, 4))
        ]
        self.style_patterns = dict(styles)
        style_combo = ttk.Combobox(appearance_frame, textvariable=self.line_style_var,
                                 values=[name for name, _ in styles], width=8, state="readonly")
        style_combo.pack(side="left", padx=2)
        style_combo.bind('<<ComboboxSelected>>', self.update_line_style)

    def create_snap_settings(self):
        snap_frame = ttk.LabelFrame(self.toolbar, text="スナップ設定")
        snap_frame.pack(side="left", padx=5)
        
        self.snap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(snap_frame, text="スナップ有効", variable=self.snap_var,
                       command=self.toggle_snap).pack(side="left")
        
        snap_types = [
            ("端点", "endpoint"),
            ("中点", "midpoint"),
            ("交点", "intersection")
        ]
        
        self.snap_type_vars = {}
        for text, snap_type in snap_types:
            var = tk.BooleanVar(value=True)
            self.snap_type_vars[snap_type] = var
            ttk.Checkbutton(snap_frame, text=text, variable=var,
                           command=lambda t=snap_type: self.toggle_snap_type(t)).pack(side="left")

    def create_display_settings(self):
        display_frame = ttk.LabelFrame(self.toolbar, text="表示設定")
        display_frame.pack(side="left", padx=5)
        
        self.dimension_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="寸法線表示", variable=self.dimension_var,
                       command=self.toggle_dimensions).pack(side="left")

    def create_undo_redo_buttons(self):
        edit_frame = ttk.Frame(self.toolbar)
        edit_frame.pack(side="right", padx=5)
        
        ttk.Button(edit_frame, text="元に戻す", command=self.undo).pack(side="left", padx=2)
        ttk.Button(edit_frame, text="やり直し", command=self.redo).pack(side="left", padx=2)

    def set_mode(self, mode):
        """描画モードを設定"""
        self.canvas.mode = mode
        mode_names = {
            "line": "線",
            "rectangle": "四角形",
            "circle": "円",
            "polygon": "多角形"
        }
        self.status_var.set(f"{mode_names.get(mode, mode)}モードに切り替えました")

    def toggle_snap(self):
        """スナップ機能のオン/オフを切り替え"""
        self.canvas.snap_enabled = not self.canvas.snap_enabled
        state = "有効" if self.canvas.snap_enabled else "無効"
        self.status_var.set(f"スナップを{state}にしました")

    def toggle_snap_type(self, snap_type):
        """特定のスナップタイプのオン/オフを切り替え"""
        self.canvas.snap_types[snap_type] = not self.canvas.snap_types[snap_type]
        state = "有効" if self.canvas.snap_types[snap_type] else "無効"
        self.status_var.set(f"{snap_type}スナップを{state}にしました")

    def toggle_dimensions(self):
        self.canvas.show_dimensions = self.dimension_var.get()
        self.canvas.redraw_all_shapes()
        state = "表示" if self.canvas.show_dimensions else "非表示"
        self.status_var.set(f"寸法線を{state}にしました")

    def undo(self):
        self.canvas.undo()
        self.status_var.set("操作を元に戻しました")

    def redo(self):
        self.canvas.redo()
        self.status_var.set("操作をやり直しました")

    def update_color(self, event=None):
        color = self.color_var.get()
        self.canvas.current_color = color
        self.status_var.set(f"色を{color}に変更しました")

    def update_line_width(self, event=None):
        """線の太さを更新"""
        width = int(self.line_width_var.get())
        self.canvas.current_width = width
        self.status_var.set(f"線の太さを{width}に変更しました")

    def update_line_style(self, event=None):
        """線スタイルを更新"""
        style_name = self.line_style_var.get()
        pattern = self.style_patterns[style_name]
        self.canvas.current_dash = pattern
        self.status_var.set(f"線スタイルを{style_name}に変更しました")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DrawingApp()
    app.run() 