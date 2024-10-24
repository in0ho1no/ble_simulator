import tkinter as tk
from tkinter import ttk
from typing import Any

from .parts_modern_scrollbar import ModernScrollbar


class ScrollableFrame(ttk.Frame):
    """スクロール可能なフレームを提供するクラス。

    垂直および水平方向のスクロールバーを持つフレームを作成する。

    Attributes:
        canvas (tk.Canvas): スクロール可能な領域を提供するキャンバス。
        scrolled_frame (ttk.Frame): 実際のコンテンツを保持するフレーム。
        horizontal_scroll (bool): 水平スクロールバーを有効にするかどうか。
        vertical_scroll (bool): 垂直スクロールバーを有効にするかどうか。
    """

    def __init__(
        self,
        container: tk.Misc,
        frame: ttk.Frame | None = None,
        horizontal_scroll: bool = True,
        vertical_scroll: bool = True,
        height: int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """ScrollableFrameクラスのコンストラクタ。

        Args:
            container (tk.Misc): このフレームの親ウィジェット。
            frame: ttk.Frame | None: 既存のフレームを使用する場合に指定。デフォルトはNone。
            horizontal_scroll (bool, optional): 水平スクロールを有効にするかどうか。デフォルトはTrue。
            vertical_scroll (bool, optional): 垂直スクロールを有効にするかどうか。デフォルトはTrue。
            height (int | None, optional): ウィジェットの高さ。指定しない場合はNone。
            *args: 可変長位置引数。
            **kwargs: 可変長キーワード引数。
        """
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)

        if frame is None:
            self.scrolled_frame = ttk.Frame(self.canvas)
        else:
            self.scrolled_frame = frame

        self.horizontal_scroll = horizontal_scroll
        self.vertical_scroll = vertical_scroll

        # キャンバスの高さを設定
        if height is not None:
            self.canvas.configure(height=height)
            self.configure(height=height)

        # 垂直スクロールバーを設定
        if vertical_scroll:
            self.v_scrollbar = ModernScrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
            self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 水平スクロールバーを設定
        if horizontal_scroll:
            self.h_scrollbar = ModernScrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
            self.canvas.configure(xscrollcommand=self.h_scrollbar.set)
            self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # canvas上へframeを割り当てる
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrolled_frame, anchor=tk.NW)

        # サイズ変更イベントをバインド
        self.scrolled_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # マウスホイールイベントをバインド
        self.bind_mouse_wheel(self.scrolled_frame)
        self.bind_mouse_wheel(self.canvas)

    def on_frame_configure(self, _: tk.Event) -> None:
        """フレームサイズ変更イベントのハンドラ

        スクロール領域をフレームの全体に合わせて更新する

        Args:
            _ (tk.Event): 読み捨て
        """
        # canvas上のすべてのwidgetを含む矩形領域をスクロール可能領域として設定する
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event: tk.Event) -> None:
        """キャンバスサイズ変更イベントのハンドラ

        スクロールされるフレームの幅と高さを更新する

        Args:
            event (tk.Event): 設定変更イベント
        """
        min_width: int = self.scrolled_frame.winfo_reqwidth()
        min_height: int = self.scrolled_frame.winfo_reqheight()
        if self.horizontal_scroll:
            self.canvas.itemconfig(self.canvas_frame, width=max(min_width, event.width))
        if self.vertical_scroll:
            self.canvas.itemconfig(self.canvas_frame, height=max(min_height, event.height))

    def bind_mouse_wheel(self, widget: tk.Widget | ttk.Widget) -> None:
        """指定されたウィジェットとその子ウィジェットにマウスホイールイベントを割り当てる

        Args:
            widget (tk.Widget | ttk.Widget): マウスホイールイベントをバインドするウィジェット

        Raises:
            TypeError: 指定されたウィジェットが tk.Widget または ttk.Widget のインスタンスでない場合に例外を発生させる
        """
        if not isinstance(widget, (tk.Widget, ttk.Widget)):
            raise TypeError(f"Expected tk.Widget or ttk.Widget, got {type(widget)}")

        widget.bind("<MouseWheel>", self.on_mousewheel)
        widget.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)

        if hasattr(widget, "winfo_children"):
            for child in widget.winfo_children():
                self.bind_mouse_wheel(child)

    def on_mousewheel(self, event: tk.Event) -> None:
        """マウスホイールイベントのハンドラ(ホイールのみ)

        垂直方向のスクロールを処理する

        Args:
            event (tk.Event): マウスホイールイベント。
        """
        if self.vertical_scroll:
            # ホイールの操作量と方向を変換してcanvasスクロールを行う
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(self, event: tk.Event) -> None:
        """マウスホイールイベントのハンドラ(Shift+ホイール)

        水平方向のスクロールを処理する

        Args:
            event (tk.Event): マウスホイールイベント。
        """
        if self.horizontal_scroll:
            # ホイールの操作量と方向を変換してcanvasスクロールを行う
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def force_update(self) -> None:
        """強制的な更新処理"""
        self.update_idletasks()
        self.scrolled_frame.event_generate("<Configure>")
        self.canvas.event_generate("<Configure>")
