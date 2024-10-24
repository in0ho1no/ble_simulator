import tkinter as tk
from tkinter import ttk
from typing import Callable, List

from gui.parts_modern_button import ModernButton

from . import gui_common as gc
from .parts_input_bit import BitInputWidget
from .window_log_viewer import LogViewer


class ByteOperationWindow:
    """バイト演算を行うウィンドウクラス"""

    def __init__(self, parent: tk.Tk, on_close_callback: Callable | None = None) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Byte演算")
        self.window.resizable(False, False)
        self.window.iconbitmap(gc.PATH_ICON)
        self.on_close_callback = on_close_callback

        self._create_widgets()
        self._setup_layout()
        self._bind_events()

    def _create_widgets(self) -> None:
        """ウィジェットの作成"""
        self.entry_frame = ttk.Frame(self.window, padding=10)
        self.bit_input_field = BitInputWidget(self.entry_frame)
        self.calc_button = ModernButton(self.entry_frame, text="計算実行", command=self._on_calculate)

        self.result_frame = ttk.Frame(self.window, padding=10)
        self.value_label = ttk.Label(self.result_frame, text="16進数: ")
        self.value_entry = ttk.Entry(self.result_frame, justify=tk.CENTER, state="readonly", width=10)

    def _setup_layout(self) -> None:
        """レイアウトの設定"""
        self.entry_frame.pack(fill=tk.X)
        self.bit_input_field.pack(side=tk.TOP)
        self.calc_button.pack(side=tk.TOP)

        self.result_frame.pack(fill=tk.X)
        self.value_entry.pack(side=tk.RIGHT)
        self.value_label.pack(side=tk.RIGHT)

    def _bind_events(self) -> None:
        """イベントのバインド"""
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self) -> None:
        """ウィンドウが閉じられるときの処理"""
        if self.on_close_callback:
            self.on_close_callback(self)
        self.window.destroy()

    def _on_calculate(self) -> None:
        """計算実行時の処理

        一時的に入力許可状態にして入力済みの文字を置き換える

        """
        self.value_entry.configure(state="normal")
        self.value_entry.delete(0, tk.END)
        hex_str = self.bit_input_field.get_hex_str()
        self.value_entry.insert(0, hex_str)
        self.value_entry.configure(state="readonly")


class ByteWindowManager:
    """Byte演算ウィンドウの管理クラス"""

    MAX_WINDOWS = 100

    def __init__(self, root: tk.Tk, logger: LogViewer) -> None:
        self.root = root
        self.logger = logger
        self.windows: List[ByteOperationWindow] = []

    def create_window(self) -> None:
        """新しいByte演算ウィンドウを作成"""
        if len(self.windows) < self.MAX_WINDOWS:
            window = ByteOperationWindow(self.root, on_close_callback=self.on_window_closing)
            self.windows.append(window)
        else:
            self.logger.add_log("警告", f"Byte演算ウィンドウは最大{self.MAX_WINDOWS}個までです。")

    def on_window_closing(self, window: ByteOperationWindow) -> None:
        """ウィンドウが閉じられたときの処理"""
        self.windows.remove(window)

    def close_all_windows(self) -> None:
        """すべてのウィンドウを閉じる"""
        for window in self.windows[:]:  # リストのコピーを使用して反復
            window.window.destroy()
        self.windows.clear()
