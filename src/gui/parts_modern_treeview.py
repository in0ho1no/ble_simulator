import tkinter as tk
from tkinter import ttk
from typing import Any

from . import gui_common as gc


class ModernTreeview(ttk.Treeview):
    """ツリービューのカスタムクラス

    Args:
        ttk (_type_): ttk.Treeviewを継承する
    """

    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Treeview"

    BACKGROUND_COLOR = "#F0F0F0"
    FOREGROUND_COLOR = "#0F0F0F"
    SELECTED_COLOR = "#3366CC"
    FONT = (gc.COMMON_FONT, gc.COMMON_FONT_SIZE)
    ROW_HEIGHT = 25

    # ヘッダ部の定義
    CUSTUM_STYLE_MTVH = STYLE_ID + "." + "Heading"
    MTVH_BACKGROUND_COLOR = gc.COMMON_BG_DISABLE
    MTVH_FOREGROUND_COLOR = gc.COMMON_FG_DISABLE
    MTVH_FONT = (gc.COMMON_FONT, gc.COMMON_FONT_SIZE)
    MTVH_BORDER_WIDTH = 0

    # ツリーエリアの定義
    CUSTUM_STYLE_TREE_AREA = STYLE_ID + "." + "treearea"

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master: ttk.Frame, **kw: Any) -> None:
        # スタイルを初期化
        self.initialize_style()
        # カスタムスタイルを利用する
        super().__init__(master, style=self.STYLE_ID, **kw)

        self.text: None | tk.Text = None
        self.bind("<Double-1>", self.on_double_click)

    @classmethod
    def initialize_style(cls) -> None:
        """スタイルの初期化をクラスメソッドとして定義し、一度だけ実行"""
        if cls.style_initialized:
            return

        style = ttk.Style()
        # config設定が反映されないのであらかじめ用意されたテーマを設定しておく
        style.theme_use("alt")

        # treeviewの設定
        style.layout(
            cls.STYLE_ID,
            [(cls.CUSTUM_STYLE_TREE_AREA, {"sticky": "nswe"})],
        )
        style.configure(
            cls.STYLE_ID,
            font=cls.FONT,
            background=cls.BACKGROUND_COLOR,
            foreground=cls.FOREGROUND_COLOR,
            rowheight=cls.ROW_HEIGHT,
        )
        style.map(
            cls.STYLE_ID,
            background=[("selected", cls.SELECTED_COLOR)],
        )

        # ヘッダ部の設定
        style.configure(
            cls.CUSTUM_STYLE_MTVH,
            font=cls.MTVH_FONT,
            background=cls.MTVH_BACKGROUND_COLOR,
            foreground=cls.MTVH_FOREGROUND_COLOR,
            borderwidth=cls.MTVH_BORDER_WIDTH,
        )
        style.map(
            cls.CUSTUM_STYLE_MTVH,
            background=[("active", cls.MTVH_BACKGROUND_COLOR)],
        )

        # ツリーエリアの設定
        style.configure(
            cls.CUSTUM_STYLE_TREE_AREA,
            fieldbackground=cls.MTVH_FOREGROUND_COLOR,
        )

        # 初期設定完了
        cls.style_initialized = True

    def on_double_click(self, event: tk.Event) -> None:
        region = self.identify("region", event.x, event.y)
        if region == "cell":
            column = self.identify_column(event.x)
            item = self.identify_row(event.y)

            bbox = self.bbox(item, column)
            if bbox:
                x, y, width, height = bbox

            value = self.set(item, column)

            if self.text is None:
                self.text = tk.Text(self, wrap=tk.NONE, borderwidth=0, highlightthickness=0, font=self.FONT)
                self.text.config(state=tk.DISABLED)  # 読み取り専用に設定

            self.text.place(x=x, y=y, width=width, height=height)
            self.text.config(state=tk.NORMAL)  # 一時的に編集可能にして内容を設定
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", value)
            self.text.config(state=tk.DISABLED)  # 再び読み取り専用に設定
            self.text.focus_set()
            self.text.tag_add(tk.SEL, "1.0", tk.END)  # すべてのテキストを選択状態にする
            self.text.bind("<FocusOut>", self.on_focus_out)
            self.text.bind("<Return>", self.on_focus_out)
            self.text.bind("<Escape>", self.on_focus_out)

    def on_focus_out(self, _: tk.Event) -> None:
        if self.text is not None:
            self.text.place_forget()
            self.text = None
