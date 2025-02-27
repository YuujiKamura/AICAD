import tkinter as tk
import logging
from drawing_canvas import DrawingCanvas

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("キーボードショートカットテスト")
        self.geometry("800x600")
        
        # 説明ラベル
        label = tk.Label(self, text="キーボードショートカットをテスト:\nCtrl+Z: アンドゥ\nCtrl+Y: リドゥ\nDelete: 削除\nCtrl+A: 全選択")
        label.pack(pady=10)
        
        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        status = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # DrawingCanvas
        self.canvas = DrawingCanvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # フォーカスの状態表示を更新
        def update_focus_status(has_focus):
            if has_focus:
                self.status_var.set("キャンバスがフォーカスを持っています")
            else:
                self.status_var.set("キャンバスがフォーカスを失いました")
        
        # フォーカスイベントのバインド
        self.canvas.bind("<FocusIn>", lambda e: update_focus_status(True))
        self.canvas.bind("<FocusOut>", lambda e: update_focus_status(False))
        
        # ウィンドウレベルでのキーバインド - イベントをキャンバスに転送
        self.bind("<Control-z>", lambda e: self.forward_event_to_canvas(e))
        self.bind("<Control-y>", lambda e: self.forward_event_to_canvas(e))
        self.bind("<Delete>", lambda e: self.forward_event_to_canvas(e))
        self.bind("<Control-a>", lambda e: self.forward_event_to_canvas(e))
        self.bind("<Control-d>", lambda e: self.forward_event_to_canvas(e))
        
        # キャンバスにフォーカスを設定
        self.canvas.focus_set()
        logger.info("アプリケーション初期化完了")
    
    def forward_event_to_canvas(self, event):
        """ウィンドウで受け取ったイベントをキャンバスに転送"""
        logger.info(f"ウィンドウがイベントを受信: {event.keysym}")
        
        # キャンバスにフォーカスがない場合、フォーカスを設定
        if self.focus_get() != self.canvas:
            self.canvas.focus_set()
        
        # イベントをキャンバスのハンドラに転送
        self.canvas.handle_keyboard_event(event)
        return "break"  # イベント処理を停止

if __name__ == "__main__":
    app = TestApp()
    app.mainloop() 