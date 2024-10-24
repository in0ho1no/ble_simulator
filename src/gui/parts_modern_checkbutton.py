from tkinter import ttk
from typing import Any

from . import gui_common as gc


class ModernCheckbutton(ttk.Checkbutton):
    """チェックボックスのカスタムクラス

    Args:
        ttk (_type_): ttk.Checkbuttonを継承する
    """

    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Checkbutton"
    FONT = (gc.COMMON_FONT, gc.COMMON_FONT_SIZE)
    COLOR_BG = gc.COMMON_BG
    COLOR_BG_MOUSE_OVER = gc.COMMON_BG_MOUSE_OVER
    COLOR_FONT = gc.COMMON_FG

    COLOR_FG_DISABLE = "#FFFFFF"

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master: ttk.Frame, **kw: Any) -> None:
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
            style.layout("TCheckbutton"),  # 標準レイアウトを継承
        )

        style.configure(
            cls.STYLE_ID,
            font=cls.FONT,
            background=cls.COLOR_BG,
            foreground=cls.COLOR_FONT,
        )

        # 異なる状態でのスタイルをマッピング
        style.map(
            cls.STYLE_ID,
            background=[
                # 指定しても反映されないが、指定がないと透過されてしまう。
                ("focus", cls.COLOR_BG_MOUSE_OVER),  # フォーカス時の背景色
            ],
        )

        cls.style_initialized = True
