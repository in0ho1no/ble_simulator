import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Any

from . import gui_common as gc
from .parts_modern_button import ModernButton
from .parts_modern_checkbutton import ModernCheckbutton
from .parts_modern_scrollbar import ModernScrollbar
from .parts_modern_treeview import ModernTreeview


class LogViewer:
    def __init__(self, master: tk.Toplevel) -> None:
        self.master = master
        self.master.title(gc.TITLE_LOG)
        self.master.iconbitmap(gc.PATH_ICON)
        self.master.geometry(f"+{gc.POS_LOG_X}+{gc.POS_LOG_Y}")

        # ログのカウンター
        self.log_counter = 0
        # 自動スクロールの状態
        self.auto_scroll = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self) -> None:
        # メインフレームの作成
        self.main_frame = ttk.Frame(self.master)
        # Treeviewの設定
        self.tree = ModernTreeview(self.main_frame, columns=("No", "Timestamp", "Type", "Log"), show="headings")
        self.setup_tree_columns()
        # スクロールバーの追加
        self.scrollbar = ModernScrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.config(command=self.custom_scroll)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        # 部品配置
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # オプション用フレームの作成
        self.option_frame = ttk.Frame(self.master)
        # ログクリアボタン
        self.clear_button = ModernButton(self.option_frame, text="ログクリア", command=self.clear_log)
        # 自動スクロールのチェックボックス
        self.auto_scroll_check = ModernCheckbutton(self.option_frame, text="自動スクロール", variable=self.auto_scroll)
        # 部品配置
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.auto_scroll_check.pack(side=tk.RIGHT, padx=5, pady=5)

        # ウィジェットの配置
        self.main_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, pady=5)
        self.option_frame.pack(side=tk.BOTTOM, expand=False, fill=tk.X, padx=5)

    def setup_tree_columns(self) -> None:
        # 列の設定
        self.tree.heading("No", text="No.")
        self.tree.heading("Timestamp", text="タイムスタンプ")
        self.tree.heading("Type", text="種別")
        self.tree.heading("Log", text="ログ")
        self.tree.column("No", width=50, minwidth=50, anchor="e", stretch=False)
        self.tree.column("Timestamp", width=150, minwidth=150, anchor="center", stretch=False)
        self.tree.column("Type", width=100, minwidth=100, anchor="center", stretch=False)
        self.tree.column("Log", width=400)

        # 背景色の交互設定
        self.tree.tag_configure("odd", background="#E8E8E8")
        self.tree.tag_configure("even", background="#FFFFFF")

    def add_log(self, type: str, log: str) -> None:
        self.master.after(0, self._add_log, type, log)

    def _add_log(self, type: str, log: str) -> None:
        # ログ追加
        self.log_counter += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tags = ("even",) if self.log_counter % 2 == 0 else ("odd",)
        self.tree.insert("", "end", values=(self.log_counter, timestamp, type, log), tags=tags)

        # 自動スクロールが有効な場合のみ最下部にスクロール
        if self.auto_scroll.get():
            self.tree.yview_moveto(1)

    def clear_log(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.log_counter = 0
        self.add_log("情報", "ログをクリアしました。")

    def custom_scroll(self, *args: Any) -> None:
        # スクロールバーの動作をカスタマイズ
        # args[0] が 'moveto' なら、スライダーの位置を設定
        if args[0] == "moveto":
            self.tree.yview_moveto(args[1])
        else:
            # 'scroll' の場合、通常のスクロール操作 (line, page) でスクロール
            move_type = args[0]
            move_units = int(args[1])

            if move_type == "scroll":
                # スクロール量をn行にカスタマイズ
                self.tree.yview_scroll(move_units * 1, "units")
