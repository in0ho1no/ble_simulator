import tkinter as tk
from tkinter import ttk
from typing import Any

from . import gui_common as gc


class ModernLabelframe(ttk.Labelframe):
    """ラベルフレームのカスタムクラス

    Args:
        ttk (_type_): ttk.Labelframeを継承する
    """

    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Labelframe"
    STYLE_ID_LABEL = STYLE_ID + "." + "Label"
    FONT = (gc.COMMON_FONT, gc.COMMON_FONT_SIZE)

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master: tk.Widget | None | tk.Toplevel, **kw: Any) -> None:
        # スタイルを初期化
        self.initialize_style()
        # カスタムスタイルを利用する
        super().__init__(master, style=self.STYLE_ID, **kw)

    @classmethod
    def initialize_style(cls) -> None:
        """スタイルの初期化をクラスメソッドとして定義し、一度だけ実行"""
        if cls.style_initialized:
            return

        style = ttk.Style()
        style.layout(
            cls.STYLE_ID,
            style.layout("TLabelframe"),  # 標準レイアウトを継承
        )

        # ボタンのデフォルトスタイルの設定
        style.configure(
            cls.STYLE_ID,
            padding=2,  # 内側のパディング
            borderwidth=0,
        )
        style.configure(
            cls.STYLE_ID_LABEL,
            font=cls.FONT,
        )

        cls.style_initialized = True
