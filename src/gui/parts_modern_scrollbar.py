from tkinter import ttk
from typing import Any, Literal

from . import gui_common as gc


class ModernScrollbar(ttk.Scrollbar):
    """スクロールバーのカスタムクラス（垂直・水平両対応）

    Args:
        ttk (_type_): ttk.Scrollbarを継承する
    """

    # スタイルの定数をクラスレベルで定義
    STYLE_ID_VERTICAL = "Modern.Vertical.TScrollbar"
    STYLE_ID_HORIZONTAL = "Modern.Horizontal.TScrollbar"
    COLOR_BG = gc.COMMON_BG
    COLOR_BG_MOUSE_OVER = gc.COMMON_BG_MOUSE_OVER

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master: ttk.Frame, orient: Literal["vertical", "horizontal"] = "vertical", **kw: Any) -> None:
        # スタイルを初期化
        self.initialize_style()
        # カスタムスタイルを利用する
        style_id = self.STYLE_ID_VERTICAL if orient == "vertical" else self.STYLE_ID_HORIZONTAL
        super().__init__(master, style=style_id, orient=orient, **kw)

    @classmethod
    def initialize_style(cls) -> None:
        """スタイルの初期化をクラスメソッドとして定義し、一度だけ実行"""
        if cls.style_initialized:
            return

        style = ttk.Style()

        # 垂直スクロールバーのスタイル
        style.layout(
            cls.STYLE_ID_VERTICAL,
            [
                (
                    "Vertical.Scrollbar.trough",
                    {
                        "children": [
                            # 上下矢印を表示させない
                            # ("Vertical.Scrollbar.uparrow", {"side": "top", "sticky": "we"}),
                            ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"}),
                            # ("Vertical.Scrollbar.downarrow", {"side": "bottom", "sticky": "we"}),
                        ],
                        "sticky": "ns",
                    },
                ),
            ],
        )

        # 水平スクロールバーのスタイル
        style.layout(
            cls.STYLE_ID_HORIZONTAL,
            [
                (
                    "Horizontal.Scrollbar.trough",
                    {
                        "children": [
                            ("Horizontal.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"}),
                        ],
                        "sticky": "ew",
                    },
                ),
            ],
        )

        # 共通のスタイル設定
        for style_id in [cls.STYLE_ID_VERTICAL, cls.STYLE_ID_HORIZONTAL]:
            style.configure(
                style_id,
                background=cls.COLOR_BG,
                bordercolor=cls.COLOR_BG,
                troughcolor="#F0F0F0",
                width=12,
            )

            style.map(
                style_id,
                background=[("active", cls.COLOR_BG_MOUSE_OVER)],
                bordercolor=[("active", cls.COLOR_BG_MOUSE_OVER)],
            )

        cls.style_initialized = True
